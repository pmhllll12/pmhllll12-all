from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.command_parser_dto import ParsedCommand


class CommandParserPort(ABC):
    @abstractmethod
    async def parse(self, website: str, command: str) -> ParsedCommand:
        """자연어 명령어에서 keyword와 크롤링 범위(max_depth, max_pages)를 추출한다."""
        raise NotImplementedError
