"""
RAW 镜像格式实现
"""
from typing import ClassVar
from .base import ImageFormat
from ..utils.command import run_command
import re


class RAWImage(ImageFormat):
    """RAW 镜像格式"""
    FORMAT_NAME: ClassVar[str] = "raw"
    PRIORITY: ClassVar[int] = 50  # 中等优先级

    def get_qemu_format_flag(self) -> str:
        return "raw"

    def validate(self) -> bool:
        # RAW 格式验证：检查是否为常规文件且大小合理
        stat = self.image_path.stat()
        return stat.st_size > 0 and stat.st_size % 512 == 0  # 块设备对齐

    @classmethod
    def detect(cls, image_path: str) -> bool:
        # RAW 无特定魔数，通过排除法检测
        try:
            # 排除已知格式
            with open(image_path, 'rb') as f:
                header = f.read(16)
                # 排除 QCOW2 魔数
                if header.startswith(b'QFI\xfb'):
                    return False
                # 排除 VMDK, VDI 等其他格式（可扩展）
            return True
        except Exception:
            return False