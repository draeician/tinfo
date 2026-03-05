import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: requires Ollama or Neo4j")


def pytest_collection_modifyitems(config, items):
    if config.getoption("-m", default=None):
        return
    skip_integration = pytest.mark.skip(reason="needs -m integration to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
