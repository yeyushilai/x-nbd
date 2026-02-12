"""
NBD 磁盘镜像挂载工具包
提供将虚拟机镜像映射为本地块设备并安全挂载的能力
"""

__version__ = "1.0.0"
__author__ = "NBD Mount Team"

# 公共 API 导出
from .core.manager import NBDMountTool
from .exceptions.errors import (
    NBDException, DeviceError, ImageError, MountError, 
    DeviceBusyError, ImageFormatError, PermissionError
)

__all__ = [
    "NBDMountTool",
    "NBDException",
    "DeviceError",
    "ImageError",
    "MountError",
    "DeviceBusyError",
    "ImageFormatError",
    "PermissionError",
]