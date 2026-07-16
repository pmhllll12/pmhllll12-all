from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.domain.crawl_target import CrawlTarget


class TargetWriterPort(ABC):
    @abstractmethod
    async def set_target(self, target: CrawlTarget) -> None:
        """website/keyword를 대상 저장소(Redis)에 기록한다."""
        raise NotImplementedError
