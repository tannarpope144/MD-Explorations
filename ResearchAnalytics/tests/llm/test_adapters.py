from pydantic import BaseModel
from evaluate.llm.openai import OpenAIClient
from evaluate.llm.anthropic import AnthropicClient


class Toy(BaseModel):
    answer: str


def test_openai_extracts_json_content(mocker):
    fake_msg = mocker.Mock()
    fake_msg.content = '{"answer": "hi"}'
    fake_resp = mocker.Mock()
    fake_resp.choices = [mocker.Mock(message=fake_msg)]
    sdk = mocker.Mock()
    sdk.chat.completions.create.return_value = fake_resp
    c = OpenAIClient(client=sdk)
    out = c.structured_call(Toy, [{"role": "user", "content": "q"}], model="gpt-x")
    assert out.answer == "hi"
    kw = sdk.chat.completions.create.call_args.kwargs
    assert kw["response_format"]["type"] == "json_schema"


def test_anthropic_extracts_tool_input(mocker):
    block = mocker.Mock()
    block.type = "tool_use"
    block.input = {"answer": "hi"}
    fake_resp = mocker.Mock()
    fake_resp.content = [block]
    sdk = mocker.Mock()
    sdk.messages.create.return_value = fake_resp
    c = AnthropicClient(client=sdk)
    out = c.structured_call(Toy, [{"role": "user", "content": "q"}], model="claude-x")
    assert out.answer == "hi"
    kw = sdk.messages.create.call_args.kwargs
    assert kw["tool_choice"]["type"] == "tool"
