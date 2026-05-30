import pytest
from pydantic import BaseModel
from evaluate.llm.base import LLMClient, StructuredCallError


class Toy(BaseModel):
    answer: str


class FakeClient(LLMClient):
    """Returns queued raw strings; lets us test validate-and-retry."""
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def _raw_structured(self, schema, messages, model, **kw):
        self.calls.append(messages)
        return self._responses.pop(0)


def test_returns_validated_instance():
    c = FakeClient(['{"answer": "ok"}'])
    out = c.structured_call(Toy, [{"role": "user", "content": "hi"}], model="m")
    assert isinstance(out, Toy) and out.answer == "ok"


def test_retries_then_succeeds():
    c = FakeClient(['{"bad": 1}', '{"answer": "fixed"}'])
    out = c.structured_call(Toy, [{"role": "user", "content": "hi"}], model="m",
                            max_retries=2)
    assert out.answer == "fixed"
    assert len(c.calls) == 2
    assert "answer" in str(c.calls[1])


def test_raises_after_exhausting_retries():
    c = FakeClient(['{"bad": 1}', '{"bad": 2}'])
    with pytest.raises(StructuredCallError):
        c.structured_call(Toy, [{"role": "user", "content": "hi"}], model="m",
                          max_retries=2)
