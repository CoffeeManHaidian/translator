import hashlib
import os
import platform
import re
import runpy
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEMANTIC_VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def application_version() -> str:
    version_module = runpy.run_path(str(ROOT / "app" / "version.py"))
    return str(version_module["__version__"])


def validate_release_metadata() -> str:
    """确保运行时和两个平台的打包版本完全一致。"""
    version = application_version()
    if SEMANTIC_VERSION_PATTERN.fullmatch(version) is None:
        raise RuntimeError(
            f"应用版本必须使用 major.minor.patch 格式：{version}"
        )

    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    windows_version = (
        ROOT / "packaging" / "windows_version_info.txt"
    ).read_text(encoding="utf-8")
    spec = (ROOT / "packaging" / "TradeTranslator.spec").read_text(
        encoding="utf-8"
    )

    project_version = re.search(
        r'^version = "([^"]+)"$',
        pyproject,
        re.MULTILINE,
    )
    mismatches: list[str] = []
    if project_version is None or project_version.group(1) != version:
        mismatches.append("pyproject.toml")
    if f"FileVersion', '{version}'" not in windows_version:
        mismatches.append("Windows FileVersion")
    if f"ProductVersion', '{version}'" not in windows_version:
        mismatches.append("Windows ProductVersion")
    if f'get("TRADE_TRANSLATOR_VERSION", "{version}")' not in spec:
        mismatches.append("PyInstaller spec")

    if mismatches:
        raise RuntimeError(
            "发布版本不一致，请先同步：" + "、".join(mismatches)
        )
    return version


def run_test_suite() -> None:
    """正式打包前运行完整测试，失败时立即停止。"""
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=ROOT,
        check=True,
    )


def normalized_architecture() -> str:
    architecture = platform.machine().lower()
    aliases = {
        "amd64": "x86_64",
        "x64": "x86_64",
        "aarch64": "arm64",
    }
    return aliases.get(architecture, architecture)


def build_application() -> Path:
    version = application_version()
    environment = os.environ.copy()
    environment["TRADE_TRANSLATOR_VERSION"] = version

    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "generate_app_icons.py")],
        cwd=ROOT,
        check=True,
        env=environment,
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--distpath",
            str(ROOT / "dist"),
            "--workpath",
            str(ROOT / "build" / "pyinstaller"),
            str(ROOT / "packaging" / "TradeTranslator.spec"),
        ],
        cwd=ROOT,
        check=True,
        env=environment,
    )

    if sys.platform == "darwin":
        return ROOT / "dist" / "Trade Translator.app"
    if sys.platform == "win32":
        return ROOT / "dist" / "TradeTranslator"
    raise RuntimeError("当前打包脚本只支持 Windows 和 macOS")


def smoke_test(application_path: Path) -> None:
    executable = (
        application_path / "Contents" / "MacOS" / "TradeTranslator"
        if sys.platform == "darwin"
        else application_path / "TradeTranslator.exe"
    )
    subprocess.run(
        [str(executable), "--smoke-test"],
        cwd=ROOT,
        check=True,
        timeout=30,
    )


def create_release_archive(application_path: Path) -> Path:
    version = application_version()
    system_name = "macos" if sys.platform == "darwin" else "windows"
    archive_base = ROOT / "release" / (
        f"TradeTranslator-{version}-{system_name}-"
        f"{normalized_architecture()}"
    )
    archive_base.parent.mkdir(parents=True, exist_ok=True)

    if sys.platform == "darwin":
        archive_path = archive_base.with_suffix(".zip")
        archive_path.unlink(missing_ok=True)
        subprocess.run(
            [
                "ditto",
                "-c",
                "-k",
                "--sequesterRsrc",
                "--keepParent",
                str(application_path),
                str(archive_path),
            ],
            check=True,
        )
        return archive_path

    archive_path = archive_base.with_suffix(".zip")
    archive_path.unlink(missing_ok=True)
    return Path(
        shutil.make_archive(
            str(archive_base),
            "zip",
            root_dir=application_path.parent,
            base_dir=application_path.name,
        )
    )


def create_checksum(archive_path: Path) -> tuple[Path, str]:
    """为发布压缩包生成可一同上传的 SHA256 文件。"""
    digest = hashlib.sha256()
    with archive_path.open("rb") as archive:
        for chunk in iter(lambda: archive.read(1024 * 1024), b""):
            digest.update(chunk)

    checksum = digest.hexdigest()
    checksum_path = archive_path.with_suffix(
        archive_path.suffix + ".sha256"
    )
    checksum_path.write_text(
        f"{checksum}  {archive_path.name}\n",
        encoding="utf-8",
    )
    return checksum_path, checksum


def main() -> int:
    version = validate_release_metadata()
    run_test_suite()
    application_path = build_application()
    smoke_test(application_path)
    archive_path = create_release_archive(application_path)
    checksum_path, checksum = create_checksum(archive_path)
    print(f"Application: {application_path}")
    print(f"Release archive: {archive_path}")
    print(f"Checksum file: {checksum_path}")
    print(f"SHA256: {checksum}")
    print(f"Version: {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
