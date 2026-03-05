import json

from shorthand_llm.graph_utils import clean_json_output, enforce_schema


# ── clean_json_output ──


class TestCleanJsonOutput:
    def test_strips_json_fence(self):
        raw = '```json\n{"nodes": []}\n```'
        assert clean_json_output(raw) == '{"nodes": []}'

    def test_strips_fence_no_newline(self):
        raw = '```json{"nodes": []}```'
        assert clean_json_output(raw) == '{"nodes": []}'

    def test_plain_json_unchanged(self):
        raw = '{"nodes": [], "edges": []}'
        assert clean_json_output(raw) == raw

    def test_whitespace_trimmed(self):
        raw = '  \n {"nodes": []}  \n '
        assert clean_json_output(raw) == '{"nodes": []}'

    def test_nested_backticks_in_content(self):
        raw = '```json\n{"code": "use `this`"}\n```'
        result = clean_json_output(raw)
        parsed = json.loads(result)
        assert parsed["code"] == "use `this`"


# ── enforce_schema ──


class TestEnforceSchema:
    def test_none_returns_empty(self):
        assert enforce_schema(None) == {}

    def test_empty_dict_returns_empty(self):
        assert enforce_schema({}) == {}

    def test_string_passthrough(self):
        assert enforce_schema({"name": "Alice"}) == {"name": "Alice"}

    def test_int_to_string(self):
        assert enforce_schema({"age": 30}) == {"age": "30"}

    def test_float_to_string(self):
        assert enforce_schema({"score": 3.14}) == {"score": "3.14"}

    def test_bool_to_string(self):
        assert enforce_schema({"active": True}) == {"active": "True"}

    def test_list_to_comma_separated(self):
        result = enforce_schema({"tags": ["python", "rust", "go"]})
        assert result == {"tags": "python, rust, go"}

    def test_list_with_mixed_types(self):
        result = enforce_schema({"vals": [1, "two", 3.0]})
        assert result == {"vals": "1, two, 3.0"}

    def test_dict_to_json_string(self):
        inner = {"a": 1, "b": "two"}
        result = enforce_schema({"meta": inner})
        assert json.loads(result["meta"]) == inner

    def test_mixed_props(self):
        props = {
            "name": "Node",
            "count": 42,
            "tags": ["x", "y"],
            "nested": {"k": "v"},
        }
        result = enforce_schema(props)
        assert result["name"] == "Node"
        assert result["count"] == "42"
        assert result["tags"] == "x, y"
        assert json.loads(result["nested"]) == {"k": "v"}
