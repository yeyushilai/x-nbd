"""
NBD 设备抽象层 - 体现资源封装
"""
import logging
from contextlib import contextmanager
from typing import Generator, Optional, List
from ..formats import ImageFormat
from ..utils.command import run_command
from ..utils.devices import find_unused_nbd_device, get_partitions
from ..exceptions.errors import DeviceError


logger = logging.getLogger(__name__)


class NBDDevice:
    """
    NBD 设备资源封装
    
    设计亮点:
    - 资源生命周期管理
    - 上下文管理器自动清理
    - 状态跟踪
    """
    
    def __init__(self, image: ImageFormat):
        self.image = image
        self.device_path: Optional[str] = None
        self.is_connected = False
        self.partitions: List[str] = []
    
    @contextmanager
    def connect(self, read_only: bool = True) -> Generator['NBDDevice', None, None]:
        """
        连接 NBD 设备的上下文管理器
        
        :param read_only: 是否以只读模式连接
        :yield: 已连接的 NBDDevice 实例
        """
        if self.is_connected:
            raise DeviceError("设备已连接", device=self.device_path)
        
        try:
            self._connect(read_only)
            yield self
        finally:
            self.disconnect()
    
    def _connect(self, read_only: bool) -> None:
        """实际连接逻辑"""
        self.device_path = find_unused_nbd_device()
        logger.info(f"将镜像 '{self.image.image_path.name}' 连接到 {self.device_path}")
        
        cmd = [
            "qemu-nbd",
            "--connect", self.device_path,
            "--format", self.image.get_qemu_format_flag(),
        ]
        if read_only:
            cmd.append("--read-only")
        cmd.append(str(self.image.image_path))
        
        run_command(cmd, timeout=30)
        self.is_connected = True
        
        # 通知内核重读分区表
        try:
            run_command(["partprobe", self.device_path], timeout=10)
            # 等待分区设备出现（最多2秒）
            import time
            for _ in range(4):
                self.partitions = get_partitions(self.device_path)
                if self.partitions:
                    break
                time.sleep(0.5)
        except Exception as e:
            logger.warning(f"分区表重读失败（可能无分区表）: {e}")
            self.partitions = []
    
    def disconnect(self) -> None:
        """安全断开 NBD 连接"""
        if not self.is_connected or not self.device_path:
            return
        
        try:
            logger.info(f"断开 NBD 设备: {self.device_path}")
            run_command(["qemu-nbd", "--disconnect", self.device_path], timeout=10)
        except Exception as e:
            # 断开失败可能因为设备已自动断开，仅记录警告
            logger.warning(f"断开 {self.device_path} 时出错（可能已断开）: {e}")
        finally:
            self.is_connected = False
            self.device_path = None
            self.partitions = []
    
    def __repr__(self) -> str:
        status = "connected" if self.is_connected else "disconnected"
        return f"NBDDevice(path={self.device_path}, status={status}, image={self.image.image_path.name})"