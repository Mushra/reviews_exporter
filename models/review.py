from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Review:

    id: str

    game: str

    review_type: str

    platform: str

    author: Optional[str]

    publication: Optional[str]

    date: str

    score: Optional[int]

    text: str

    source: dict = field(
        default_factory=dict
    )

    metadata: dict = field(
        default_factory=dict
    )