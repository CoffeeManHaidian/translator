import os
import platform
import runpy
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def application_version() -> str:
    version_module = runpy.run_path(str(ROOT / "app" / "version.py"))
    return str(version_module["__version__"])


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

    return Path(
        shutil.make_archive(
            str(archive_base),
            "zip",
            root_dir=application_path.parent,
            base_dir=application_path.name,
        )
    )


def main() -> int:
    application_path = build_application()
    smoke_test(application_path)
    archive_path = create_release_archive(application_path)
    print(f"Application: {application_path}")
    print(f"Release archive: {archive_path}")
    print(f"Version: {application_version()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
