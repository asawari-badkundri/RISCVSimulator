from Core import Core, State
from InstructionParser import execute_instruction
from constants import DEFAULT_OFFSET


def int2bin(x, n_bits=32):
    bin_x = bin(x & (2**n_bits - 1))[2:]
    return "0" * (n_bits - len(bin_x)) + bin_x

class SingleStageCore(Core):

    def __init__(self, ioDir, imem, dmem):
        super(SingleStageCore, self).__init__(ioDir + "/SS_", imem, dmem)
        self.opFilePath = ioDir + "/StateResult_SS.txt"

    def step(self):
        # IF
        instruction = self.ext_imem.readInstr(self.state.IF["PC"])

        if self.state.IF["nop"] or len(instruction) == 0:
            self.halted = True
            return

        register_contents = self.myRF.Registers

        # ID & EX
        result = execute_instruction(instruction, register_contents, self.ext_dmem)
        if result:
            if result["operation"] == "LW":
                if result["rd"] != 0:
                    register_contents[result["rd"]] = int2bin(int(
                        ''.join(self.ext_dmem.DMem[result["value"]: result["value"] + 4]), 2))
            elif result["operation"] == "SW":
                _32b = '{:032b}'.format(result["value"])
                for i in range(4):
                    self.ext_dmem.DMem[result["memory_location"] + i] = _32b[8 * i: 8 * (i + 1)]
            elif result["operation"] in ["BEQ", "BNE"]:
                if result["offset"] != 4:
                    print("+1")
                pass
                # if result.get("value"):
                #     self.nextState.IF["PC"] = result.get("offset") - 4
            elif result["operation"] == "JAL":
                if result["rd"] != 0:
                    register_contents[result["rd"]] = int2bin(self.state.IF["PC"] + 4)
            else:
                if result["rd"] != 0:
                    register_contents[result["rd"]] = int2bin(result["value"])
                    # self.myRF.writeRF(result["rd"], result["value"])
            self.nextState.IF["PC"] = self.state.IF["PC"] + result.get("offset", DEFAULT_OFFSET)
        else:
            self.halted = True
            self.nextState.IF["PC"] = self.state.IF["PC"] 
            self.nextState.IF["nop"] = 1

        self.myRF.outputRF(self.cycle)  # dump RF
        self.printState(self.nextState, self.cycle)  # print states after executing cycle 0, cycle 1, cycle 2 ...

        if self.halted:
            self.cycle += 1
            self.myRF.outputRF(self.cycle)  # dump RF
            self.printState(self.nextState, self.cycle)  # print states after executing cycle 0, cycle 1, cycle 2 ...

        # The end of the cycle and updates the current state with the values calculated in this cycle
        nextState = self.nextState
        self.state = nextState
        self.nextState = State()
        self.cycle += 1


    def printState(self, state, cycle):
        print_state = [
            "-" * 70 + "\n", "State after executing cycle: " + str(cycle) + "\n",
            "IF.PC: " + str(state.IF["PC"]) + "\n",
            "IF.nop: " + str(state.IF["nop"]) + "\n"
        ]
        #print(self.myRF.Registers)
        if cycle == 0:
            perm = "w"
        else:
            perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(print_state)