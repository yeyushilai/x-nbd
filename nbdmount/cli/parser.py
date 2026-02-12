"""
命令行接口 - 专业级参数处理
"""
import argparse
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(debug: bool = False) -> None:
    """配置日志系统"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S"
    )
    # 第三方库日志降级
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def parse_arguments(argv: Optional[list] = None) -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="NBD 磁盘镜像挂载管理工具",
        epilog="示例:\n"
               "  nbdmount disk.qcow2 mount\n"
               "  nbdmount disk.raw list --format raw\n"
               "  nbdmount disk.qcow2 mount --mount-dir /mnt/forensics",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 位置参数
    parser.add_argument("image", help="虚拟机镜像文件路径 (qcow2/raw/vmdk 等)")
    parser.add_argument(
        "action", 
        choices=["mount", "list", "info", "check"],
        help="操作类型: mount=挂载分区, list=列出分区, info=镜像信息, check=环境检查"
    )
    
    # 可选参数
    parser.add_argument(
        "--mount-dir", 
        metavar="DIR",
        help="挂载基目录 (默认: /mnt/nbd-<镜像名>)"
    )
    parser.add_argument(
        "--format", 
        choices=["qcow2", "raw"],
        help="指定镜像格式（自动检测失败时使用）"
    )
    parser.add_argument(
        "--rw", 
        action="store_true",
        help="以读写模式挂载（⚠️ 谨慎使用，可能损坏镜像）"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="启用调试日志"
    )
    parser.add_argument(
        "--version", 
        action="version",
        version="nbdmount 1.0.0"
    )
    
    args = parser.parse_args(argv)
    
    # 验证镜像路径
    image_path = Path(args.image)
    if not image_path.exists():
        parser.error(f"镜像文件不存在: {args.image}")
    if not image_path.is_file():
        parser.error(f"路径不是常规文件: {args.image}")
    
    return args