"""
分区挂载管理 - 体现策略模式
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional
from ..utils.command import run_command
from ..exceptions.errors import MountError


logger = logging.getLogger(__name__)


class MountPoint:
    """挂载点封装"""
    def __init__(self, partition: str, mount_path: Path):
        self.partition = partition
        self.mount_path = mount_path.resolve()
        self.is_mounted = False
    
    def mount(self, options: Optional[List[str]] = None) -> None:
        """挂载分区"""
        if self.is_mounted:
            logger.warning(f"{self.mount_path} 已挂载，跳过")
            return
        
        # 创建挂载目录
        self.mount_path.mkdir(parents=True, exist_ok=True)
        
        # 构建挂载选项
        mount_opts = options or ["ro", "noload"]  # noload 避免 ext4 日志重放
        
        logger.info(f"挂载 {self.partition} 到 {self.mount_path} (options: {','.join(mount_opts)})")
        try:
            run_command(
                ["mount"] + 
                (["-o", ",".join(mount_opts)] if mount_opts else []) +
                [self.partition, str(self.mount_path)],
                timeout=15
            )
            self.is_mounted = True
            logger.info(f"✓ 挂载成功: {self.partition} -> {self.mount_path}")
        except Exception as e:
            raise MountError(f"挂载失败: {e}", device=self.partition)
    
    def umount(self, force: bool = False) -> None:
        """卸载分区"""
        if not self.is_mounted and not self._is_mounted_system():
            logger.warning(f"{self.mount_path} 未挂载")
            return
        
        logger.info(f"卸载 {self.mount_path}")
        try:
            cmd = ["umount"]
            if force:
                cmd.append("-f")
            cmd.append(str(self.mount_path))
            run_command(cmd, timeout=10)
            self.is_mounted = False
            logger.info(f"✓ 卸载成功: {self.mount_path}")
        except Exception as e:
            raise MountError(f"卸载失败: {e}", device=str(self.mount_path))
    
    def _is_mounted_system(self) -> bool:
        """系统级检查是否挂载"""
        try:
            result = run_command(["mountpoint", "-q", str(self.mount_path)], 
                               capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def __repr__(self) -> str:
        status = "mounted" if self.is_mounted else "unmounted"
        return f"MountPoint(partition='{self.partition}', path='{self.mount_path}', status={status})"


class MountManager:
    """
    挂载管理器 - 管理多个挂载点
    
    设计亮点:
    - 跟踪所有挂载点状态
    - 安全批量操作
    - 自动清理
    """
    
    def __init__(self):
        self.mount_points: Dict[str, MountPoint] = {}  # partition -> MountPoint
    
    def mount_partition(
        self, 
        partition: str, 
        mount_path: Path,
        options: Optional[List[str]] = None
    ) -> MountPoint:
        """
        挂载单个分区
        
        :return: MountPoint 实例
        """
        mp = MountPoint(partition, mount_path)
        mp.mount(options)
        self.mount_points[partition] = mp
        return mp
    
    def mount_all_partitions(
        self,
        partitions: List[str],
        base_mount_dir: Path,
        options: Optional[List[str]] = None
    ) -> Dict[str, MountPoint]:
        """
        挂载所有分区到基目录下的子目录
        
        :return: {partition: MountPoint} 映射
        """
        results = {}
        for part in partitions:
            # 从分区名提取编号 (如 /dev/nbd0p1 -> 1)
            match = re.search(r"p(\d+)$", part)
            part_num = match.group(1) if match else part.replace("/dev/", "")
            
            mount_path = base_mount_dir / f"part{part_num}"
            try:
                mp = self.mount_partition(part, mount_path, options)
                results[part] = mp
                logger.info(f"✓ 分区 {part} 挂载到 {mount_path}")
            except Exception as e:
                logger.error(f"✗ 挂载 {part} 失败: {e}")
                continue
        return results
    
    def umount_all(self, force: bool = False) -> None:
        """卸载所有管理的挂载点"""
        # 反向卸载（先挂载的后卸载）
        for partition in reversed(list(self.mount_points.keys())):
            try:
                self.mount_points[partition].umount(force)
                del self.mount_points[partition]
            except Exception as e:
                logger.error(f"卸载 {partition} 失败: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文退出时自动清理"""
        if self.mount_points:
            logger.info(f"上下文退出，清理 {len(self.mount_points)} 个挂载点...")
            self.umount_all()
        return False  # 不抑制异常