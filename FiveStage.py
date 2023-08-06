from Core import Core, State
from constants import OPCODE, R_TYPE, I_TYPE, S_TYPE, SB_TYPE, DEFAULT_OFFSET


def val(num):
    return int(num, 2)


def signed_val(num):
    if num[0] == "0":
        return int(num, 2)
    return -(-int(num, 2) & (2 ** len(num) - 1))


def int2bin(x, n_bits=32):
    bin_x = bin(x & (2**n_bits - 1))[2:]
    return "0" * (n_bits - len(bin_x)) + bin_x


class FiveStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(FiveStageCore, self).__init__(ioDir + "/FS_", imem, dmem)
        self.opFilePath = ioDir + "/StateResult_FS.txt"
        self.state.ID["nop"] = self.state.EX["nop"] = self.state.MEM[
            "nop"
        ] = self.state.WB["nop"] = 1

    def IF(self):
        self.nextState.IF["PC"] = self.state.IF["PC"]
        if (
            self.state.IF["nop"]
            or self.nextState.ID["nop"]
            or (self.nextState.is_hazard_nop and self.nextState.EX["nop"])
        ):
            return

        instr = self.ext_imem.readInstr(self.state.IF["PC"])
        if "".join(instr) == "1" * 32:
            self.nextState.IF["nop"] = 1
            self.nextState.ID["nop"] = 1
        else:
            self.nextState.ID["PC"] = self.state.IF["PC"]
            self.nextState.ID["Instr"] = instr
            self.nextState.IF["PC"] += 4

    def detect_hazard(self, rs):
        if rs == self.nextState.MEM["Wrt_reg_addr"] and self.nextState.MEM["rd_mem"] == 0:
            # ex to 1st
            return 2
        elif rs == self.nextState.WB["Wrt_reg_addr"] and self.nextState.WB["wrt_enable"]:
            # ex to 2nd
            return 1
        elif rs == self.nextState.MEM["Wrt_reg_addr"] and self.nextState.MEM["rd_mem"]:
            # mem to 1st
            self.nextState.is_hazard_nop = 1
            return -1
        return 0

    def read_forwarded_value(self, rs, signal):
        if signal == 1:
            return self.nextState.WB["Wrt_data"]
        elif signal == 2:
            return self.nextState.MEM["ALUresult"]
        else:
            return self.myRF.readRF(rs)

    def ID(self):
        if self.state.ID["nop"]:
            self.nextState.ID["nop"] = self.state.IF["nop"]
            return

        self.nextState.ID["nop"] = self.state.IF["nop"]
        opcode = self.state.ID["Instr"][3][-7:]
        funct3 = self.state.ID["Instr"][2][1:4]
        self.nextState.is_hazard_nop = 0
        self.nextState.EX["is_I_type"] = 0
        self.nextState.EX["rd_mem"] = 0
        self.nextState.EX["wrt_mem"] = 0
        self.nextState.EX["wrt_enable"] = 0
        self.nextState.EX["Wrt_reg_addr"] = "0"*6

        if opcode in OPCODE["R_TYPE"]:
            funct7 = self.state.ID["Instr"][0][:7]
            identifier = funct7 + funct3
            rd = self.state.ID["Instr"][2][4:] + self.state.ID["Instr"][3][0]
            rs = self.state.ID["Instr"][1][4:] + self.state.ID["Instr"][2][0]
            rt = self.state.ID["Instr"][0][-1] + self.state.ID["Instr"][1][:4]

            signal_rs = self.detect_hazard(rs)
            signal_rt = self.detect_hazard(rt)

            if self.nextState.is_hazard_nop:
                self.nextState.EX["nop"] = 1
                return

            self.nextState.EX["Rs"] = rs
            self.nextState.EX["Rt"] = rt
            self.nextState.EX["Wrt_reg_addr"] = rd
            self.nextState.EX["Read_data1"] = self.read_forwarded_value(rs, signal_rs)
            self.nextState.EX["Read_data2"] = self.read_forwarded_value(rt, signal_rt)
            self.nextState.EX["wrt_enable"] = 1

            if identifier == R_TYPE["ADD"]:
                self.nextState.EX["alu_op"] = "00"
            elif identifier == R_TYPE["SUB"]:
                self.nextState.EX["alu_op"] = "00"
                self.nextState.EX["Read_data2"] = int2bin(
                    -signed_val(self.nextState.EX["Read_data2"])
                )
            elif identifier == R_TYPE["AND"]:
                self.nextState.EX["alu_op"] = "01"
            elif identifier == R_TYPE["OR"]:
                self.nextState.EX["alu_op"] = "10"
            elif identifier == R_TYPE["XOR"]:
                self.nextState.EX["alu_op"] = "11"

        elif opcode in OPCODE["I_TYPE"]:
            identifier = funct3
            rd = self.state.ID["Instr"][2][4:] + self.state.ID["Instr"][3][0]
            rs = self.state.ID["Instr"][1][4:] + self.state.ID["Instr"][2][0]
            imm = (
                self.state.ID["Instr"][0][:7]
                + self.state.ID["Instr"][0][-1]
                + self.state.ID["Instr"][1][:4]
            )

            signal_rs = self.detect_hazard(rs)

            if self.nextState.is_hazard_nop:
                self.nextState.EX["nop"] = 1
                return

            self.nextState.EX["Rs"] = rs
            self.nextState.EX["Wrt_reg_addr"] = rd
            self.nextState.EX["Read_data1"] = self.read_forwarded_value(rs, signal_rs)
            self.nextState.EX["Imm"] = imm
            self.nextState.EX["wrt_enable"] = 1
            self.nextState.EX["is_I_type"] = 1

            if opcode == OPCODE["I_TYPE_LW"]:
                self.nextState.EX["alu_op"] = "00"
                self.nextState.EX["rd_mem"] = 1
            elif identifier == I_TYPE["ADDI"]:
                self.nextState.EX["alu_op"] = "00"
            elif identifier == I_TYPE["ANDI"]:
                self.nextState.EX["alu_op"] = "01"
            elif identifier == I_TYPE["ORI"]:
                self.nextState.EX["alu_op"] = "10"
            elif identifier == I_TYPE["XORI"]:
                self.nextState.EX["alu_op"] = "11"

        elif opcode in OPCODE["S_TYPE"]:
            rs = self.state.ID["Instr"][1][4:] + self.state.ID["Instr"][2][0]
            rt = self.state.ID["Instr"][0][-1] + self.state.ID["Instr"][1][:4]
            imm = (
                self.state.ID["Instr"][0][:7]
                + self.state.ID["Instr"][2][4:]
                + self.state.ID["Instr"][3][0]
            )

            signal_rs = self.detect_hazard(rs)
            signal_rt = self.detect_hazard(rt)

            if self.nextState.is_hazard_nop:
                self.nextState.EX["nop"] = 1
                return

            self.nextState.EX["Rs"] = rs
            self.nextState.EX["Rt"] = rt
            self.nextState.EX["Imm"] = imm
            self.nextState.EX["wrt_mem"] = 1
            self.nextState.EX["Read_data1"] = self.read_forwarded_value(rs, signal_rs)
            self.nextState.EX["Read_data2"] = self.read_forwarded_value(rt, signal_rt)

        elif opcode in OPCODE["SB_TYPE"]:
            rs = self.state.ID["Instr"][1][4:] + self.state.ID["Instr"][2][0]
            rt = self.state.ID["Instr"][0][-1] + self.state.ID["Instr"][1][:4]
            imm = (
                self.state.ID["Instr"][0][0]
                + self.state.ID["Instr"][3][0]
                + self.state.ID["Instr"][0][1:-1]
                + self.state.ID["Instr"][2][4:]
                + "0"
            )

            signal_rs = self.detect_hazard(rs)
            signal_rt = self.detect_hazard(rt)

            if self.nextState.is_hazard_nop:
                self.nextState.EX["nop"] = 1
                return

            self.nextState.EX["Rs"] = rs
            self.nextState.EX["Rt"] = rt
            self.nextState.EX["Imm"] = imm
            self.nextState.EX["wrt_mem"] = 0
            self.nextState.EX["Read_data1"] = self.read_forwarded_value(rs, signal_rs)
            self.nextState.EX["Read_data2"] = self.read_forwarded_value(rt, signal_rt)
            diff = signed_val(self.nextState.EX["Read_data1"]) - signed_val(
                self.nextState.EX["Read_data2"]
            )
            if (diff == 0 and funct3 == SB_TYPE["BEQ"]) or (
                diff != 0 and funct3 == SB_TYPE["BNE"]
            ):
                self.state.IF["PC"] = self.state.ID["PC"] + signed_val(self.nextState.EX["Imm"])
                self.nextState.ID["nop"] = 1
                self.nextState.EX["nop"] = 1
            else:
                self.nextState.EX["nop"] = 1

        elif opcode in OPCODE["UJ_TYPE"]:
            rd = self.state.ID["Instr"][2][4:] + self.state.ID["Instr"][3][0]
            imm = (
                self.state.ID["Instr"][0][0]
                + self.state.ID["Instr"][1][4:]
                + self.state.ID["Instr"][2][:4]
                + self.state.ID["Instr"][1][3]
                + self.state.ID["Instr"][0][1:]
                + self.state.ID["Instr"][1][:3]
                + "0"
            )
            self.nextState.EX["Imm"] = imm
            self.nextState.EX["Wrt_reg_addr"] = rd
            self.nextState.EX["Read_data1"] = int2bin(self.state.ID["PC"])
            self.nextState.EX["Read_data2"] = int2bin(4)
            self.nextState.EX["wrt_enable"] = 1
            self.nextState.EX["alu_op"] = "00"

            self.state.IF["PC"] = self.state.ID["PC"] + signed_val(imm)
            self.nextState.ID["nop"] = 1
        else:
            raise NotImplementedError(f"Unknown OPCODE encountered: {opcode}")

    def EX(self):
        if self.state.EX["nop"]:
            self.nextState.EX["nop"] = self.state.ID["nop"]
            return

        op1 = signed_val(self.state.EX["Read_data1"])
        op2 = signed_val(
            self.state.EX["Read_data2"]
            if not self.state.EX["is_I_type"] and not self.state.EX["wrt_mem"]
            else self.state.EX["Imm"]
        )

        if self.state.EX["alu_op"] == "00":
            self.nextState.MEM["ALUresult"] = int2bin(op1 + op2)
        elif self.state.EX["alu_op"] == "01":
            self.nextState.MEM["ALUresult"] = int2bin(op1 & op2)
        elif self.state.EX["alu_op"] == "10":
            self.nextState.MEM["ALUresult"] = int2bin(op1 | op2)
        elif self.state.EX["alu_op"] == "11":
            self.nextState.MEM["ALUresult"] = int2bin(op1 ^ op2)

        self.nextState.MEM["Rs"] = self.state.EX["Rt"]
        self.nextState.MEM["Rt"] = self.state.EX["Rt"]
        self.nextState.MEM["rd_mem"] = self.state.EX["rd_mem"]
        self.nextState.MEM["wrt_mem"] = self.state.EX["wrt_mem"]
        self.nextState.MEM["wrt_enable"] = self.state.EX["wrt_enable"]
        self.nextState.MEM["Wrt_reg_addr"] = self.state.EX["Wrt_reg_addr"]

        if self.state.EX["wrt_mem"]:
            self.nextState.MEM["Store_data"] = self.state.EX["Read_data2"]

        self.nextState.EX["nop"] = int(self.state.ID["nop"])

    def MEM(self):
        if self.state.MEM["nop"]:
            self.nextState.MEM["nop"] = self.state.EX["nop"]
            return

        if self.state.MEM["rd_mem"]:
            self.nextState.WB["Wrt_data"] = self.ext_dmem.readDataMem(
                signed_val(self.state.MEM["ALUresult"])
            )
        elif self.state.MEM["wrt_mem"]:
            self.ext_dmem.writeDataMem(
                signed_val(self.state.MEM["ALUresult"]), self.state.MEM["Store_data"]
            )
        else:
            self.nextState.WB["Wrt_data"] = self.state.MEM["ALUresult"]
            self.nextState.MEM["Store_data"] = self.state.MEM["ALUresult"]

        self.nextState.WB["wrt_enable"] = self.state.MEM["wrt_enable"]
        self.nextState.WB["Wrt_reg_addr"] = self.state.MEM["Wrt_reg_addr"]

        self.nextState.MEM["nop"] = self.state.EX["nop"]

    def WB(self):
        if self.state.WB["nop"]:
            self.nextState.WB["nop"] = self.state.MEM["nop"]
            return

        if self.state.WB["wrt_enable"]:
            self.myRF.writeRF(self.state.WB["Wrt_reg_addr"], self.state.WB["Wrt_data"])

        self.nextState.WB["nop"] = self.state.MEM["nop"]

    def step(self):
        """
        0    F D X M W
        1      F D . X M W
        2      . F . D X M W
        3        . . F D X M W
        4              F D X M W
        5                F D X M W

        """

        """
        0       F0 -- -- -- --   [0,-1,-2,-3,-4] [1, 0,-1,-2,-3]
        1       F1 D0 -- -- --   [1, 0,-1,-2,-3] [2, 1, 0,-1,-2]
        2       F2 D1 X0 -- --   [2, 1, 0,-1,-2] [3, 2, 1, 0,-1]
        3       -- -- -- M0 --   [3, 2, 1, 0,-1] [3, 2, 1, 1, 0]
        4       F3 D2 X1 -- W0   [3, 2, 1, 1, 0] [4, 3, 2, 1, 1]
        5       F4 D3 X2 M1 --   [4, 3, 2, 1, 1] [5, 4, 3, 2, 1]

        """

        """
        0 lw    F D X M W
        1 ad      F D . X M W
        2 lw        F . D X M W
        3 ad          . F D . X M W
        4 lw              F . D X M W
        5 ad                . F D . X M W
        6 lw                    F . D X M W
        7 ad                      . F D . X M W
        8 lw                          F . D X M W
        9 ad                            . F D . X M W
        """
        # print("#CYCLE:", self.cycle)
        if (
            self.state.IF["nop"]
            and self.state.ID["nop"]
            and self.state.EX["nop"]
            and self.state.MEM["nop"]
            and self.state.WB["nop"]
        ):
            self.halted = True

        self.WB()
        self.MEM()
        self.EX()
        self.ID()
        self.IF()

        self.myRF.outputRF(self.cycle)  # dump RF
        self.printState(
            self.nextState, self.cycle
        )  # print states after executing cycle 0, cycle 1, cycle 2 ...
        # The end of the cycle and updates the current state with the values calculated in this cycle
        import copy

        self.state = copy.deepcopy(self.nextState)
        self.cycle += 1

    def printState(self, state, cycle):
        printstate = [
            "-" * 70 + "\n",
            "State after executing cycle: " + str(cycle) + "\n",
        ]
        printstate.extend(
            ["IF." + key + ": " + str(val) + "\n" for key, val in state.IF.items()]
        )
        printstate.extend(
            ["ID." + key + ": " + str(val) + "\n" for key, val in state.ID.items()]
        )
        printstate.extend(
            ["EX." + key + ": " + str(val) + "\n" for key, val in state.EX.items()]
        )
        printstate.extend(
            ["MEM." + key + ": " + str(val) + "\n" for key, val in state.MEM.items()]
        )
        printstate.extend(
            ["WB." + key + ": " + str(val) + "\n" for key, val in state.WB.items()]
        )
        # print(self.myRF.Registers)
        if cycle == 0:
            perm = "w"
        else:
            perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)
