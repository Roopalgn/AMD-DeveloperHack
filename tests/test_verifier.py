"""Tests for replay verifier."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from replaylab.backend.verifier import _load_json


def test_load_json_valid(tmp_path):
    f = tmp_path / "test.json"
    f.write_text('{"key": "value"}')
    result = _load_json(f)
    assert result == {"key": "value"}


def test_load_json_non_dict_raises(tmp_path):
    import pytest
    f = tmp_path / "list.json"
    f.write_text('[1, 2, 3]')
    with pytest.raises(ValueError, match="Expected JSON object"):
        _load_json(f)


def test_load_json_invalid_raises(tmp_path):
    import pytest
    f = tmp_path / "bad.json"
    f.write_text("not json at all")
    with pytest.raises(json.JSONDecodeError):
        _load_json(f)
