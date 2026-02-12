# x-nbd

x-nbd是一套基于 NBD（Network Block Device）机制的磁盘镜像挂载与管理工具，提供将虚拟机镜像映射为本地块设备并安全挂载的能力。

## 功能特性

- **多格式支持**: 支持 QCOW2、RAW 等常见虚拟机镜像格式
- **自动检测**: 智能识别镜像格式，无需手动指定
- **安全挂载**: 默认以只读模式挂载，避免误操作损坏镜像
- **分区识别**: 自动识别并挂载镜像中的所有分区
- **资源管理**: 使用上下文管理器自动管理 NBD 设备和挂载点
- **命令行接口**: 简洁易用的 CLI 工具，支持多种操作模式

## 系统要求

- **操作系统**: Linux (需要内核支持 NBD)
- **Python**: 3.7+
- **依赖工具**:
  - `qemu-nbd` - QEMU NBD 工具
  - `qemu-img` - QEMU 镜像工具
  - `partprobe` - 分区表重读工具
  - `mount`/`umount` - 挂载/卸载工具

## 安装

### 1. 安装依赖

在 Ubuntu/Debian 系统上：

```bash
sudo apt update
sudo apt install qemu-utils util-linux
```

在 CentOS/RHEL 系统上：

```bash
sudo yum install qemu-img util-linux
```

### 2. 加载 NBD 内核模块

```bash
sudo modprobe nbd max_part=16
```

### 3. 安装 x-nbd

```bash
pip install nbdmount
```

或从源码安装：

```bash
git clone https://github.com/yeyushilai/x-nbd.git
cd x-nbd
pip install -e .
```

## 使用说明

### 基本命令

```bash
# 查看帮助
nbdmount --help

# 检查运行环境
nbdmount disk.qcow2 check

# 查看镜像信息
nbdmount disk.qcow2 info

# 列出镜像中的分区
nbdmount disk.qcow2 list

# 挂载镜像分区（只读模式）
sudo nbdmount disk.qcow2 mount

# 挂载到指定目录
sudo nbdmount disk.qcow2 mount --mount-dir /mnt/forensics

# 以读写模式挂载（谨慎使用）
sudo nbdmount disk.qcow2 mount --rw
```

### 使用示例

#### 示例 1: 挂载 QCOW2 镜像

```bash
# 挂载镜像
sudo nbdmount vm-disk.qcow2 mount

# 输出示例：
# ✓ 镜像格式识别: qcow2 (vm-disk.qcow2)
# 将镜像 'vm-disk.qcow2' 连接到 /dev/nbd0
# 在 /dev/nbd0 上检测到 2 个分区: ['/dev/nbd0p1', '/dev/nbd0p2']
# 挂载 /dev/nbd0p1 到 /mnt/nbd-vm-disk/part1
# ✓ 挂载成功: /dev/nbd0p1 -> /mnt/nbd-vm-disk/part1
# 挂载 /dev/nbd0p2 到 /mnt/nbd-vm-disk/part2
# ✓ 挂载成功: /dev/nbd0p2 -> /mnt/nbd-vm-disk/part2
#
# ✓ 挂载成功:
#   /dev/nbd0p1          -> /mnt/nbd-vm-disk/part1
#   /dev/nbd0p2          -> /mnt/nbd-vm-disk/part2
#
# 💡 提示: 使用 'nbdmount <image> umount' 或重启系统来清理挂载
```

#### 示例 2: 查看镜像信息

```bash
nbdmount vm-disk.qcow2 info

# 输出示例：
# 镜像信息:
#   路径:     /path/to/vm-disk.qcow2
#   格式:     qcow2
#   大小:     20.00 GB (21474836480 bytes)
#   挂载模式: 只读
```

#### 示例 3: 列出分区

```bash
nbdmount vm-disk.qcow2 list

# 输出示例：
# ✓ 在镜像中找到 2 个分区:
#   1. /dev/nbd0p1
#   2. /dev/nbd0p2
```

### 卸载镜像

```bash
# 手动卸载所有分区
sudo umount /mnt/nbd-vm-disk/part*
sudo qemu-nbd --disconnect /dev/nbd0

# 或重启系统自动清理
```

## 项目结构

```
x-nbd/
├── nbdmount/
│   ├── __init__.py          # 包初始化和公共 API
│   ├── __main__.py          # 命令行主入口
│   ├── cli/
│   │   └── parser.py        # 命令行参数解析
│   ├── core/
│   │   ├── device.py        # NBD 设备抽象层
│   │   ├── manager.py       # 挂载管理器
│   │   └── mounter.py       # 分区挂载管理
│   ├── formats/
│   │   ├── base.py          # 镜像格式抽象基类
│   │   ├── qcow2.py         # QCOW2 格式实现
│   │   └── raw.py           # RAW 格式实现
│   ├── utils/
│   │   ├── command.py       # 命令执行封装
│   │   ├── devices.py       # 设备管理工具
│   │   └── validators.py    # 验证工具
│   └── exceptions/
│       └── errors.py       # 异常定义
├── setup.py                 # 安装配置
└── README.md                # 项目文档
```

## 开发指南

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/yeyushilai/x-nbd.git
cd x-nbd

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e .
```

### 代码风格

项目遵循 PEP 8 编码规范，建议使用以下工具：

```bash
pip install black flake8 mypy

# 格式化代码
black nbd/

# 检查代码风格
flake8 nbd/

# 类型检查
mypy nbd/
```

### 测试

```bash
# 运行测试
python -m pytest tests/
```

## Issue 提交规范

### 提交 Issue 前请检查

1. 搜索现有 Issue，确认问题未被报告
2. 确认问题是否为已知限制或配置错误
3. 准备复现步骤和环境信息

### Issue 模板

提交 Bug 报告时，请包含以下信息：

#### 标题格式
`[Bug] 简短的问题描述` 或 `[Feature] 功能建议`

#### 内容模板

```markdown
## 问题描述
清晰描述遇到的问题或建议的功能

## 复现步骤
1. 执行命令: `nbdmount disk.qcow2 mount`
2. 观察到的错误信息: ...
3. 期望的行为: ...

## 环境信息
- 操作系统: Ubuntu 20.04
- Python 版本: 3.9.7
- x-nbd 版本: 1.0.0
- 镜像格式: qcow2
- 镜像大小: 10GB

## 错误日志
```
粘贴完整的错误日志，包括堆栈跟踪
```

## 附加信息
任何其他有助于解决问题的信息
```

### Issue 分类

使用以下标签分类 Issue：

- `bug` - 程序错误
- `enhancement` - 功能增强
- `documentation` - 文档改进
- `question` - 使用问题
- `help wanted` - 需要帮助
- `good first issue` - 适合新手

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

### Pull Request 规范

- 标题格式: `[类型] 简短描述`
  - 类型: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- 描述中说明更改内容和原因
- 关联相关 Issue
- 确保代码通过测试和代码风格检查

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 致谢

- QEMU 项目提供的 NBD 工具
- 所有贡献者的支持

## 联系方式

- 项目主页: https://github.com/yeyushilai/x-nbd
- 问题反馈: https://github.com/yeyushilai/x-nbd/issues

## 常见问题

### Q: 提示 "需要 root 权限运行此工具"？
A: NBD 设备操作需要 root 权限，请使用 `sudo` 运行命令。

### Q: 提示 "未找到空闲 NBD 设备"？
A: 可能是 NBD 模块未加载或所有设备已被占用，执行 `sudo modprobe nbd max_part=16` 加载模块。

### Q: 挂载后如何卸载？
A: 手动执行 `sudo umount` 卸载所有挂载点，然后执行 `sudo qemu-nbd --disconnect /dev/nbdX` 断开设备。

### Q: 支持哪些镜像格式？
A: 当前支持 QCOW2 和 RAW 格式，未来计划支持 VMDK、VDI 等格式。
