"""Shared custom-exit result formatting helpers."""


def format_exit_reason(exit_result, enter_tag):
  sell, signal_name = exit_result
  if sell and (signal_name is not None):
    return f"{signal_name} ( {enter_tag})"
  return None
