#!/usr/bin/env bash
set -Eeuo pipefail

# 用法示例：
#   sudo bash deploy_freqtrade_vultr.sh \
#     --bot-name ftbot \
#     --strategy-class MyStrategy \
#     --config-file config.json
#
# 如果你已经把本地的 user_data 打包上传到服务器：
#   sudo bash deploy_freqtrade_vultr.sh \
#     --bot-name ftbot \
#     --strategy-class MyStrategy \
#     --config-file config.json \
#     --import-tar /root/user_data.tar.gz

BOT_NAME="ftbot"
INSTALL_ROOT="/opt/freqtrade"
USER_DATA_DIR="$INSTALL_ROOT/user_data"
COMPOSE_FILE="$INSTALL_ROOT/compose.yaml"
STRATEGY_CLASS="SampleStrategy"
CONFIG_FILE="config.json"
IMPORT_TAR=""
TIMEZONE="Asia/Shanghai"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --bot-name) BOT_NAME="$2"; shift 2 ;;
    --install-root) INSTALL_ROOT="$2"; shift 2 ;;
    --strategy-class) STRATEGY_CLASS="$2"; shift 2 ;;
    --config-file) CONFIG_FILE="$2"; shift 2 ;;
    --import-tar) IMPORT_TAR="$2"; shift 2 ;;
    --timezone) TIMEZONE="$2"; shift 2 ;;
    -h|--help)
      sed -n '1,60p' "$0"
      exit 0
      ;;
    *)
      echo "未知参数: $1"
      exit 1
      ;;
  esac
done

USER_DATA_DIR="$INSTALL_ROOT/user_data"
COMPOSE_FILE="$INSTALL_ROOT/compose.yaml"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "缺少命令: $1"; exit 1; }
}

if [[ $EUID -ne 0 ]]; then
  echo "请用 root 或 sudo 运行此脚本。"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

echo "==> 更新系统并安装基础依赖"
apt-get update -y
apt-get upgrade -y
apt-get install -y ca-certificates curl gnupg lsb-release ufw git unzip tar jq

echo "==> 设置时区为 $TIMEZONE"
timedatectl set-timezone "$TIMEZONE" || true

if ! command -v docker >/dev/null 2>&1; then
  echo "==> 安装 Docker 官方仓库"
  install -m 0755 -d /etc/apt/keyrings
  if [[ ! -f /etc/apt/keyrings/docker.asc ]]; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
  fi

  ARCH="$(dpkg --print-architecture)"
  RELEASE_CODENAME="$(. /etc/os-release && echo "$VERSION_CODENAME")"
  echo \
    "deb [arch=${ARCH} signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    ${RELEASE_CODENAME} stable" | tee /etc/apt/sources.list.d/docker.list >/dev/null

  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
else
  echo "==> Docker 已安装，跳过"
fi

systemctl enable docker
systemctl restart docker

echo "==> 创建目录"
mkdir -p "$USER_DATA_DIR"/{backtest_results,data,hyperopts,logs,notebooks,plot,strategies}
mkdir -p "$INSTALL_ROOT"

echo "==> 配置防火墙"
ufw allow OpenSSH || true
ufw allow 8080/tcp || true
ufw --force enable || true

echo "==> 写入 compose.yaml"
cat > "$COMPOSE_FILE" <<EOF
services:
  freqtrade:
    image: freqtradeorg/freqtrade:stable
    container_name: ${BOT_NAME}
    restart: unless-stopped
    tty: true
    stdin_open: true
    environment:
      - TZ=${TIMEZONE}
    volumes:
      - ${USER_DATA_DIR}:/freqtrade/user_data
    ports:
      - "127.0.0.1:8080:8080"
    command: >
      trade
      --logfile /freqtrade/user_data/logs/freqtrade.log
      --db-url sqlite:////freqtrade/user_data/tradesv3.sqlite
      --config /freqtrade/user_data/${CONFIG_FILE}
      --strategy ${STRATEGY_CLASS}
EOF

echo "==> 拉取镜像"
docker compose -f "$COMPOSE_FILE" pull

echo "==> 初始化 user_data 目录（已存在则忽略报错）"
docker compose -f "$COMPOSE_FILE" run --rm freqtrade create-userdir --userdir /freqtrade/user_data || true

if [[ -n "$IMPORT_TAR" ]]; then
  if [[ ! -f "$IMPORT_TAR" ]]; then
    echo "指定的导入包不存在: $IMPORT_TAR"
    exit 1
  fi
  echo "==> 导入本地迁移包: $IMPORT_TAR"
  tar -xzf "$IMPORT_TAR" -C "$USER_DATA_DIR"
fi

if [[ ! -f "$USER_DATA_DIR/$CONFIG_FILE" ]]; then
  echo
  echo "!!! 还没有检测到配置文件: $USER_DATA_DIR/$CONFIG_FILE"
  echo "请把你的 config.json 上传到上面这个路径后，再执行："
  echo "docker compose -f $COMPOSE_FILE up -d"
  echo
else
  echo "==> 检查策略文件目录"
  ls -lah "$USER_DATA_DIR/strategies" || true

  echo "==> 启动机器人"
  docker compose -f "$COMPOSE_FILE" up -d

  echo
  echo "启动完成。常用命令："
  echo "查看状态: docker compose -f $COMPOSE_FILE ps"
  echo "查看日志: docker compose -f $COMPOSE_FILE logs -f --tail=200"
  echo "停止服务: docker compose -f $COMPOSE_FILE down"
  echo "重启服务: docker compose -f $COMPOSE_FILE restart"
fi

echo
echo "部署目录: $INSTALL_ROOT"
echo "配置文件: $USER_DATA_DIR/$CONFIG_FILE"
echo "策略目录: $USER_DATA_DIR/strategies"
echo "数据库文件: $USER_DATA_DIR/tradesv3.sqlite"
