
class Core(object):
    def __init__(self, ioDir, imem, dmem):
        self.myRF = RegisterFile(ioDir)
        self.cycle = 0
        self.halted = False
        self.ioDir = ioDir
        self.state = State()
        self.nextState = State()
        self.ext_imem = imem
        self.ext_dmem = dmem


class State(object):
    def __init__(self):
        self.IF = {"nop": 0, "PC": 0}
        self.ID = {"nop": 0, "PC": 0, "Instr": 0}
        self.EX = {"nop": 0, "Read_data1": 0, "Read_data2": 0, "Imm": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0,
                   "is_I_type": False, "rd_mem": 0,
                   "wrt_mem": 0, "alu_op": 0, "wrt_enable": 0}
        self.MEM = {"nop": 0, "ALUresult": 0, "Store_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "rd_mem": 0,
                    "wrt_mem": 0, "wrt_enable": 0}
        self.WB = {"nop": 0, "Wrt_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "wrt_enable": 0}
        self.is_hazard_nop = 0

class RegisterFile(object):
    def __init__(self, ioDir):
        self.outputFile = ioDir + "RFResult.txt"
        self.Registers = ["0"*32 for i in range(32)]

    def readRF(self, Reg_addr):
        # Fill in
        return self.Registers[int(Reg_addr, 2)]

    def writeRF(self, Reg_addr, Wrt_reg_data):
        if int(Reg_addr, 2) != 0:
            self.Registers[int(Reg_addr, 2)] = Wrt_reg_data

    def outputRF(self, cycle):
        op = ["State of RF after executing cycle:\t" + str(cycle) + "\n"]

        #print(self.Registers)
        # op.extend([str('{:032b}'.format(val & 4294967295)) + "\n" for val in self.Registers])
        op.extend([str(val) + "\n" for val in self.Registers])
        #print("opfinal", op)
        if cycle == 0:
            perm = "w"
        else:
            perm = "a"
        with open(self.outputFile, perm) as file:
            file.writelines(op)
