from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from admin.app.ports.output.pdf_text_extractor_port import PdfTextExtractorPort
from neo4j_graphrag.experimental.components.data_loader import PdfLoader
from neo4j_graphrag.experimental.components.types import LoadedDocument


class Neo4jGraphRagPdfTextExtractor(PdfTextExtractorPort):
    """neo4j-graphrag의 `PdfLoader`(pypdf 기반)로 업로드된 PDF에서 텍스트를 추출한다."""

    async def extract(self, content: bytes, filename: str) -> str:
        suffix = Path(filename).suffix or ".pdf"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)
        try:
            # PdfLoader.run은 async def지만 내부는 pypdf 동기 파싱이라 to_thread로 오프로드.
            document = await asyncio.to_thread(_load_pdf_sync, tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)
        return document.text


def _load_pdf_sync(path: Path) -> LoadedDocument:
    return asyncio.run(PdfLoader().run(filepath=path))
