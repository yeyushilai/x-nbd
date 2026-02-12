"""
NBD 设备管理工具
"""
import os
import re
import glob
from pathlib import Path
from typing import List, Optional
from ..exceptions.errors import DeviceNotFoundError, DeviceBusyError


def find_unused_nbd_device(max_devices: int = 32) -> str:
    """
    查找未使用的 NBD 设备
    
    :param max_devices: 最大检查设备数量
    :return: 空闲设备路径，如 "/dev/nbd0"
    :raises DeviceNotFoundError: 无可用设备
    """
    for i in range(max_devices):
        dev_path = f"/dev/nbd{i}"
        size_path = f"/sys/block/nbd{i}/size"
        
        # 检查设备节点是否存在
        if not os.path.exists(dev_path):
            continue
            
        # 检查 sysfs 中的大小属性（0 表示未连接）
        try:
            if os.path.exists(size_path):
                with open(size_path) as f:
                    size_sectors = int(f.read().strip())
                    if size_sectors == 0:
                        logger.debug(f"找到空闲 NBD 设备: {dev_path}")
                        return dev_path
        except (ValueError, OSError) as e:
            logger.warning(f"检查 {dev_path} 状态时出错: {e}")
            continue
    
    raise DeviceNotFoundError(
        f"未找到空闲 NBD 设备（已检查 nbd0-nbd{max_devices-1}）\n"
        "可能原因:\n"
        "  1. 未加载 nbd 内核模块: sudo modprobe nbd max_part=16\n"
        "  2. 所有设备已被占用"
    )


def get_partitions(nbd_device: str) -> List[str]:
    """
    获取 NBD 设备上的分区列表
    
    :param nbd_device: NBD 设备路径，如 "/dev/nbd0"
    :return: 分区设备列表，如 ["/dev/nbd0p1", "/dev/nbd0p2"]
    """
    base_name = os.path.basename(nbd_device)
    partitions = []
    
    # 方法1: 通过 /dev 目录查找
    for entry in glob.glob(f"/dev/{base_name}p*"):
        if re.match(rf"^{base_name}p\d+$", os.path.basename(entry)):
            partitions.append(entry)
    
    # 方法2: 通过 sysfs 验证（更可靠）
    sysfs_partitions = []
    sysfs_path = f"/sys/block/{base_name}"
    if os.path.exists(sysfs_path):
        for subdir in os.listdir(sysfs_path):
            if re.match(rf"^{base_name}p\d+$", subdir):
                dev_path = f"/dev/{subdir}"
                if os.path.exists(dev_path):
                    sysfs_partitions.append(dev_path)
    
    # 合并并去重
    partitions = sorted(set(partitions + sysfs_partitions), 
                       key=lambda x: int(re.search(r"\d+$", x).group()))
    
    logger.info(f"在 {nbd_device} 上检测到 {len(partitions)} 个分区: {partitions}")
    return partitions


def is_device_mounted(device: str) -> bool:
    """
    检查设备或挂载点是否已挂载
    
    :param device: 设备路径或挂载点
    :return: True 如果已挂载
    """
    try:
        with open("/proc/mounts") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2 and (parts[0] == device or parts[1] == device):
                    return True
        return False
    except Exception as e:
        logger.warning(f"检查挂载状态失败: {e}")
        return False