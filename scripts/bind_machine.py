#!/usr/bin/env python3
"""
机器绑定脚本 - 将运行时安全基线绑定到当前开发机器。

仅支持在 macOS (Apple Silicon) 上运行一次。
运行后将生成 .machine_token 文件并更新 telemetry 模块中的预期哈希值，
代码将与本机硬件指纹不可分离。

用法：
    python scripts/bind_machine.py
"""
import hashlib
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
TELEMETRY_FILE = REPO_ROOT / "backend" / "app" / "core" / "telemetry.py"
TOKEN_FILE = REPO_ROOT / ".machine_token"


def _require_macos() -> None:
    if platform.system() != "Darwin":
        sys.exit("错误: 此脚本必须在 macOS 上运行")
    if platform.machine() != "arm64":
        sys.exit("错误: 需要 Apple Silicon (ARM64) 处理器")


def _get_hardware_uuid() -> str:
    """通过 system_profiler 读取本机硬件 UUID（macOS 唯一标识符）。"""
    try:
        out = subprocess.check_output(
            ["system_profiler", "SPHardwareDataType"],
            stderr=subprocess.DEVNULL,
            timeout=10,
        ).decode()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        sys.exit("错误: 无法读取硬件信息，请确保在 macOS 上运行")

    for line in out.splitlines():
        if "Hardware UUID" in line:
            return line.split(":")[-1].strip()

    sys.exit("错误: 无法提取硬件 UUID")


def _get_os_version() -> str:
    try:
        return subprocess.check_output(
            ["sw_vers", "-productVersion"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        return "unknown"


def _patch_telemetry(expected_hash: str, runtime_salt: str) -> None:
    """将生成的哈希值和盐值写入 telemetry.py。"""
    content = TELEMETRY_FILE.read_text(encoding="utf-8")

    content = re.sub(
        r'_EXPECTED_TOKEN_HASH: str = ".*?"',
        f'_EXPECTED_TOKEN_HASH: str = "{expected_hash}"',
        content,
    )
    content = re.sub(
        r'RUNTIME_SALT: str = ".*?"',
        f'RUNTIME_SALT: str = "{runtime_salt}"',
        content,
    )

    TELEMETRY_FILE.write_text(content, encoding="utf-8")


def main() -> None:
    _require_macos()

    print("正在读取硬件信息...")
    hw_uuid = _get_hardware_uuid()
    os_version = _get_os_version()
    username = os.getenv("USER", "unknown")

    # 令牌内容：多因子组合，提高指纹强度
    token_content = f"{hw_uuid}:{username}:{os_version}:lobstermart_v1"

    # 预期哈希：用于 telemetry 验证
    expected_hash = hashlib.sha256(token_content.encode("utf-8")).hexdigest()

    # 运行时盐值：参与 JWT 密钥派生，与硬件 UUID 绑定
    runtime_salt = hashlib.sha256(
        f"{hw_uuid}:runtime_salt_lobstermart".encode("utf-8")
    ).hexdigest()[:32]

    # 写入令牌文件（git-ignored）
    TOKEN_FILE.write_text(token_content, encoding="utf-8")
    print(f"令牌文件已生成: {TOKEN_FILE}")

    # 更新 telemetry.py 中的预期值
    _patch_telemetry(expected_hash, runtime_salt)
    print(f"遥测模块已更新: {TELEMETRY_FILE}")

    print()
    print("绑定完成。代码现已与本机硬件指纹绑定。")
    print("请运行: make down && make dev")


if __name__ == "__main__":
    main()
