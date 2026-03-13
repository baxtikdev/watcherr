from watcherr.config import WatcherrConfig, configure
from watcherr.sender import send_alert, send_info, send_photo, send_warning

__all__ = [
    "WatcherrConfig",
    "configure",
    "send_alert",
    "send_warning",
    "send_info",
    "send_photo",
]
