from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.domain.evidence import Evidence
from ontology.domain.verdict import Verdict


class JudgeUseCase(ABC):
    @abstractmethod
    async def evaluate(self, evidence: Evidence) -> Verdict:
        raise NotImplementedError
