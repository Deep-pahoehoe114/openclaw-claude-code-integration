"""
conftest.py — pytest fixtures and shared mocks

Provides:
- mock_lancedb: patches LanceDB so tests don't need a real DB
- mock_minimax_api: patches MiniMax API calls
- sample_messages: fake session messages for self_eval tests
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# add scripts to path
SKILLS_ROOT = Path(__file__).parent.parent / "skills"
for skill in SKILLS_ROOT.iterdir():
    scripts = skill / "scripts"
    if scripts.is_dir():
        sys.path.insert(0, str(scripts))


# ─── LanceDB mock ─────────────────────────────────────────────────────────

class MockLanceDBTable:
    def __init__(self):
        self._rows = []

    def add(self, rows):
        self._rows.extend(rows)

    def search(self):
        return MockSearch(self._rows)

    def scan(self):
        return iter(self._rows)


class MockSearch:
    def __init__(self, rows):
        self._rows = rows

    def limit(self, n):
        return self

    def to_list(self):
        return self._rows


class MockLanceDB:
    def __init__(self):
        self._tables = {}

    def open_table(self, name):
        if name not in self._tables:
            self._tables[name] = MockLanceDBTable()
        return self._tables[name]

    @property
    def memories(self):
        return self._tables.get("memories", MockLanceDBTable())


@pytest.fixture
def mock_lancedb():
    """Replace lancedb.connect with a mock that returns in-memory data."""
    mock_db = MockLanceDB()

    with patch("lancedb.connect", return_value=mock_db):
        yield mock_db


@pytest.fixture
def mock_minimax_api():
    """Replace MiniMax API calls with a deterministic fallback vector."""
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.read.return_value = b'{"data":[{"embedding":[0.0]*1024}]}'
        mock_urlopen.return_value = mock_response
        yield mock_urlopen


# ─── Session messages fixtures ────────────────────────────────────────────

@pytest.fixture
def sample_messages():
    """Normal conversation messages — no corrections/failures."""
    return [
        {
            "role": "user",
            "content": "帮我查一下今天的天气",
        },
        {
            "role": "assistant",
            "content": "今天成都晴，气温18-26度",
        },
        {
            "role": "user",
            "content": "谢谢",
        },
    ]


@pytest.fixture
def sample_messages_with_correction():
    """Messages that include a user correction."""
    return [
        {
            "role": "user",
            "content": "帮我查一下今天的天气",
        },
        {
            "role": "assistant",
            "content": "今天成都晴",
        },
        {
            "role": "user",
            "content": "不对，我想要的是上海的天气",
        },
        {
            "role": "assistant",
            "content": "抱歉，上海今天多云，22-28度",
        },
    ]


@pytest.fixture
def sample_messages_with_tool_failure():
    """Messages that include tool failure patterns."""
    return [
        {
            "role": "user",
            "content": "运行测试",
        },
        {
            "role": "assistant",
            "content": "重试1次仍失败，工具调用失败",
        },
    ]


@pytest.fixture
def sample_messages_with_pause():
    """Messages that trigger pause/confirm patterns."""
    return [
        {
            "role": "user",
            "content": "帮我删除这个文件",
        },
        {
            "role": "assistant",
            "content": "需要我确认吗？这是一个删除操作。",
        },
        {
            "role": "user",
            "content": "先告诉我具体要删什么",
        },
    ]
