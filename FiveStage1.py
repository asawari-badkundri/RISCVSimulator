
from Core import Core, State
from InstructionParser import execute_instruction
from constants import DEFAULT_OFFSET, I_TYPE
import pprint


class FiveStageCore(Core):

    def __init__(self, ioDir, imem, dmem):
        super(FiveStageCore, self).__init__(ioDir + "/FS_", imem, dmem)
        self.instruction_queue = []
        self.stage_pointer = { "IF": 1, "ID": 0, "EX": -1, "MEM": -2, "WB": -3 }
        self.output_state = {}
        self.output_state["IF"] = {"NOP": 0, "PC": 0}
        self.output_state["ID"] = {"NOP": 0, "Instr": 0}
        self.output_state["EX"] = {"NOP": 0, "Read_data1": 0, "Read_data2": 0, "Imm": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0,
                                    "is_I_type": False, "rd_mem": 0,
                                    "wrt_mem": 0, "alu_op": 0, "wrt_enable": 0}
        self.output_state["MEM"] = {"NOP": 0, "ALUresult": 0, "Store_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "rd_mem": 0,
                                    "wrt_mem": 0, "wrt_enable": 0}
        self.output_state["WB"] = {"NOP": 0, "Wrt_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "wrt_enable": 0}
        self.previous_stage_dest_reg = None
        self.opFilePath = ioDir + "/StateResult_FS.txt"


    def ptr(self, string, val=None):
        if val == None:
            return self.stage_pointer[string]
        self.stage_pointer[string] += val
        return self.stage_pointer[string]


    def get_WB(result, cycle_count):
        return {
            "VAL": cycle_count,
            "Wrt_data": 0,  # data to be written (or data read in load)
            "Rs": 0, 
            "Rt": 0, 
            "Wrt_reg_addr": 0, 
            "wrt_enable": 0
        }

    def get_MEM(result, cycle_count):
        return {
            "VAL": cycle_count,
            # change
            "ALUResult": result.get("memory_location"), # offset or output of ALU
            "Store_data": result.get("value") if result.get("operation") == "SW" else None,
            "Rs": result.get("rs1"), # rs
            "Rt": result.get("rs2"), # rt
            "Wrt_reg_addr": result.get("rd"), # rd
            "rd_mem": result.get("operation") == "LW",
            "wrt_mem": result.get("operation") == "SW", 
            "wrt_enable": True if result.get("instruction_type") in ["R", "I"] else False
        }
    
    def get_EX(result, cycle_count):
        return {
            "VAL": cycle_count,
            "Read_data1": result.get("Read_data1"), # rs
            "Read_data2": result.get("Read_data2"), # rt
            "Rs": result.get("rs1"), # rs
            "Rt": result.get("rs2"), # rt
            "Imm": result.get("immediate"),
            "ALUResult": result.get("value"),
            "Wrt_reg_addr": result.get("rd"),
            "alu_op": None, # TODO
            "rd_mem": result.get("operation") == "LW",
            "wrt_mem": result.get("operation") == "SW",
            "wrt_enable": True if result.get("instruction_type") in ["R", "I"] else False,
            "is_I_type": result.get("operation") in I_TYPE
        }

    def get_ID(instruction, cycle_count):
        return  {
            "VAL": cycle_count,
            "Instr": ''.join(instruction)
        }
    
    def get_IF(pc, nextPc, cycle_count):
        return {
            "VAL": cycle_count,
            "PC": pc,
            "NextPC": nextPc
        }



    def outputContents(self):

        # handle edge cases + NOP
        cycleCount = -1
        while self.ptr("WB") < len(self.instruction_queue):
            cycleCount += 1
            for key in self.output_state:
                self.output_state[key]["NOP"] = 1

            # peform WB
            if self.ptr("WB") >= 0 and self.ptr("WB") < len(self.instruction_queue):
                if self.ptr("WB") < self.ptr("MEM"):
                    self.output_state["WB"] = self.instruction_queue[self.ptr("WB")]["WB"]
                    self.output_state["WB"]["NOP"] = 0
                else:
                    self.ptr("WB", -1)
            self.ptr("WB", 1)


            # perform MEM
            if self.ptr("MEM") >= 0 and self.ptr("MEM") < len(self.instruction_queue):
                if self.ptr("MEM") < self.ptr("EX"):
                    self.output_state["MEM"] = self.instruction_queue[self.ptr("MEM")]["MEM"]
                    self.output_state["MEM"]["NOP"] = 0
                else:
                    self.ptr("MEM", -1)
            self.ptr("MEM", 1)

            # perform EX 
            # If NOP occurs, stop execution of EX, ID and IF
            if self.ptr("EX") >= 0 and self.ptr("EX") < len(self.instruction_queue) and self.ptr("EX") < self.ptr("ID"):
                if self.instruction_queue[self.ptr("EX")]["NOP"]:
                    self.instruction_queue[self.ptr("EX")]["NOP"] = False
                    print("Cycle", cycleCount)
                    # pprint.pprint(self.output_state)
                    self.printState(self.output_state, cycleCount)
                    continue
                else:
                    self.output_state["EX"] = self.instruction_queue[self.ptr("EX")]["EX"]
                    self.output_state["EX"]["NOP"] = 0
            self.ptr("EX", 1)

            # perform ID
            if self.ptr("ID") >= 0 and self.ptr("ID") < len(self.instruction_queue) and self.ptr("ID") < self.ptr("IF"):
                self.output_state["ID"] = self.instruction_queue[self.ptr("ID")]["ID"]
                self.output_state["ID"]["NOP"] = 0
            self.ptr("ID", 1)

            # perform IF
            if self.ptr("IF") >= 0 and self.ptr("IF") < len(self.instruction_queue) :
                self.output_state["IF"] = self.instruction_queue[self.ptr("IF")]["IF"]
                self.output_state["IF"]["NOP"] = 0
            self.ptr("IF", 1)

        
            print("Cycle", cycleCount)
            # pprint.pprint(self.output_state)
            self.printState(self.output_state, cycleCount)

        self.output_state["WB"]["NOP"] = 1
        self.printState(self.output_state, cycleCount + 1)
        self.printState(self.output_state, cycleCount + 2)




    def printState(self, state, cycle):
        print_state = ["-" * 70 + "\n", "State after executing cycle: " + str(cycle) + "\n"]
        for instr_stage in ["IF", "ID", "EX", "MEM", "WB"]:
            for key, val in state[instr_stage].items():
                if key in ['Instr', 'Read_data1', 'Read_data2', 'ALUResult', 'Store_data', 'Wrt_data'] and val != None:
                    if key == 'Instr':
                        val = int(val, 2)
                    val = int(val)
                    val = '{:032b}'.format(val & 4294967295)
                elif key in ['rd', 'rs1', 'rs2', 'Wrt_reg_addr'] and val != None:
                    val = int(val)
                    val = '{:05b}'.format(val)
                elif key == 'AluOperation' and val != None:
                    val = int(val)
                    val = '{:02b}'.format(val)
                print_state.extend(
                    [instr_stage + "." + key + ": " + str(val) + "\n"])
            print_state.extend(["\n\n"])

        if cycle == 0:
            perm = "w"
        else:
            perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(print_state)


    def step(self):

        result, instruction, NOP = self.execute_instructions() 

        state_params = {}

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

        """
            print if index > 0 and increase immediately
            Check for NOP during EX and skip EX, ID, IF: decrease value of EX, ID and IF
            if currentIndex < nextIndex: print
        """

        if result:

            # if result.get("offset", 4) != 4:
            #     self.instruction_queue.append({
            #         "IF": {
            #             "VAL": self.cycle + 0.5,
            #             "PC": self.state.IF["PC"],
            #             "NextPC": self.state.IF["PC"] + 4
            #         },
            #         "ID": {
            #             "VAL": self.cycle + 0.5,
            #             "NOP": True
            #         },
            #         "EX": {
            #             "VAL": self.cycle + 0.5,
            #             "NOP": True
            #         },
            #         "MEM": {
            #             "VAL": self.cycle + 0.5,
            #             "NOP": True
            #         },
            #         "WB": {
            #             "VAL": self.cycle + 0.5,
            #             "NOP": True
            #         },
            #         "NOP": False
            #     })

            state_params = {
                "IF": {
                    "VAL": self.cycle,
                    "PC": result["PC"],
                    "NextPC": result["NextPC"],
                    "InstructionString": result.get("InstructionString")
                },
                "ID": {
                    "VAL": self.cycle,
                    "Instr": ''.join(instruction),
                    "InstructionString": result.get("InstructionString")
                },
                "EX": {
                    "VAL": self.cycle,
                    "Read_data1": result.get("Read_data1"), # rs
                    "Read_data2": result.get("immediate") if result.get("load_wrt") else result.get("Read_data2"), # rt
                    "Rs": result.get("rs1"), # rs
                    "Rt": result.get("rs2"), # rt
                    "Imm": result.get("immediate"),
                    "ALUResult": result.get("value"),
                    "Wrt_reg_addr": result.get("rd"),
                    "alu_op": None, # TODO
                    "rd_mem": result.get("operation") == "LW",
                    "wrt_mem": result.get("operation") == "SW",
                    "wrt_enable": True if result.get("instruction_type") in ["R", "I"] else False,
                    "is_I_type": result.get("operation") in I_TYPE,
                    "InstructionString": result.get("InstructionString")
                },
                "MEM": {
                    "VAL": self.cycle,
                    # change
                    # TODO 
                    "ALUresult": 
                        result.get("immediate") 
                        if result.get("load_wrt") 
                        else result.get("value") 
                        if result.get("instruction_type") in ["R", "I"] 
                        else result.get("memory_location"), # offset or output of ALU
                    "Store_data": result.get("value") if result.get("operation") == "SW" else None,
                    "Rs": result.get("rs1"), # rs
                    "Rt": result.get("rs2"), # rt
                    "Wrt_reg_addr": result.get("rd"), # rd
                    "rd_mem": result.get("operation") == "LW",
                    "wrt_mem": result.get("operation") == "SW", 
                    "wrt_enable": True if result.get("instruction_type") in ["R", "I"] else False,
                    "InstructionString": result.get("InstructionString")
                },
                "WB": {
                    "VAL": self.cycle,
                    "Wrt_data": result.get("load_wrt") or (result.get("value") if result.get("instruction_type") in ["R", "I"] else None),  # data to be written (or data read in load)
                    "Rs": result.get("rs1"), # rs
                    "Rt": result.get("rs2"), # rt
                    "Wrt_reg_addr": result.get("rd"), 
                    "wrt_enable": True if result.get("instruction_type") in ["R", "I"] else False,
                    "InstructionString": result.get("InstructionString")
                },
                "NOP": NOP,
                "InstructionString": result.get("InstructionString")
            }

        if len(state_params) > 0:
            self.instruction_queue.append(state_params)

        if self.state.IF["nop"] and self.state.ID["nop"] and self.state.EX["nop"] and self.state.MEM["nop"] and \
                self.state.WB["nop"]:
            self.halted = True

        # self.halted = False

        self.myRF.outputRF(self.cycle)  # dump RF
        # self.printState(self.state, self.cycle)  # print states after executing cycle 0, cycle 1, cycle 2 ...

        # The end of the cycle and updates the current state with the values calculated in this cycle
        nextState = self.nextState
        self.state = nextState
        self.nextState = State()
        self.cycle += 1


    def execute_instructions(self):

        instruction = self.ext_imem.readInstr(self.state.IF["PC"])

        if self.state.IF["nop"] or len(instruction) == 0:
            self.halted = True
            return

        NOP = False

        register_contents = self.myRF.Registers

        result = execute_instruction(instruction, register_contents, self.ext_dmem)
        if result:
            if result["operation"] == "LW":
                # detected nop hazard
                self.previous_stage_dest_reg = result["rd"]
                register_contents[result["rd"]] = int(
                    ''.join(self.ext_dmem.DMem[result["value"]: result["value"] + 4]), 2)
                result["load_wrt"] = register_contents[result["rd"]]
                pass
            elif result["operation"] == "SW":
                # MEM to 1st hazard
                if self.previous_stage_dest_reg and result["rs1"] == self.previous_stage_dest_reg:
                    NOP = True
                    self.previous_stage_dest_reg = None
                _32b = '{:032b}'.format(result["value"])
                for i in range(4):
                    self.ext_dmem.DMem[result["memory_location"] + i] = _32b[8 * i: 8 * (i + 1)]
            elif result["operation"] in ["BEQ", "BNE"]:
                # MEM to 1st hazard
                if self.previous_stage_dest_reg and (result["rs1"] == self.previous_stage_dest_reg or result["rs2"] == self.previous_stage_dest_reg):
                    NOP = True
                    self.previous_stage_dest_reg = None
                pass
            elif result["operation"] == "JAL":
                register_contents[result["rd"]] = self.state.IF["PC"] + 4
            else:
                # MEM to 1st hazard
                if self.previous_stage_dest_reg and (result["rs1"] == self.previous_stage_dest_reg or result.get("rs2") == self.previous_stage_dest_reg):
                    NOP = True
                    print(self.previous_stage_dest_reg)
                register_contents[result["rd"]] = result["value"]
                self.myRF.writeRF(result["rd"], result["value"])
            if result["operation"] != "LW":
                self.previous_stage_dest_reg = None
            result["PC"] = self.state.IF["PC"]
            result["NextPC"] = self.nextState.IF["PC"]
            # update program counter
            self.nextState.IF["PC"] = self.state.IF["PC"] + result.get("offset", DEFAULT_OFFSET)
            result["PC"] = self.state.IF["PC"]
            result["NextPC"] = self.nextState.IF["PC"]
        else:
            self.halted = True

        return result, instruction, NOP


