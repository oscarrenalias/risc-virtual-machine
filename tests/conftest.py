"""
pytest configuration and shared fixtures
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.cpu import CPU
from src.memory import Memory
from src.display import Display
from src.timer import Timer
from src.realtime_timer import RealTimeTimer
from src.vm import VirtualMachine
from src.assembler import Assembler


@pytest.fixture
def cpu():
    """Create a fresh CPU instance"""
    return CPU()


@pytest.fixture
def memory():
    """Create a fresh Memory instance"""
    return Memory()


@pytest.fixture
def display():
    """Create a fresh Display instance"""
    return Display()


@pytest.fixture
def timer():
    """Create a fresh Timer instance"""
    return Timer()


@pytest.fixture
def rt_timer():
    """Create a fresh RealTimeTimer instance"""
    return RealTimeTimer()


@pytest.fixture
def assembler():
    """Create a fresh Assembler instance"""
    return Assembler()


@pytest.fixture
def vm():
    """Create a fresh VirtualMachine instance"""
    return VirtualMachine(debug=False)


@pytest.fixture
def vm_debug():
    """Create a fresh VirtualMachine instance with debug enabled"""
    return VirtualMachine(debug=True)


@pytest.fixture
def vm_protected():
    """Create a fresh VirtualMachine instance with text segment protection"""
    return VirtualMachine(debug=False, protect_text=True)
