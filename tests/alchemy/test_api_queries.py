import json

import pytest

from duty_board.alchemy import api_queries


# @ToDo(jorrick) Add tests for the missing lines in API Queries.
def test_parse_extra_attributes() -> None:
    assert api_queries.parse_extra_attributes(0, None) == []

    with pytest.raises(TypeError, match="Expected extra_attributes field to be a dict"):
        api_queries.parse_extra_attributes(123, json.dumps([]))

    with pytest.raises(TypeError, match=r"Expected extra_attributes\[abc\] field to be a dict"):
        api_queries.parse_extra_attributes(123, json.dumps({"abc": []}))

    with pytest.raises(ValueError, match=r"Missing required extra_attributes\[abc\]\[information\]"):
        api_queries.parse_extra_attributes(123, json.dumps({"abc": {}}))

    value = {"nickname": {"information": "henkie"}}
    api_queries.parse_extra_attributes(123, json.dumps(value))
