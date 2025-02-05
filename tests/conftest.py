import pytest
from typing import Any

def pytest_configure(config: Any) -> None:
    """配置 pytest"""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test"
    ) 