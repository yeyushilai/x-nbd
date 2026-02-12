"""
QCOW2 镜像格式实现
"""
import re
from typing import ClassVar
from .base import ImageFormat
from ..utils.command import run_command


class QCOW2Image(ImageFormat):
    """QCOW2 镜像格式"""
    FORMAT_NAME: ClassVar[str] = "qcow2"
    PRIORITY: ClassVar[int] = 10  # 高优先级

    def get_qemu_format_flag(self) -> str:
        return "qcow2"

    def validate(self) -> bool:
        try:
            result = run_command(
                ["qemu-img", "info", str(self.image_path)],
                capture_output=True,
                timeout=10
            )
            return bool(re.search(r"file format:\s*qcow2", result.stdout, re.IGNORECASE))
        except Exception as e:
            logger.warning(f"QCOW2 验证失败: {e}")
            return False

    @classmethod
    def detect(cls, image_path: str) -> bool:
        try:
            # 快速检测：检查文件魔数
            with open(image_path, 'rb') as f:
                magic = f.read(4)
                return magic == b'QFI\xfb'  # QCOW2 魔数
        except Exception:
            return False