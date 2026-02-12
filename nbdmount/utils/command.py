"""
安全的命令执行封装 - 体现防御式编程
"""
import subprocess
import logging
import shlex
from typing import List, Optional, Union
from pathlib import Path


logger = logging.getLogger(__name__)


class CommandResult:
    """命令执行结果封装"""
    def __init__(self, returncode: int, stdout: str, stderr: str, command: List[str]):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.command = command

    @property
    def success(self) -> bool:
        return self.returncode == 0

    def __repr__(self) -> str:
        cmd_str = " ".join(shlex.quote(c) for c in self.command[:3]) + (" ..." if len(self.command) > 3 else "")
        return f"CommandResult(returncode={self.returncode}, command='{cmd_str}')"


def run_command(
    cmd: List[Union[str, Path]],
    *,
    capture_output: bool = True,
    timeout: Optional[int] = None,
    check: bool = True,
    cwd: Optional[Union[str, Path]] = None,
    env: Optional[dict] = None,
    input_data: Optional[str] = None
) -> CommandResult:
    """
    安全执行系统命令
    
    :param cmd: 命令参数列表
    :param capture_output: 是否捕获输出
    :param timeout: 超时时间（秒）
    :param check: 是否检查返回码
    :param cwd: 工作目录
    :param env: 环境变量
    :param input_data: 标准输入数据
    :return: CommandResult 对象
    :raises subprocess.TimeoutExpired: 超时
    :raises subprocess.CalledProcessError: check=True 且命令失败
    """
    # 转换 Path 对象为字符串
    cmd_strs = [str(c) for c in cmd]
    
    # 记录命令（敏感信息脱敏）
    safe_cmd = [shlex.quote(str(c)) for c in cmd_strs]
    logger.debug(f"Executing: {' '.join(safe_cmd)}")
    
    try:
        process = subprocess.run(
            cmd_strs,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            check=False,
            cwd=str(cwd) if cwd else None,
            env=env,
            input=input_data
        )
        
        result = CommandResult(
            returncode=process.returncode,
            stdout=process.stdout if capture_output else "",
            stderr=process.stderr if capture_output else "",
            command=cmd_strs
        )
        
        if capture_output:
            if process.stdout:
                logger.debug(f"STDOUT:\n{process.stdout}")
            if process.stderr:
                logger.debug(f"STDERR:\n{process.stderr}")
        
        if check and process.returncode != 0:
            logger.error(
                f"命令执行失败 (exit {process.returncode}):\n"
                f"  Command: {' '.join(safe_cmd)}\n"
                f"  stderr: {process.stderr.strip() if capture_output else 'N/A'}"
            )
            raise subprocess.CalledProcessError(
                process.returncode,
                cmd_strs,
                output=process.stdout if capture_output else None,
                stderr=process.stderr if capture_output else None
            )
        
        return result
        
    except subprocess.TimeoutExpired as e:
        logger.error(f"命令执行超时 ({timeout}s): {' '.join(safe_cmd)}")
        raise
    except FileNotFoundError as e:
        logger.error(f"命令未找到: {cmd_strs[0]} - 请确保已安装必要工具")
        raise