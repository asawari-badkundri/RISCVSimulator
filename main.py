from SingleStage import SingleStageCore
from FiveStage import FiveStageCore

import os
import argparse

MemSize = 1000
# memory size, in reality, the memory size should be 2^32, but for this lab,
# for the space resaon, we keep it as this large number, but the memory is still 32-bit addressable.

TC_NUMBER = 4
CUSTOM_IO = False
ENABLE_SS = True
ENABLE_FS = True
TC_PATH = "" if CUSTOM_IO else f"/Testcases/TC{TC_NUMBER}"
PERF_METRIC_FILE = f"/PerformanceMetrics_Results_{TC_NUMBER}.txt"


class InsMem(object):
    def __init__(self, name, ioDir):
        self.id = name

        with open(ioDir + f"{TC_PATH}/imem.txt") as im:
            self.IMem = [data.replace("\n", "") for data in im.readlines()]
            # insert halt
            # self.IMem.extend(["00000000", "00000000", "00000000", "01111111"])

    def readInstr(self, read_address):
        # read instruction memory
        # returns array of 4 bytes starting from readAddress
        instruction = self.IMem[read_address : read_address + 4]
        # TODO: return 32 bit hex val
        return instruction


class DataMem(object):
    def __init__(self, name, ioDir):
        self.id = name
        self.ioDir = ioDir
        with open(ioDir + f"{TC_PATH}/dmem.txt") as dm:
            init_dmem = ["00000000"] * MemSize
            self.DMem = [data.replace("\n", "") for data in dm.readlines()]
            init_dmem[: len(self.DMem)] = self.DMem
            self.DMem = init_dmem

    def readDataMem(self, ReadAddress):
        # read data memory
        # return 32 bit hex val
        return "".join(self.DMem[ReadAddress : ReadAddress + 4])

    def writeDataMem(self, Address, WriteData):
        # write data into byte addressable memory
        for i in range(4):
            self.DMem[Address + i] = WriteData[i : i + 8]

    def outputDataMem(self, id):
        resPath = self.ioDir + "/" + id + "_DMEMResult.txt"
        with open(resPath, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])


if __name__ == "__main__":

    # parse arguments for input file location
    parser = argparse.ArgumentParser(description="RV32I processor")
    parser.add_argument(
        "--iodir", default="", type=str, help="Directory containing the input files."
    )
    args = parser.parse_args()

    ioDir = os.path.abspath(args.iodir)
    print("IO Directory:", ioDir)

    # contains data from imem and dmem
    imem = InsMem("Imem", ioDir)
    dmem_ss = DataMem("SS", ioDir)
    dmem_fs = DataMem("FS", ioDir)

    ssCore = SingleStageCore(ioDir, imem, dmem_ss)
    fsCore = FiveStageCore(ioDir, imem, dmem_fs)

    while True and ENABLE_SS:
        if not ssCore.halted:
            ssCore.step()

        if ssCore.halted:
            break

    # output single stage dmem
    dmem_ss.outputDataMem("SS")

    while True and ENABLE_FS:
        if not fsCore.halted:
            fsCore.step()

        if fsCore.halted:
            break

    # output five stage dmem
    dmem_ss.outputDataMem("FS")

    performance = [
        "Single Stage Core Performance Metrics-----------------------------" + "\n" +
        "Number of cycles taken: " + str(ssCore.cycle) + "\n" +
        "Cycles per instruction: " + str(round(ssCore.cycle / (len(ssCore.ext_imem.IMem) / 4),6)) + "\n" + 
        "Instructions per cycle: " + str((len(ssCore.ext_imem.IMem)/4) / ssCore.cycle) + "\n\n",
        "Five Stage Core Performance Metrics-----------------------------" + "\n"+
        "Number of cycles taken: " + str(fsCore.cycle) + "\n",
        "Cycles per instruction: " + str(round(fsCore.cycle / (len(fsCore.ext_imem.IMem) / 4),6)) + "\n"
        "Instructions per cycle: " + str((len(fsCore.ext_imem.IMem)/4) / fsCore.cycle) + "\n"
    ]
    with open(ioDir + PERF_METRIC_FILE, 'w+') as wf:
        wf.writelines(performance)
