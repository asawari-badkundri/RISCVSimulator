# RISCV Simulator

The project involves implementing cycle-accurate simulators of a 32-bit RISC-V processor in Python. The simulator takes two files (imem.txt and dmem.txt) as inputs to initialize the instruction and data memory. It provides cycle-by-cycle states of the register file, microarchitectural state of the machine, and resulting dmem data after program execution.

The supported instructions are ADD, SUB, XOR, OR, AND, ADDI, XORI, ORI, ANDI, JAL, BEQ, BNE, LW, SW, and HALT. The simulator has a five-stage pipeline, including Instruction Fetch, Instruction Decode/Register Read, Execute, Load/Store, and Writeback stages. It handles RAW hazards using forwarding and stalling and resolves control flow hazards during the ID/RF stage.

- Program starts from `main.py`.
- Make sure `ENABLE_SS` and `ENABLE_FS` are set to `True`.
- Add more test cases in the `Testcases/` folder.
- Run a specific test case by setting `TC_NUMBER` to the desired test #.


