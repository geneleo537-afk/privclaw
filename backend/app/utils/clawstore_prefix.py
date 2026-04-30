"""
ClawStore 插件包前缀处理器。

功能：
1. 解压上传的 ZIP 文件
2. 找到 manifest.json / plugin.json / package.json，读取插件 ID
3. 在 manifest 的 id 字段前加 "clawstore." 前缀（幂等：已有则跳过）
4. 在入口文件（.py/.js/.ts）头部添加注释 `# clawstore:{id}`
5. 重新打包为 ZIP 并返回
6. 安全校验：防路径穿越、ZIP Bomb

安全边界：
- 解压路径限制在临时目录内，拒绝含 ../ 的条目
- 解压大小上限 100MB，条目数上限 1000
- 单个文件大小上限 50MB
"""
import io
import json
import logging
import os
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# 安全限制常量
MAX_UNCOMPRESSED_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_ENTRY_COUNT = 1000                      # 最多 1000 个条目
MAX_SINGLE_FILE_SIZE = 50 * 1024 * 1024    # 单文件 50 MB

# 支持的 manifest 文件名（按优先级排列）
MANIFEST_CANDIDATES = ["manifest.json", "plugin.json", "package.json"]

# 支持在头部添加注释的入口文件扩展名
ENTRY_FILE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx"}


@dataclass
class ProcessReport:
    """处理结果报告。"""

    success: bool
    manifest_file: Optional[str] = None
    plugin_id_original: Optional[str] = None
    plugin_id_final: Optional[str] = None
    entry_files_patched: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: Optional[str] = None


class ClawstorePrefixProcessor:
    """
    对上传的插件 ZIP 包进行前缀注入处理。

    使用方式：
        processor = ClawstorePrefixProcessor()
        patched_bytes, report = processor.process(zip_bytes)
        if report.success:
            # 使用 patched_bytes 存储到对象存储
    """

    PREFIX = "clawstore."

    def process(self, zip_bytes: bytes) -> tuple[bytes, ProcessReport]:
        """
        处理插件 ZIP 包。

        Args:
            zip_bytes: 原始 ZIP 文件字节内容

        Returns:
            (处理后的 ZIP 字节内容, 处理报告)
            若处理失败，返回原始字节和包含错误信息的报告
        """
        report = ProcessReport(success=False)

        try:
            return self._do_process(zip_bytes, report)
        except Exception as exc:
            logger.exception("插件包处理失败")
            report.error = str(exc)
            return zip_bytes, report

    def _do_process(
        self,
        zip_bytes: bytes,
        report: ProcessReport,
    ) -> tuple[bytes, ProcessReport]:
        """核心处理逻辑，在临时目录中完成所有操作。"""
        with tempfile.TemporaryDirectory(prefix="clawstore_") as tmp_dir:
            tmp_path = Path(tmp_dir)

            # 1. 安全解压
            self._safe_extract(zip_bytes, tmp_path)

            # 2. 寻找 manifest 文件
            manifest_path, manifest_data = self._find_manifest(tmp_path)
            if manifest_path is None:
                report.error = "未找到 manifest.json / plugin.json / package.json"
                return zip_bytes, report

            report.manifest_file = str(manifest_path.relative_to(tmp_path))

            # 3. 读取并修改插件 ID
            plugin_id = manifest_data.get("id") or manifest_data.get("name", "")
            if not plugin_id:
                report.warnings.append("manifest 中未找到 id 或 name 字段，跳过 ID 修改")
                plugin_id = "unknown"

            report.plugin_id_original = plugin_id

            if plugin_id.startswith(self.PREFIX):
                # 幂等：已有前缀，不重复添加
                report.plugin_id_final = plugin_id
                report.warnings.append(f"ID 已含 {self.PREFIX} 前缀，跳过修改")
            else:
                new_id = f"{self.PREFIX}{plugin_id}"
                manifest_data["id"] = new_id
                report.plugin_id_final = new_id
                # 写回 manifest（保留原始缩进格式）
                manifest_path.write_text(
                    json.dumps(manifest_data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

            # 4. 在入口文件头部注入注释
            final_id = report.plugin_id_final
            entry_files = self._patch_entry_files(tmp_path, final_id)
            report.entry_files_patched = entry_files

            # 5. 重新打包 ZIP
            output_bytes = self._repack_zip(tmp_path)

        report.success = True
        return output_bytes, report

    def _safe_extract(self, zip_bytes: bytes, dest: Path) -> None:
        """
        安全解压 ZIP 文件。

        防御：
        - 路径穿越（ZipSlip）：拒绝含 ../ 或绝对路径的条目
        - ZIP Bomb：限制总解压大小和条目数
        """
        total_size = 0
        entry_count = 0

        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
            for info in zf.infolist():
                # 路径穿越检测
                entry_path = Path(info.filename)
                if entry_path.is_absolute():
                    raise ValueError(f"ZIP 条目包含绝对路径，拒绝解压：{info.filename}")
                # 规范化后检查是否逃出目标目录
                resolved = (dest / info.filename).resolve()
                if not str(resolved).startswith(str(dest.resolve())):
                    raise ValueError(f"ZIP 条目路径穿越，拒绝解压：{info.filename}")

                # 条目数量限制
                entry_count += 1
                if entry_count > MAX_ENTRY_COUNT:
                    raise ValueError(
                        f"ZIP 条目数超过上限 {MAX_ENTRY_COUNT}，疑似 ZIP Bomb"
                    )

                # 单文件大小限制
                if info.file_size > MAX_SINGLE_FILE_SIZE:
                    raise ValueError(
                        f"单个文件 {info.filename} 大小超过 {MAX_SINGLE_FILE_SIZE // 1024 // 1024}MB"
                    )

                # 总大小限制
                total_size += info.file_size
                if total_size > MAX_UNCOMPRESSED_SIZE:
                    raise ValueError(
                        f"ZIP 解压后总大小超过 {MAX_UNCOMPRESSED_SIZE // 1024 // 1024}MB，疑似 ZIP Bomb"
                    )

                zf.extract(info, dest)

    def _find_manifest(
        self,
        root: Path,
    ) -> tuple[Optional[Path], Optional[dict]]:
        """
        在解压目录中查找 manifest 文件。

        查找优先级：manifest.json > plugin.json > package.json
        支持嵌套目录（如 ZIP 根目录包含一个子目录的情况）。
        """
        for candidate in MANIFEST_CANDIDATES:
            # 先检查根目录
            direct = root / candidate
            if direct.exists():
                return direct, self._load_json(direct)

            # 再检查一层子目录（ZIP 通常会有一个顶层目录）
            for child in root.iterdir():
                if child.is_dir():
                    nested = child / candidate
                    if nested.exists():
                        return nested, self._load_json(nested)

        return None, None

    def _load_json(self, path: Path) -> dict:
        """加载 JSON 文件，解析失败时抛出 ValueError。"""
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON 解析失败：{path.name}，原因：{exc}") from exc

    def _patch_entry_files(self, root: Path, plugin_id: str) -> list[str]:
        """
        在所有入口文件（.py/.js/.ts 等）头部注入 clawstore 标识注释。

        注释格式：
        - Python: # clawstore:{plugin_id}
        - JS/TS:  // clawstore:{plugin_id}

        幂等：文件已含相同注释则跳过。
        """
        comment_marker = f"clawstore:{plugin_id}"
        patched: list[str] = []

        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix not in ENTRY_FILE_EXTENSIONS:
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                # 二进制文件或非 UTF-8 编码，跳过
                continue

            # 幂等检查
            if comment_marker in content.split("\n")[0] if content else False:
                continue

            # 根据文件类型选择注释符号
            comment_char = "//" if file_path.suffix in {".js", ".ts", ".jsx", ".tsx"} else "#"
            header_comment = f"{comment_char} {comment_marker}\n"

            file_path.write_text(header_comment + content, encoding="utf-8")
            patched.append(str(file_path.relative_to(root)))

        return patched

    def _repack_zip(self, source_dir: Path) -> bytes:
        """将处理后的目录重新打包为 ZIP 字节流。"""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in sorted(source_dir.rglob("*")):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zf.write(file_path, arcname)
        return buf.getvalue()
