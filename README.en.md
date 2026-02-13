# x-nbd

A disk image mounting and management tool based on NBD (Network Block Device) mechanism, providing the ability to map virtual machine images to local block devices and mount them safely.

## Features

- **Multi-format Support**: Supports common virtual machine image formats including QCOW2 and RAW
- **Auto Detection**: Intelligently identifies image formats without manual specification
- **Safe Mounting**: Mounts in read-only mode by default to prevent accidental damage to images
- **Partition Recognition**: Automatically identifies and mounts all partitions within the image
- **Resource Management**: Uses context managers to automatically manage NBD devices and mount points
- **Command Line Interface**: Simple and easy-to-use CLI tool with multiple operation modes

## System Requirements

- **Operating System**: Linux (requires kernel NBD support)
- **Python**: 3.7+
- **Dependencies**:
  - `qemu-nbd` - QEMU NBD tool
  - `qemu-img` - QEMU image tool
  - `partprobe` - Partition table reread tool
  - `mount`/`umount` - Mount/unmount tools

## Installation

### 1. Install Dependencies

On Ubuntu/Debian systems:

```bash
sudo apt update
sudo apt install qemu-utils util-linux
```

On CentOS/RHEL systems:

```bash
sudo yum install qemu-img util-linux
```

### 2. Load NBD Kernel Module

```bash
sudo modprobe nbd max_part=16
```

### 3. Install x-nbd

```bash
pip install nbdmount
```

Or install from source:

```bash
git clone https://github.com/yeyushilai/x-nbd.git
cd x-nbd
pip install -e .
```

## Usage

### Basic Commands

```bash
# View help
nbdmount --help

# Check runtime environment
nbdmount disk.qcow2 check

# View image information
nbdmount disk.qcow2 info

# List partitions in the image
nbdmount disk.qcow2 list

# Mount image partitions (read-only mode)
sudo nbdmount disk.qcow2 mount

# Mount to a specific directory
sudo nbdmount disk.qcow2 mount --mount-dir /mnt/forensics

# Mount in read-write mode (use with caution)
sudo nbdmount disk.qcow2 mount --rw
```

### Usage Examples

#### Example 1: Mount QCOW2 Image

```bash
# Mount image
sudo nbdmount vm-disk.qcow2 mount

# Example output:
# ✓ Image format detected: qcow2 (vm-disk.qcow2)
# Connecting image 'vm-disk.qcow2' to /dev/nbd0
# Detected 2 partitions on /dev/nbd0: ['/dev/nbd0p1', '/dev/nbd0p2']
# Mounting /dev/nbd0p1 to /mnt/nbd-vm-disk/part1
# ✓ Mount successful: /dev/nbd0p1 -> /mnt/nbd-vm-disk/part1
# Mounting /dev/nbd0p2 to /mnt/nbd-vm-disk/part2
# ✓ Mount successful: /dev/nbd0p2 -> /mnt/nbd-vm-disk/part2
#
# ✓ Mount successful:
#   /dev/nbd0p1          -> /mnt/nbd-vm-disk/part1
#   /dev/nbd0p2          -> /mnt/nbd-vm-disk/part2
#
# 💡 Tip: Use 'nbdmount <image> umount' or reboot to clean up mounts
```

#### Example 2: View Image Information

```bash
nbdmount vm-disk.qcow2 info

# Example output:
# Image Information:
#   Path:     /path/to/vm-disk.qcow2
#   Format:   qcow2
#   Size:     20.00 GB (21474836480 bytes)
#   Mode:     Read-only
```

#### Example 3: List Partitions

```bash
nbdmount vm-disk.qcow2 list

# Example output:
# ✓ Found 2 partitions in image:
#   1. /dev/nbd0p1
#   2. /dev/nbd0p2
```

### Unmounting Images

```bash
# Manually unmount all partitions
sudo umount /mnt/nbd-vm-disk/part*
sudo qemu-nbd --disconnect /dev/nbd0

# Or reboot to automatically clean up
```

## Project Structure

```
x-nbd/
├── nbdmount/
│   ├── __init__.py          # Package initialization and public API
│   ├── __main__.py          # Command line main entry point
│   ├── cli/
│   │   └── parser.py        # Command line argument parsing
│   ├── core/
│   │   ├── device.py        # NBD device abstraction layer
│   │   ├── manager.py       # Mount manager
│   │   └── mounter.py       # Partition mount management
│   ├── formats/
│   │   ├── base.py          # Image format abstract base class
│   │   ├── qcow2.py         # QCOW2 format implementation
│   │   └── raw.py           # RAW format implementation
│   ├── utils/
│   │   ├── command.py       # Command execution wrapper
│   │   ├── devices.py       # Device management utilities
│   │   └── validators.py    # Validation utilities
│   └── exceptions/
│       └── errors.py       # Exception definitions
├── setup.py                 # Installation configuration
└── README.md                # Project documentation
```

## Development Guide

### Development Environment Setup

```bash
# Clone repository
git clone https://github.com/yeyushilai/x-nbd.git
cd x-nbd

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install development dependencies
pip install -e .
```

### Code Style

The project follows PEP 8 coding standards. It's recommended to use the following tools:

```bash
pip install black flake8 mypy

# Format code
black nbd/

# Check code style
flake8 nbd/

# Type checking
mypy nbd/
```

### Testing

```bash
# Run tests
python -m pytest tests/
```

## Issue Submission Guidelines

### Before Submitting an Issue

1. Search existing issues to confirm the problem hasn't been reported
2. Confirm if the issue is a known limitation or configuration error
3. Prepare reproduction steps and environment information

### Issue Template

When submitting a bug report, please include the following information:

#### Title Format
`[Bug] Short description of the issue` or `[Feature] Feature suggestion`

#### Content Template

```markdown
## Problem Description
Clearly describe the problem encountered or the suggested feature

## Reproduction Steps
1. Execute command: `nbdmount disk.qcow2 mount`
2. Observed error message: ...
3. Expected behavior: ...

## Environment Information
- Operating System: Ubuntu 20.04
- Python Version: 3.9.7
- x-nbd Version: 1.0.0
- Image Format: qcow2
- Image Size: 10GB

## Error Logs
```
Paste complete error logs, including stack traces
```

## Additional Information
Any other information that helps solve the problem
```

### Issue Classification

Use the following labels to classify issues:

- `bug` - Program error
- `enhancement` - Feature enhancement
- `documentation` - Documentation improvement
- `question` - Usage question
- `help wanted` - Help needed
- `good first issue` - Good for beginners

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Submit a Pull Request

### Pull Request Guidelines

- Title format: `[type] Short description`
  - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Describe what changes were made and why in the description
- Reference related issues
- Ensure code passes tests and code style checks

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

- QEMU project for providing NBD tools
- All contributors for their support

## Contact

- Project Homepage: https://github.com/yeyushilai/x-nbd
- Issue Tracker: https://github.com/yeyushilai/x-nbd/issues

## FAQ

### Q: Getting "Need root privileges to run this tool"?
A: NBD device operations require root privileges. Please run commands with `sudo`.

### Q: Getting "No available NBD device found"?
A: The NBD module may not be loaded or all devices are occupied. Run `sudo modprobe nbd max_part=16` to load the module.

### Q: How to unmount after mounting?
A: Manually execute `sudo umount` to unmount all mount points, then run `sudo qemu-nbd --disconnect /dev/nbdX` to disconnect the device.

### Q: What image formats are supported?
A: Currently supports QCOW2 and RAW formats. Plans to support VMDK, VDI, and other formats in the future.
