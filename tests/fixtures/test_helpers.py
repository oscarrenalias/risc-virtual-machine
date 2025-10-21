"""
Helper functions for testing
"""

def run_program_until_halt(vm, source, max_instructions=10000):
    """
    Load and run a program until it halts or reaches max instructions
    
    Args:
        vm: VirtualMachine instance
        source: Assembly source code
        max_instructions: Maximum instructions to execute
        
    Returns:
        Number of instructions executed
    """
    vm.load_program(source)
    return vm.run(max_instructions=max_instructions)


def run_and_get_register(vm, source, register, max_instructions=10000):
    """
    Run a program and return the value of a specific register
    
    Args:
        vm: VirtualMachine instance
        source: Assembly source code
        register: Register number or name
        max_instructions: Maximum instructions to execute
        
    Returns:
        Register value after execution
    """
    run_program_until_halt(vm, source, max_instructions)
    return vm.cpu.read_register(register)


def run_and_get_memory(vm, source, address, size=4, max_instructions=10000):
    """
    Run a program and return memory contents at an address
    
    Args:
        vm: VirtualMachine instance
        source: Assembly source code
        address: Memory address to read
        size: Number of bytes to read (1, 2, or 4)
        max_instructions: Maximum instructions to execute
        
    Returns:
        Memory value at address
    """
    run_program_until_halt(vm, source, max_instructions)
    if size == 1:
        return vm.memory.read_byte(address)
    elif size == 2:
        b0 = vm.memory.read_byte(address)
        b1 = vm.memory.read_byte(address + 1)
        return b0 | (b1 << 8)
    else:  # size == 4
        return vm.memory.read_word(address)


def assert_register_equals(cpu, reg, expected_value, message=None):
    """
    Assert that a register contains the expected value
    
    Args:
        cpu: CPU instance
        reg: Register number or name
        expected_value: Expected register value
        message: Optional error message
    """
    actual = cpu.read_register(reg)
    msg = message or f"Register {reg} should be 0x{expected_value:08X}, but was 0x{actual:08X}"
    assert actual == expected_value, msg


def assert_memory_contains(memory, address, expected_value, message=None):
    """
    Assert that memory contains the expected value
    
    Args:
        memory: Memory instance
        address: Memory address
        expected_value: Expected value (byte or word)
        message: Optional error message
    """
    if expected_value <= 0xFF:
        actual = memory.read_byte(address)
        msg = message or f"Memory[0x{address:08X}] should be 0x{expected_value:02X}, but was 0x{actual:02X}"
    else:
        actual = memory.read_word(address)
        msg = message or f"Memory[0x{address:08X}] should be 0x{expected_value:08X}, but was 0x{actual:08X}"
    assert actual == expected_value, msg


def assert_halted(cpu, message=None):
    """
    Assert that the CPU is in halted state
    
    Args:
        cpu: CPU instance
        message: Optional error message
    """
    msg = message or "CPU should be halted"
    assert cpu.halted, msg


def assert_not_halted(cpu, message=None):
    """
    Assert that the CPU is not in halted state
    
    Args:
        cpu: CPU instance
        message: Optional error message
    """
    msg = message or "CPU should not be halted"
    assert not cpu.halted, msg


def assert_interrupt_pending(cpu, interrupt_mask, message=None):
    """
    Assert that an interrupt is pending
    
    Args:
        cpu: CPU instance
        interrupt_mask: Interrupt mask bit to check
        message: Optional error message
    """
    mip = cpu.read_csr(cpu.CSR_MIP)
    msg = message or f"Interrupt 0x{interrupt_mask:02X} should be pending"
    assert (mip & interrupt_mask) != 0, msg


def assert_pc_equals(cpu, expected_pc, message=None):
    """
    Assert that PC has the expected value
    
    Args:
        cpu: CPU instance
        expected_pc: Expected PC value
        message: Optional error message
    """
    msg = message or f"PC should be 0x{expected_pc:08X}, but was 0x{cpu.pc:08X}"
    assert cpu.pc == expected_pc, msg


def build_program(*lines):
    """
    Build a program from instruction lines
    
    Args:
        *lines: Variable number of instruction strings
        
    Returns:
        Complete program as string
    """
    return "\n".join(lines)
