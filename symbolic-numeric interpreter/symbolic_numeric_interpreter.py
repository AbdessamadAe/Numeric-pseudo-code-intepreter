"""
Symbolic-Numeric Interpreter
Authors: Younes Kettani, Abdessamad Ait Elmouden
"""

import sys
import re


class SymbolicNumericInterpreter:
    def __init__(self, debug=False):
        self.memory = [0] * 1000
        self.top_memory = 0
        self.variables = {}
        self.instruction_labels = {}
        self.pc = 0
        self.running = True
        self.debug = debug
        self.initialize_constants()
        self.block_execution = False
        self.queued_label = None
        self.section = 0
        self.input_top = 0
        self.inputs = []
    
    def debug_log(self, category, message, indent_level=0):
        """Structured debug logging with categories and indentation"""
        if self.debug:
            indent = "  " * indent_level
            print(f"DEBUG [{category}]: {indent}{message}")
    
    def initialize_constants(self):
        for i in range(10):
            self.variables[i] = i
            self.memory[i] = i
        self.top_memory = i
    
    def load_program(self, filename):
        instructions = []
        try:
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('//'):
                        instruction = self.parse_instruction(line)
                        if instruction and (instruction['sign'] == '+' and instruction['op_code'] == 9 and instruction['operand1'] == 999 and instruction['operand3'] == 999):
                                    self.section += 1
                                    self.debug_log("PARSE", f"Switching to section {self.section}")
                        else:
                            if self.section == 0 or self.section == 1:
                                instructions.append(instruction)
                            else: # means it's input section
                                if instruction['sign'] == '+' and instruction['op_code'] == 0:
                                    self.inputs.append(instruction['operand3'])
                                elif instruction['sign'] == '-' and instruction['op_code'] == 0:
                                    self.inputs.append(-1*instruction['operand3'])
            return instructions
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return None
        except Exception as e:
            print(f"Error loading program: {e}")
            return None
    
    def parse_instruction(self, line):
        line = line.split('//')[0].strip()
        if not line:
            return None
        
        parts = line.split()
        if len(parts) >= 4:
            sign = parts[0][0]
            op_code = int(parts[0][1:])
            operand1 = int(parts[1])
            operand2 = int(parts[2])
            operand3 = int(parts[3])
            
            return {
                'sign': sign,
                'op_code': op_code,
                'operand1': operand1,
                'operand2': operand2,
                'operand3': operand3
            }
        return None
    
    def execute_instruction(self, instruction):
        op_code = instruction['op_code']
        operand1 = instruction['operand1']
        operand2 = instruction['operand2']
        operand3 = instruction['operand3']
        sign = instruction['sign']

        self.debug_log("EXEC", f"PC={self.pc}, Instruction: {sign}{op_code} {operand1:03d} {operand2:03d} {operand3:03d}")
        
        if not self.block_execution:
            if op_code == 0:
                if sign == '+':
                    self.variables[operand1] = self.top_memory + 1
                    self.top_memory += operand2
                    self.debug_log("ALLOC", f"Variable {operand1} allocated at memory location {self.variables[operand1]}, top_memory now {self.top_memory}", 1)
            elif op_code == 1:
                if sign == '+':
                    self.memory[self.variables[operand3]] = self.memory[self.variables[operand1]] + self.memory[self.variables[operand2]]
                else:
                    self.memory[self.variables[operand3]] = self.memory[self.variables[operand1]] - self.memory[self.variables[operand2]]
            elif op_code == 2:
                if sign == '+':
                    self.memory[self.variables[operand3]] = self.memory[self.variables[operand1]] * self.memory[self.variables[operand2]]
                else:
                    self.memory[self.variables[operand3]] = self.memory[self.variables[operand1]] // self.memory[self.variables[operand2]]
            elif op_code == 3:
                if sign == '+':
                    self.memory[self.variables[operand3]] = self.memory[self.variables[operand1]] * self.memory[self.variables[operand1]]
                else:
                    self.memory[self.variables[operand3]] = int(self.memory[self.variables[operand1]] ** 0.5)
            elif op_code == 4:
                jumpaddress = None
                if operand3 in self.instruction_labels:
                    jumpaddress = self.instruction_labels[operand3]
                if sign == '+':
                    if self.memory[self.variables[operand1]] == self.memory[self.variables[operand2]]:
                        if jumpaddress == None:
                            self.block_execution = True
                            self.queued_label = operand3
                        else:
                            self.pc = jumpaddress
                else:
                    if self.memory[self.variables[operand1]] != self.memory[self.variables[operand2]]:
                        if jumpaddress == None:
                            self.block_execution = True
                            self.queued_label = operand3
                        else:
                            self.pc = jumpaddress
            elif op_code == 5:
                jumpaddress = None
                if operand3 in self.instruction_labels:
                    jumpaddress = self.instruction_labels[operand3]
                if sign == '+':
                    if self.memory[self.variables[operand1]] >= self.memory[self.variables[operand2]]:
                        if jumpaddress == None:
                            self.block_execution = True
                            self.queued_label = operand3
                        else:
                            self.pc = jumpaddress
                else:
                    if self.memory[self.variables[operand1]] < self.memory[self.variables[operand2]]:
                        if jumpaddress == None:
                            self.block_execution = True
                            self.queued_label = operand3
                        else:
                            self.pc = jumpaddress
            elif op_code == 6:
                if sign == '+':
                    self.debug_log("ARRAY", f"Load operation: calculating array index", 1)
                    self.debug_log("ARRAY", f"Offset value: {self.memory[self.variables[operand2]]}", 2)
                    array_index = self.variables[operand1] + self.memory[self.variables[operand2]]
                    self.memory[self.variables[operand3]] = self.memory[array_index]
                    self.debug_log("ARRAY", f"Load: M[{self.variables[operand3]}] = M[{array_index}] = {self.memory[array_index]}", 1)
                else:
                    array_index = self.variables[operand2] + self.memory[self.variables[operand3]]
                    self.memory[array_index] = self.memory[self.variables[operand1]]
                    self.debug_log("ARRAY", f"Store: M[{array_index}] = M[{self.variables[operand1]}] = {self.memory[self.variables[operand1]]}", 1)
            elif op_code == 7:
                self.debug_log("LABEL", f"Current instruction_labels: {self.instruction_labels}", 1)

                if sign == '+':
                    jumpaddress = self.instruction_labels[operand3]
                    self.debug_log("LOOP", f"Incrementing M[{self.variables[operand1]}] from {self.memory[self.variables[operand1]]} to {self.memory[self.variables[operand1]] + 1}", 1)
                    self.memory[self.variables[operand1]] += 1
                    self.debug_log("LOOP", f"Comparing M[{self.variables[operand1]}]={self.memory[self.variables[operand1]]} < M[{self.variables[operand2]}]={self.memory[self.variables[operand2]]}", 1)
                    if self.memory[self.variables[operand1]] < self.memory[self.variables[operand2]]:
                        self.debug_log("JUMP", f"Loop condition true, jumping to instruction {jumpaddress}", 1)
                        self.pc = jumpaddress
                    else:
                        self.debug_log("JUMP", f"Loop condition false, continuing to next instruction", 1)
                else:
                    self.instruction_labels[operand1] = self.pc + 1
                    self.debug_log("LABEL", f"Label {operand1} set to instruction {self.pc + 1}", 1)
            elif op_code == 8:
                if sign == '+':
                    self.debug_log("I/O", f"Reading input {self.inputs[self.input_top]} into M[{self.variables[operand3]}] (input #{self.input_top})", 1)
                    self.memory[self.variables[operand3]] = int(self.inputs[self.input_top])
                    self.input_top += 1
                else:
                    self.debug_log("I/O", f"Output: M[{self.variables[operand1]}] = {self.memory[self.variables[operand1]]}", 1)
                    print(self.memory[self.variables[operand1]])
            elif op_code == 9:
                if sign == '+' and operand1 == 0 and operand2 == 0 and operand3 == 0:
                    self.running = False
            else:
                print(f"Unknown operation code: {sign}{op_code}")

        else:
            if op_code == 7 and sign == '-':
                self.instruction_labels[operand1] = self.pc + 1
                if self.queued_label != None and self.queued_label == operand1:
                    self.block_execution = False
                    self.queued_label = None
                    self.pc = self.instruction_labels[operand1]
 
    def run(self, instructions):
        if instructions is None:
            return
        
        self.debug_log("INIT", f"Starting execution with {len(instructions)} instructions")
        self.debug_log("INIT", f"Initial variables: {self.variables}")
        self.pc = 0
        self.running = True
        
        while self.running and self.pc < len(instructions):
            self.debug_log("EXEC", f"About to execute instruction at PC={self.pc}")
            if self.block_execution:
                self.debug_log("BLOCK", f"Execution blocked, waiting for label {self.queued_label}", 1)
            
            instruction = instructions[self.pc]
            old_pc = self.pc
            self.execute_instruction(instruction)
            
            # Handle program counter updates
            if self.pc == old_pc:
                self.pc += 1
                self.debug_log("PC", f"Sequential execution: PC incremented to {self.pc}", 1)
            else:
                self.debug_log("PC", f"Control flow change: PC jumped from {old_pc} to {self.pc}", 1)
            
            self.debug_log("EXEC", "Instruction completed")
            if self.debug:
                print()


def main():
    debug = False
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 numeric_interpreter.py <program_file> [--debug]")
        return
    
    filename = sys.argv[1]
    if len(sys.argv) == 3 and sys.argv[2] == '--debug':
        debug = True
    
    interpreter = SymbolicNumericInterpreter(debug=debug)
    instructions = interpreter.load_program(filename)
    interpreter.run(instructions)

if __name__ == "__main__":
    main()
