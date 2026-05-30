from abc import ABC, abstractmethod
from pydantic import BaseModel, ValidationError


class StructuredCallError(RuntimeError):
    pass


class LLMClient(ABC):
    @abstractmethod
    def _raw_structured(self, schema: type[BaseModel], messages: list[dict],
                        model: str, **kwargs) -> str:
        """Provider-specific call. Returns the raw JSON string the model produced."""
        ...

    def structured_call(self, schema: type[BaseModel], messages: list[dict],
                        model: str, max_retries: int = 3, **kwargs) -> BaseModel:
        convo = list(messages)
        last_err = None
        for _ in range(max_retries):
            raw = self._raw_structured(schema, convo, model, **kwargs)
            try:
                return schema.model_validate_json(raw)
            except ValidationError as e:
                last_err = e
                convo = convo + [
                    {"role": "assistant", "content": raw},
                    {"role": "user", "content":
                        f"Your previous response failed schema validation:\n{e}\n"
                        f"Return ONLY valid JSON matching the schema."},
                ]
        raise StructuredCallError(f"schema validation failed after "
                                  f"{max_retries} attempts: {last_err}")
