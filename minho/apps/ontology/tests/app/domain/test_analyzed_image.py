from __future__ import annotations

from datetime import datetime

import pytest
from ontology.domain.analyzed_image import AnalyzedImage


def test_valid_analyzed_image():
    image = AnalyzedImage(
        filename="cat.jpg",
        caption="갈색 고양이가 소파에 앉아 있다",
        tags=["고양이", "동물", "실내"],
        image_key="vision/abc123-cat.jpg",
        analyzed_at=datetime(2026, 7, 3, 12, 0, 0),
    )
    assert image.filename == "cat.jpg"
    assert "고양이" in image.tags


def test_blank_filename_raises():
    with pytest.raises(ValueError, match="filename은 비어 있을 수 없습니다"):
        AnalyzedImage(
            filename="   ",
            caption="설명",
            tags=[],
            image_key="vision/abc123-cat.jpg",
            analyzed_at=datetime.now(),
        )


def test_blank_caption_raises():
    with pytest.raises(ValueError, match="caption은 비어 있을 수 없습니다"):
        AnalyzedImage(
            filename="cat.jpg",
            caption="  ",
            tags=[],
            image_key="vision/abc123-cat.jpg",
            analyzed_at=datetime.now(),
        )


def test_blank_image_key_raises():
    with pytest.raises(ValueError, match="image_key는 비어 있을 수 없습니다"):
        AnalyzedImage(
            filename="cat.jpg", caption="설명", tags=[], image_key="  ", analyzed_at=datetime.now()
        )


def test_immutable():
    image = AnalyzedImage(
        filename="cat.jpg",
        caption="설명",
        tags=[],
        image_key="vision/abc123-cat.jpg",
        analyzed_at=datetime.now(),
    )
    with pytest.raises(Exception):
        image.filename = "다른 파일명"  # type: ignore[misc]
