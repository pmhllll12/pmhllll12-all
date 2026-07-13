from __future__ import annotations

from pathlib import Path

from ultralytics import YOLO
from ultralytics.utils import ASSETS


def main() -> None:
    model = YOLO("yolo11n.pt")
    results = model(ASSETS / "bus.jpg")

    for result in results:
        result.show()
        result.save(filename=str(Path(__file__).parent / "yolo_hello_world.jpg"))


if __name__ == "__main__":
    main()
