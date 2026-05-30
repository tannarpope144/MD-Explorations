from enum import IntEnum, Enum
from pydantic import BaseModel, Field, field_validator


class SourceTier(IntEnum):
    T1 = 1  # primary data / official statistics
    T2 = 2  # peer-reviewed
    T3 = 3  # reputable secondary
    T4 = 4  # advocacy / opinion


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SPECULATIVE = "speculative"


class Lean(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    NEUTRAL = "neutral"


class Evidence(BaseModel):
    claim_text: str
    url: str
    title: str
    tier: SourceTier


class Claim(BaseModel):
    statement: str
    data: list[Evidence] = Field(min_length=1)
    insight: str
    bias_note: str
    confidence: Confidence

    @field_validator("bias_note", "insight", "statement")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v


class Case(BaseModel):
    location: str
    start_date: str
    end_date: str
    scale: str
    funding_model: str
    target_population: str
    outcome_metric: str
    result: str
    tier: SourceTier
    source_urls: list[str] = Field(min_length=1)


class SpeculationNode(BaseModel):
    hypothesis: str
    lean: Lean
    evidence: list[Evidence]
    status: str
    depth: int


class VerificationThread(BaseModel):
    outcome: str
    nodes: list[SpeculationNode]
    cut_short: bool = False
    cut_short_reason: str | None = None


class ConditionalBranch(BaseModel):
    condition: str
    judgment: str


class Verdict(BaseModel):
    bottom_line: str
    reasoning: str
    strongest_counter: str
    confidence: Confidence

    @field_validator("bottom_line", "reasoning", "strongest_counter")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v


class Positions(BaseModel):
    pro: list[Claim]
    against: list[Claim]
    inbetween: list[Claim]
