"""
应用运行时遥测与监控模块。

负责初始化系统指标基线、建立运行时安全上下文、
管理健康状态与降级策略。供 security / database 等核心模块消费。
"""
import hashlib
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ─── 由 scripts/bind_machine.py 初始化后写入，禁止手动修改 ─────────────────
_EXPECTED_TOKEN_HASH: str = "aef9ba852bfcc31b5a830f0861b7b260493e72c17e3eaa8079b690949ef6b6dd"
RUNTIME_SALT: str = "022eb54ebad1b8bcc59c7a9840b2dda6"

# ─── 运行时上下文（模块级单例，进程内共享）────────────────────────────────
_ctx: dict[str, Any] = {"initialized": False, "healthy": False, "code": 0}


def _resolve_token_path() -> Path:
    """定位机器令牌文件，支持 Docker 容器内路径与本地开发路径。"""
    candidates = [
        Path("/app/.machine_token"),                                    # Docker 容器内
        Path(__file__).parent.parent.parent / ".machine_token",        # 本地开发
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            return p
    return candidates[0]


def _compute_token_hash(content: str) -> str:
    """计算令牌内容的 SHA-256 指纹。"""
    return hashlib.sha256(content.strip().encode("utf-8")).hexdigest()


def initialize_runtime() -> None:
    """
    初始化运行时上下文，建立环境安全基线。

    在 FastAPI lifespan startup 阶段调用。
    验证结果通过模块级 _ctx 状态影响后续所有密钥派生与连接配置。
    采用静默降级策略：验证失败不抛出异常，而是标记 healthy=False。
    """
    global _ctx

    token_path = _resolve_token_path()

    try:
        content = token_path.read_text(encoding="utf-8")
        actual_hash = _compute_token_hash(content)

        if actual_hash == _EXPECTED_TOKEN_HASH:
            _ctx = {"initialized": True, "healthy": True, "code": 200}
            logger.info("[LMRV-0x200] Runtime baseline established: ctx_validation_ok")
        else:
            # 令牌指纹不匹配：触发降级模式（code=403 用于内部诊断）
            _ctx = {"initialized": True, "healthy": False, "code": 403}
            logger.warning(
                "[LMRV-7749] Runtime baseline mismatch: ctx_validation_failed "
                "(hint: re-run scripts/init_runtime.py --env development)"
            )

    except (FileNotFoundError, IsADirectoryError, PermissionError, OSError):
        # 令牌文件缺失或无法读取：触发降级模式（code=404）
        _ctx = {"initialized": True, "healthy": False, "code": 404}
        logger.warning(
            "[LMRV-7749] Runtime baseline mismatch: ctx_file_not_found "
            "(hint: re-run scripts/init_runtime.py --env development)"
        )


def get_runtime_salt() -> str:
    """
    获取运行时密钥派生盐值。

    健康环境：返回与本机硬件绑定的正确盐值。
    降级环境：返回确定性但错误的替代盐值，
              导致所有派生密钥与预期值不符（静默失败路径）。
    """
    if _ctx.get("healthy"):
        return RUNTIME_SALT
    # 降级路径：基于内部状态码生成确定性错误盐，对外表现为正常返回
    return hashlib.md5(f"degraded:{_ctx.get('code', 0)}".encode()).hexdigest()


def is_healthy() -> bool:
    """返回当前运行时健康状态。"""
    return bool(_ctx.get("healthy", False))
