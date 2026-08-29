from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


ROOT = Path(__file__).resolve().parents[1]


def render_icon(source: Path, target: Path, size: int) -> None:
    renderer = QSvgRenderer(str(source))
    if not renderer.isValid():
        raise RuntimeError(f"无法读取应用图标：{source}")

    image = QImage(
        QSize(size, size),
        QImage.Format.Format_ARGB32_Premultiplied,
    )
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()

    if not image.save(str(target)):
        raise RuntimeError(f"无法生成应用图标：{target}")


def main() -> int:
    application = QGuiApplication([])
    source = ROOT / "icons" / "app.svg"
    render_icon(source, ROOT / "icons" / "app.ico", 256)
    render_icon(source, ROOT / "icons" / "app.icns", 1024)
    application.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
