from pathlib import Path

from tools import build_app


def test_current_release_metadata_is_consistent() -> None:
    assert build_app.validate_release_metadata() == "0.1.0"


def test_create_checksum_matches_archive(tmp_path: Path) -> None:
    archive = tmp_path / "TradeTranslator-0.1.0-test.zip"
    archive.write_bytes(b"release artifact")

    checksum_path, checksum = build_app.create_checksum(archive)

    assert checksum == (
        "133cfccb5b503cf4040c95f3dfad56d07c157428"
        "3a1e39066b594f6ee33711ba"
    )
    assert checksum_path.name.endswith(".zip.sha256")
    assert checksum_path.read_text(encoding="utf-8") == (
        f"{checksum}  {archive.name}\n"
    )
