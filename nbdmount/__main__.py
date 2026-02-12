"""
命令行主入口 - 体现专业工具设计
"""
import sys
import logging
import shutil
from pathlib import Path
from .cli.parser import parse_arguments, setup_logging
from .core.manager import NBDMountTool
from .exceptions.errors import (
    NBDException, PermissionError, ImageFormatError, 
    DeviceNotFoundError, MountError
)


logger = logging.getLogger(__name__)


def action_mount(tool: NBDMountTool, args) -> int:
    """挂载动作"""
    logger.info("开始挂载镜像分区...")
    try:
        mounts = tool.mount_image(
            mount_dir=args.mount_dir,
            mount_options=None if args.rw else ["ro", "noload"]
        )
        
        if mounts:
            logger.info("\n✓ 挂载成功:")
            for part, mp in mounts.items():
                logger.info(f"  {part:20s} -> {mp}")
            logger.info("\n💡 提示: 使用 'nbdmount <image> umount' 或重启系统来清理挂载")
            return 0
        else:
            logger.error("✗ 未挂载任何分区")
            return 1
    except MountError as e:
        logger.error(f"挂载失败: {e}")
        return 2


def action_list(tool: NBDMountTool, args) -> int:
    """列出分区动作"""
    logger.info("检测镜像分区...")
    partitions = tool.list_partitions()
    
    if partitions:
        logger.info(f"\n✓ 在镜像中找到 {len(partitions)} 个分区:")
        for i, part in enumerate(partitions, 1):
            logger.info(f"  {i}. {part}")
        return 0
    else:
        logger.warning("⚠ 未检测到分区（可能是无分区表的裸文件系统）")
        return 0


def action_info(tool: NBDMountTool, args) -> int:
    """镜像信息动作"""
    info = tool.get_image_info()
    logger.info("\n镜像信息:")
    logger.info(f"  路径:     {info['path']}")
    logger.info(f"  格式:     {info['format']}")
    logger.info(f"  大小:     {info['size_gb']:.2f} GB ({info['size_bytes']} bytes)")
    logger.info(f"  挂载模式: {'读写' if not info['read_only'] else '只读'}")
    return 0


def action_check(tool: NBDMountTool, args) -> int:
    """环境检查动作"""
    logger.info("检查运行环境...")
    try:
        NBDMountTool.check_prerequisites()
        logger.info("✓ 所有前提条件满足")
        return 0
    except Exception as e:
        logger.error(f"✗ 环境检查失败: {e}")
        return 1


def main(argv: list = None) -> int:
    """主函数"""
    args = parse_arguments(argv)
    setup_logging(args.debug)
    
    # 环境检查
    try:
        NBDMountTool.check_prerequisites()
    except Exception as e:
        logger.error(f"环境检查失败: {e}")
        return 1
    
    # 创建工具实例
    try:
        tool = NBDMountTool(
            image_path=args.image,
            image_format=args.format,
            read_only=not args.rw
        )
    except ImageFormatError as e:
        logger.error(f"镜像格式错误: {e}")
        logger.info("提示: 使用 --format 参数指定格式，如 --format qcow2")
        return 1
    except Exception as e:
        logger.exception(f"初始化失败: {e}")
        return 1
    
    # 执行动作
    action_map = {
        "mount": action_mount,
        "list": action_list,
        "info": action_info,
        "check": action_check,
    }
    
    try:
        return action_map[args.action](tool, args)
    except KeyboardInterrupt:
        logger.warning("\n操作被用户中断")
        return 130
    except NBDException as e:
        logger.error(f"操作失败: {e}")
        return 2
    except Exception as e:
        logger.exception(f"未预期错误: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())