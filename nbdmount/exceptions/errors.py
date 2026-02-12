"""
NBD 操作异常体系 - 体现分层异常设计
"""
from typing import Optional


class NBDException(Exception):
    """NBD 操作异常基类"""
    def __init__(self, message: str, device: Optional[str] = None):
        self.device = device
        super().__init__(f"[{device or 'NBD'}] {message}" if device else message)


class DeviceError(NBDException):
    """设备相关错误"""
    pass


class DeviceBusyError(DeviceError):
    """设备忙异常"""
    pass


class DeviceNotFoundError(DeviceError):
    """设备未找到"""
    pass


class ImageError(NBDException):
    """镜像相关错误"""
    pass


class ImageFormatError(ImageError):
    """镜像格式错误"""
    pass


class ImageNotFoundError(ImageError):
    """镜像文件不存在"""
    pass


class MountError(NBDException):
    """挂载相关错误"""
    pass


class PermissionError(NBDException):
    """权限错误"""
    pass