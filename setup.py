"""
NBD Mount 工具安装配置
"""
from setuptools import setup, find_packages

setup(
    name="nbdmount",
    version="1.0.0",
    description="基于 NBD 的虚拟机镜像挂载与管理工具",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="NBD Mount Team",
    license="MIT",
    packages=find_packages(exclude=["tests", "docs"]),
    entry_points={
        "console_scripts": [
            "nbdmount = nbdmount.__main__:main",
        ],
    },
    python_requires=">=3.7",
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Filesystems",
        "Topic :: System :: Recovery Tools",
        "Topic :: Utilities",
    ],
    keywords="nbd qemu disk image mount forensics",
)