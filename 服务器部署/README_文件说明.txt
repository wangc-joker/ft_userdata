文件说明

1) Vultr_Freqtrade_VPS_购买与部署指南.docx
   购买 Vultr、部署 Ubuntu、安装 Docker、迁移本地 Windows 11 Docker 版 Freqtrade、启动实盘机器人的完整说明。

2) deploy_freqtrade_vultr.sh
   在 Vultr 的 Ubuntu 22.04/24.04 服务器上执行的部署脚本。
   作用：安装 Docker、创建 /opt/freqtrade、生成 compose.yaml、导入你本地的 user_data、启动机器人。

3) upload_user_data_to_vultr.ps1
   在你的 Windows 11 本地 PowerShell 里执行的上传脚本。
   作用：把本地 user_data 目录打包并通过 scp 上传到服务器。

建议顺序
A. 先看 DOCX 文档
B. 购买服务器并拿到 IP
C. 本地执行 PowerShell 上传脚本
D. 服务器执行 deploy_freqtrade_vultr.sh
