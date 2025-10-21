# Supported Instruction set

### Arithmetic (R-type)
- `ADD rd, rs1, rs2` - Add
- `SUB rd, rs1, rs2` - Subtract
- `SLT rd, rs1, rs2` - Set less than (signed)
- `SLTU rd, rs1, rs2` - Set less than (unsigned)

### M-Extension: Multiply/Divide (R-type)
- `MUL rd, rs1, rs2` - Multiply (lower 32 bits)
- `DIV rd, rs1, rs2` - Divide (signed, rounds toward zero)
- `DIVU rd, rs1, rs2` - Divide (unsigned)
- `REM rd, rs1, rs2` - Remainder (signed, sign matches dividend)
- `REMU rd, rs1, rs2` - Remainder (unsigned)

**Note:** The following M-extension instructions are **not yet supported**:
- `MULH rd, rs1, rs2` - Multiply high (signed × signed, upper 32 bits)
- `MULHSU rd, rs1, rs2` - Multiply high (signed × unsigned, upper 32 bits)
- `MULHU rd, rs1, rs2` - Multiply high (unsigned × unsigned, upper 32 bits)

### Arithmetic Immediate (I-type)
- `ADDI rd, rs1, imm` - Add immediate
- `SLTI rd, rs1, imm` - Set less than immediate
- `SLTIU rd, rs1, imm` - Set less than immediate unsigned

### Logical (R-type)
- `AND rd, rs1, rs2` - Bitwise AND
- `OR rd, rs1, rs2` - Bitwise OR
- `XOR rd, rs1, rs2` - Bitwise XOR

### Logical Immediate (I-type)
- `ANDI rd, rs1, imm` - AND immediate
- `ORI rd, rs1, imm` - OR immediate
- `XORI rd, rs1, imm` - XOR immediate

### Shift (R-type)
- `SLL rd, rs1, rs2` - Shift left logical
- `SRL rd, rs1, rs2` - Shift right logical
- `SRA rd, rs1, rs2` - Shift right arithmetic

### Shift Immediate (I-type)
- `SLLI rd, rs1, shamt` - Shift left logical immediate
- `SRLI rd, rs1, shamt` - Shift right logical immediate
- `SRAI rd, rs1, shamt` - Shift right arithmetic immediate

### Memory Load (I-type)
- `LW rd, offset(rs1)` - Load word
- `LH rd, offset(rs1)` - Load halfword
- `LB rd, offset(rs1)` - Load byte
- `LHU rd, offset(rs1)` - Load halfword unsigned
- `LBU rd, offset(rs1)` - Load byte unsigned

### Memory Store (S-type)
- `SW rs2, offset(rs1)` - Store word
- `SH rs2, offset(rs1)` - Store halfword
- `SB rs2, offset(rs1)` - Store byte

### Branch (B-type)
- `BEQ rs1, rs2, label` - Branch if equal
- `BNE rs1, rs2, label` - Branch if not equal
- `BLT rs1, rs2, label` - Branch if less than
- `BGE rs1, rs2, label` - Branch if greater or equal
- `BLTU rs1, rs2, label` - Branch if less than unsigned
- `BGEU rs1, rs2, label` - Branch if greater or equal unsigned

### Jump (J-type)
- `JAL rd, label` - Jump and link
- `JALR rd, rs1, offset` - Jump and link register

### Upper Immediate (U-type)
- `LUI rd, imm` - Load upper immediate
- `AUIPC rd, imm` - Add upper immediate to PC

### Control and Status Registers (CSR)
- `CSRRW rd, csr, rs1` - Atomic Read/Write CSR
- `CSRRS rd, csr, rs1` - Atomic Read and Set Bits in CSR
- `CSRRC rd, csr, rs1` - Atomic Read and Clear Bits in CSR
- `CSRRWI rd, csr, imm` - Read/Write CSR, immediate
- `CSRRSI rd, csr, imm` - Read and Set Bits in CSR, immediate
- `CSRRCI rd, csr, imm` - Read and Clear Bits in CSR, immediate

### System
- `HALT` - Halt execution
- `MRET` - Return from interrupt/exception
- `NOP` - No operation