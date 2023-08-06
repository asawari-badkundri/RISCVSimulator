from constants import OPCODE, R_TYPE, I_TYPE, S_TYPE, SB_TYPE, DEFAULT_OFFSET


def val(num):
    return int(num, 2)

def signed_val(num):
    if num[0] == '0':
        return int(num, 2)
    return -(-int(num, 2) & (2 ** len(num) - 1))


def execute_RType(instruction, register_contents):
    funct7 = instruction[0][:7]
    funct3 = instruction[2][1:4]
    rd = instruction[2][4:] + instruction[3][0]
    rs1 = instruction[1][4:] + instruction[2][0]
    rs2 = instruction[0][-1] + instruction[1][0:4]

    identifier = funct7 + funct3

    # ADD
    if identifier == R_TYPE["ADD"]:
        # add x7 x8 x9
        print(f"add x{val(rd)} x{val(rs1)} x{val(rs2)}")
        return {
            "InstructionString": f"add x{val(rd)} x{val(rs1)} x{val(rs2)}",
            "Read_data1": register_contents[val(rs1)],
            "Read_data2": register_contents[val(rs2)],
            "rs1": val(rs1),
            "rs2": val(rs2),
            "rd": val(rd),
            "value": int(register_contents[val(rs1)], 2) + int(register_contents[val(rs2)], 2),
            "operation": "ADD",
            "instruction_type": "R"
        }

    # SUB
    if identifier == R_TYPE["SUB"]:
        print(f"sub x{val(rd)} x{val(rs1)} x{val(rs2)}")
        return {            
            "InstructionString": f"sub x{val(rd)} x{val(rs1)} x{val(rs2)}",
            "Read_data1": register_contents[val(rs1)],
            "Read_data2": register_contents[val(rs2)],
            "rs1": val(rs1),
            "rs2": val(rs2),
            "rd": val(rd),
            "value": int(register_contents[val(rs1)], 2) - int(register_contents[val(rs2)], 2),
            "operation": "SUB",
            "instruction_type": "R"
        }

    # XOR
    if identifier == R_TYPE["XOR"]:
        print(f"xor x{val(rd)} x{val(rs1)} x{val(rs2)}")
        return {
            "InstructionString": f"xor x{val(rd)} x{val(rs1)} x{val(rs2)}",
            "Read_data1": register_contents[val(rs1)],
            "Read_data2": register_contents[val(rs2)],
            "rs1": val(rs1),
            "rs2": val(rs2),
            "rd": val(rd),
            "value": int(register_contents[val(rs1)], 2) ^ int(register_contents[val(rs2)], 2),
            "operation": "XOR",
            "instruction_type": "R"
        }

    # OR
    if identifier == R_TYPE["OR"]:
        print(f"or x{val(rd)} x{val(rs1)} x{val(rs2)}")
        return {
            "InstructionString": f"or x{val(rd)} x{val(rs1)} x{val(rs2)}",
            "Read_data1": register_contents[val(rs1)],
            "Read_data2": register_contents[val(rs2)],
            "rs1": val(rs1),
            "rs2": val(rs2),
            "rd": val(rd),
            "value": int(register_contents[val(rs1)], 2) | int(register_contents[val(rs2)], 2),
            "operation": "OR",
            "instruction_type": "R"
        }

    # AND
    if identifier == R_TYPE["AND"]:
        print(f"and x{val(rd)} x{val(rs1)} x{val(rs2)}")
        return {
            "InstructionString": f"and x{val(rd)} x{val(rs1)} x{val(rs2)}",
            "Read_data1": register_contents[val(rs1)],
            "Read_data2": register_contents[val(rs2)],
            "rs1": val(rs1),
            "rs2": val(rs2),
            "rd": val(rd),
            "value": int(register_contents[val(rs1)], 2) & int(register_contents[val(rs2)], 2),
            "operation": "AND",
            "instruction_type": "R"
        }


def execute_IType(instruction, register_contents):
    opcode = instruction[3][-7:]
    funct3 = instruction[2][1:4]
    imm = instruction[0][:7] + instruction[0][-1] + instruction[1][0:4]
    rd = instruction[2][4:] + instruction[3][0]
    rs1 = instruction[1][4:] + instruction[2][0]

    identifier = funct3

    # LW
    if opcode == OPCODE["I_TYPE_LW"]:
        print(f'lw x{val(rd)} {val(imm)}(x{val(rs1)})')
        assert identifier == I_TYPE["LW"]
        assert (val(imm) + int(register_contents[val(rs1)], 2)) % 4 == 0, \
            f"Loading from non-aligned word: {val(imm) + int(register_contents[val(rs1)], 2)}"
        return {
            "InstructionString": f'lw x{val(rd)} {val(imm)}(x{val(rs1)})',
            "Read_data1": register_contents[val(rs1)],
            "Read_data2": 0,
            "immediate": val(imm),
            "rs1": val(rs1),
            "rd": val(rd),
            "value": val(imm) + int(register_contents[val(rs1)], 2),
            "operation": "LW",
            "instruction_type": "I"
        }

    # ADDI
    if identifier == I_TYPE["ADDI"]:
        print(f'addi x{val(rd)} x{val(rs1)} {signed_val(imm)}')
        return {
            "InstructionString": f'addi x{val(rd)} x{val(rs1)} {signed_val(imm)}',
            "Read_data1": register_contents[val(rs1)],
            "Read_data2": 0,
            "immediate": signed_val(imm),
            "rs1": val(rs1),
            "rd": val(rd),
            "value": int(register_contents[val(rs1)], 2) + signed_val(imm),
            "operation": "ADDI",
            "instruction_type": "I"
        }

    # XORI
    if identifier == I_TYPE["XORI"]:
        print(f'xori x{val(rd)} x{val(rs1)} {signed_val(imm)}')
        return {
            "InstructionString": f'xori x{val(rd)} x{val(rs1)} {signed_val(imm)}',
            "Read_data1": register_contents[val(rs1)],
            "Read_data2": 0,
            "immediate": signed_val(imm),
            "rs1": val(rs1),
            "rd": val(rd),
            "value": int(register_contents[val(rs1)], 2) ^ signed_val(imm),
            "operation": "XORI",
            "instruction_type": "I"
        }

    # ANDI
    if identifier == I_TYPE["ANDI"]:
        print(f'andi x{val(rd)} x{val(rs1)} {signed_val(imm)}')
        return {
            "InstructionString": f'andi x{val(rd)} x{val(rs1)} {signed_val(imm)}',
            "Read_data1": register_contents[val(rs1)],
            "Read_data2": 0,
            "immediate": signed_val(imm),
            "rs1": val(rs1),
            "rd": val(rd),
            "value": int(register_contents[val(rs1)], 2) & signed_val(imm),
            "operation": "ANDI",
            "instruction_type": "I"
        }

    # ORI
    if identifier == I_TYPE["ORI"]:
        print(f'ori x{val(rd)} x{val(rs1)} {signed_val(imm)}')
        return {
            "InstructionString": f'ori x{val(rd)} x{val(rs1)} {signed_val(imm)}',
            "Read_data1": register_contents[val(rs1)],
            "Read_data2": 0,
            "immediate": signed_val(imm),
            "rs1": val(rs1),
            "rd": val(rd),
            "value": int(register_contents[val(rs1)], 2) | signed_val(imm),
            "operation": "ORI",
            "instruction_type": "I"
        }


def execute_SType(instruction, register_contents):
    funct3 = instruction[2][1:4]
    imm = instruction[0][:7] + instruction[2][4:] + instruction[3][0]
    rs1 = instruction[1][4:] + instruction[2][0]
    rs2 = instruction[0][-1] + instruction[1][0:4]

    assert funct3 == S_TYPE["SW"], f"Incorrect funct3 received for S-type instruction: {funct3}." \
                                   f" Supported funct3 values: '{S_TYPE['SW']}'"

    print(f"sw x{val(rs2)} {val(imm)}(x{val(rs1)})")
    return {
        "InstructionString": f"sw x{val(rs2)} {val(imm)}(x{val(rs1)})",
        "Read_data1": register_contents[val(rs1)],
        "Read_data2": register_contents[val(rs2)],
        "immediate": val(imm),
        "rs1": val(rs1), # destination
        "rs2": val(rs2), # source
        "memory_location": val(imm) + int(register_contents[val(rs1)], 2),
        "value": int(register_contents[val(rs2)], 2),
        "operation": "SW"
    }


def execute_UJType(instruction, register_contents):
    imm = instruction[0][0] + instruction[1][4:] + instruction[2][:4] + instruction[1][3] + instruction[0][1:] + \
          instruction[1][:3] + '0'
    rd = instruction[2][4:] + instruction[3][0]
    funct3 = instruction[2][1:4]
    opcode = instruction[3][1:]
    print(f"jal x{val(rd)} {signed_val(imm)}")
    return {
        "InstructionString": f"jal x{val(rd)} {signed_val(imm)}",
        "rd": val(rd),
        "offset": signed_val(imm),
        "operation": "JAL"
    }


def execute_SBType(instruction, register_contents):
    imm11 = instruction[0][0] + instruction[3][0] + instruction[0][1:-1] + instruction[2][4:]
    sign_ext_imm = instruction[0][0] * 20 + instruction[3][0] + instruction[0][1:-1] + instruction[2][4:] + '0'
    rs2 = instruction[0][-1] + instruction[1][0:4]
    rs1 = instruction[1][4:] + instruction[2][0]
    funct3 = instruction[2][1:4]
    opcode = instruction[3][1:]
    # BEQ
    if funct3 == SB_TYPE["BEQ"]:
        print(f"beq x{val(rs1)} x{val(rs2)} {signed_val(sign_ext_imm)}")
        branch_to_offset = register_contents[val(rs1)] == register_contents[val(rs2)]
        return {
            "InstructionString": f"beq x{val(rs1)} x{val(rs2)} {signed_val(sign_ext_imm)}",
            "Read_data1": register_contents[val(rs1)],
            "Read_data2": register_contents[val(rs2)],
            "rs1": val(rs1), 
            "rs2": val(rs2), 
            "offset": signed_val(sign_ext_imm) if branch_to_offset else DEFAULT_OFFSET,
            "value": branch_to_offset,
            "operation": "BEQ"
        }

    # BNE
    if funct3 == SB_TYPE["BNE"]:
        print(f"bne x{val(rs1)} x{val(rs2)} {signed_val(sign_ext_imm)}")
        branch_to_offset = register_contents[val(rs1)] != register_contents[val(rs2)]
        return {
            "InstructionString": f"bne x{val(rs1)} x{val(rs2)} {signed_val(sign_ext_imm)}",
            "Read_data1": register_contents[val(rs1)],
            "Read_data2": register_contents[val(rs2)],
            "rs1": val(rs1), 
            "rs2": val(rs2), 
            "offset": signed_val(sign_ext_imm) if branch_to_offset else DEFAULT_OFFSET,
            "value": branch_to_offset,
            "operation": "BNE"
        }


def execute_instruction(instruction, register_contents, data_memory):
    """
    Parses the instruction according to the OPCODE
    :param instruction: holds an array of 4 bytes from IMem
    :param register_contents: contains the values in the registers
    :param data_memory: contents of the DMem file
    :return: an object that defines what needs to be done in the CPU
    """
    opcode = instruction[3][-7:]
    if opcode in OPCODE["R_TYPE"]:
        return execute_RType(instruction, register_contents)
    elif opcode in OPCODE["I_TYPE"]:
        return execute_IType(instruction, register_contents)
    elif opcode in OPCODE["S_TYPE"]:
        return execute_SType(instruction, register_contents)
    elif opcode in OPCODE["SB_TYPE"]:
        return execute_SBType(instruction, register_contents)
    elif opcode in OPCODE["UJ_TYPE"]:
        return execute_UJType(instruction, register_contents)
    elif opcode in OPCODE["HALT"]:
        return 
    else:
        raise NotImplementedError(f"Unknown OPCODE encountered: {opcode}")
