"""
NBD 挂载核心管理器 - 高层业务逻辑编排
"""
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, Optional
from ..formats import detect_image_format, ImageFormat
from ..core.device import NBDDevice
from ..core.mounter import MountManager
from ..exceptions.errors import PermissionError
from ..utils.command import run_command


logger = logging.getLogger(__name__)


class NBDMountTool:
    """
    NBD 挂载工具主类
    
    设计亮点:
    - 分层架构：格式检测 -> 设备连接 -> 分区挂载
    - 资源自动管理
    - 可扩展的挂载策略
    """
    
    def __init__(
        self, 
        image_path: str, 
        image_format: Optional[str] = None,
        read_only: bool = True
    ):
        self.image_path = Path(image_path).resolve()
        self.read_only = read_only
        
        # 1. 检测镜像格式
        self.image: ImageFormat = detect_image_format(str(self.image_path), image_format)
        logger.info(f"✓ 镜像格式识别: {self.image.FORMAT_NAME} ({self.image_path.name})")
        
        # 2. 创建设备管理器
        self.device = NBDDevice(self.image)
        self.mounter = MountManager()
    
    def mount_image(
        self, 
        mount_dir: Optional[str] = None,
        mount_options: Optional[list] = None
    ) -> Dict[str, str]:
        """
        完整挂载流程：连接设备 -> 识别分区 -> 挂载分区
        
        :param mount_dir: 挂载基目录（默认 /mnt/nbd-<镜像名>）
        :param mount_options: 挂载选项列表
        :return: {分区: 挂载点} 映射
        """
        # 确定挂载目录
        if not mount_dir:
            safe_name = self.image_path.stem.replace(" ", "_").lower()
            mount_dir = f"/mnt/nbd-{safe_name}"
        
        base_dir = Path(mount_dir)
        
        # 执行完整挂载流程
        with self.device.connect(read_only=self.read_only):
            if not self.device.partitions:
                logger.warning("⚠ 未检测到分区，尝试直接挂载整个设备...")
                # 直接挂载整个设备（无分区表场景）
                with self.mounter:
                    mp = self.mounter.mount_partition(
                        self.device.device_path,
                        base_dir / "whole_disk",
                        mount_options or ["ro", "noload"]
                    )
                    return {self.device.device_path: str(mp.mount_path)}
            
            # 挂载所有分区
            with self.mounter:
                mounts = self.mounter.mount_all_partitions(
                    self.device.partitions,
                    base_dir,
                    mount_options or ["ro", "noload"]
                )
                # 返回简化映射（供外部使用）
                return {part: str(mp.mount_path) for part, mp in mounts.items()}
    
    def list_partitions(self) -> list:
        """列出镜像中的分区"""
        with self.device.connect(read_only=True):
            return self.device.partitions
    
    def get_image_info(self) -> dict:
        """获取镜像详细信息"""
        size_gb = self.image_path.stat().st_size / (1024 ** 3)
        return {
            "path": str(self.image_path),
            "format": self.image.FORMAT_NAME,
            "size_gb": round(size_gb, 2),
            "size_bytes": self.image_path.stat().st_size,
            "read_only": self.read_only
        }
    
    @staticmethod
    def check_prerequisites() -> None:
        """检查运行前提条件"""
        # 检查 root 权限
        if os.geteuid() != 0:
            raise PermissionError("需要 root 权限运行此工具")
        
        # 检查必要命令
        required_cmds = ["qemu-nbd", "qemu-img", "partprobe", "mount", "umount", "mountpoint"]
        missing = [cmd for cmd in required_cmds if not shutil.which(cmd)]
        
        if missing:
            raise RuntimeError(
                f"缺少必要命令: {', '.join(missing)}\n"
                "请安装: sudo apt install qemu-utils util-linux"
            )
        
        # 检查 nbd 模块
        if not Path("/sys/module/nbd").exists():
            logger.warning(
                "NBD 内核模块未加载，尝试自动加载...\n"
                "如失败请手动执行: sudo modprobe nbd max_part=16"
            )
            try:
                run_command(["modprobe", "nbd", "max_part=16"], timeout=5)
            except Exception as e:
                logger.warning(f"自动加载 nbd 模块失败: {e}")