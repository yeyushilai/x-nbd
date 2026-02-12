"""
镜像格式抽象层 - 体现多态设计
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar


class ImageFormat(ABC):
    """
    抽象镜像格式接口
    
    设计亮点:
    - 通过类属性标识格式名称
    - 统一验证接口
    - 工厂方法支持自动检测
    """
    FORMAT_NAME: ClassVar[str] = "unknown"
    PRIORITY: ClassVar[int] = 100  # 优先级，数值越小优先级越高

    def __init__(self, image_path: str):
        self.image_path = Path(image_path).resolve()
        self._validate_path()

    def _validate_path(self) -> None:
        """验证镜像路径有效性"""
        if not self.image_path.exists():
            raise FileNotFoundError(f"镜像文件不存在: {self.image_path}")
        if not self.image_path.is_file():
            raise ValueError(f"路径不是常规文件: {self.image_path}")
        if not os.access(self.image_path, os.R_OK):
            raise PermissionError(f"无权读取镜像文件: {self.image_path}")

    @abstractmethod
    def get_qemu_format_flag(self) -> str:
        """返回 qemu-nbd 对应的 -f 参数值"""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """验证镜像格式有效性"""
        pass

    @classmethod
    @abstractmethod
    def detect(cls, image_path: str) -> bool:
        """检测文件是否为此格式"""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path='{self.image_path}', format='{self.FORMAT_NAME}')"