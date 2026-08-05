from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Review:

    id: str

    game: str

    source: str

    type: str

    platform: str

    author: Optional[str]

    language: Optional[str]

    date: str

    score: dict

    text: str

    text_completeness: str

    word_count: int

    engagement: dict = field(
        default_factory=dict
    )

    flags: dict = field(
        default_factory=dict
    )

    source_meta: dict = field(
        default_factory=dict
    )
