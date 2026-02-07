import pytest


def pytest_terminal_summary():
    import os
    if os.path.exists('temp'):
        os.remove('temp')
