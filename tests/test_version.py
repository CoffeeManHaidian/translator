import re
from pathlib import Path

from app.version import __version__


ROOT = Path(__file__).resolve().parents[1]


def test_mvp_version_is_0_1_0() -> None:
    assert __version__ == "0.1.0"


def test_packaging_versions_match_runtime_version() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    windows_version = (
        ROOT / "packaging" / "windows_version_info.txt"
    ).read_text(encoding="utf-8")

    project_version = re.search(
        r'^version = "([^"]+)"$',
        pyproject,
        re.MULTILINE,
    )
    assert project_version is not None
    assert project_version.group(1) == __version__
    assert f"FileVersion', '{__version__}'" in windows_version
    assert f"ProductVersion', '{__version__}'" in windows_version
