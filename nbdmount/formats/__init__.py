"""
镜像格式工厂 - 体现开闭原则（对扩展开放，对修改关闭）
"""
from typing import List, Type, Optional
from .base import ImageFormat
from .qcow2 import QCOW2Image
from .raw import RAWImage
from ..exceptions.errors import ImageFormatError


# 注册支持的格式（按优先级排序）
SUPPORTED_FORMATS: List[Type[ImageFormat]] = [
    QCOW2Image,
    RAWImage,
    # 可在此添加更多格式：VMDKImage, VDIImage 等
]


def detect_image_format(image_path: str, format_hint: Optional[str] = None) -> ImageFormat:
    """
    自动检测或根据提示创建镜像格式对象
    
    :param image_path: 镜像文件路径
    :param format_hint: 可选的格式提示（如 "qcow2"）
    :return: ImageFormat 实例
    :raises ImageFormatError: 无法识别格式时
    """
    # 1. 如果有格式提示，优先使用
    if format_hint:
        format_hint = format_hint.lower()
        for fmt_cls in SUPPORTED_FORMATS:
            if format_hint in fmt_cls.FORMAT_NAME.lower():
                try:
                    img = fmt_cls(image_path)
                    if img.validate():
                        return img
                except Exception:
                    continue
        raise ImageFormatError(f"指定的格式 '{format_hint}' 不受支持或验证失败")

    # 2. 按优先级自动检测
    for fmt_cls in sorted(SUPPORTED_FORMATS, key=lambda x: x.PRIORITY):
        try:
            if fmt_cls.detect(image_path):
                img = fmt_cls(image_path)
                if img.validate():
                    return img
        except Exception as e:
            logger.debug(f"{fmt_cls.__name__} 检测失败: {e}")
            continue

    raise ImageFormatError(
        f"无法识别镜像格式: {image_path}\n"
        f"支持的格式: {', '.join(f.FORMAT_NAME for f in SUPPORTED_FORMATS)}"
    )