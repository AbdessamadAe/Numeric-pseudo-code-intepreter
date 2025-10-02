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
    
    def initialize_constants(self):
        for i in range(10):
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
                        if instruction:
                            instructions.append(instruction)
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

        if self.debug:
            print(f"DEBUG: PC={self.pc}, Executing: {sign}{op_code} {operand1:03d} {operand2:03d} {operand3:03d}")
            print(f"DEBUG: Memory[{operand1}]={self.memory[operand1]}, Memory[{operand2}]={self.memory[operand2]}, Memory[{operand3}]={self.memory[operand3]}")
        
        if op_code == 0:
            if sign == '+':
                self.variables[operand1] = self.top_memory + 1
                self.top_memory += operand2
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
            if sign == '+':
                labeladdress = self.instruction_labels[operand3]
                if self.memory[operand1] == self.memory[operand2]:
                    self.pc = operand3
            else:
                if self.memory[self.variables[operand3]] != self.memory[self.variables[operand3]]:
                    self.pc = operand3
        elif op_code == 5:
            if sign == '+':
                if self.memory[operand1] >= self.memory[operand2]:
                    self.pc = operand3
            else:
                if self.memory[operand1] < self.memory[operand2]:
                    self.pc = operand3
        elif op_code == 6:
            if sign == '+':
                self.memory[operand3] = self.memory[operand1 + self.memory[operand2]]
            else:
                self.memory[operand2 + self.memory[operand3]] = self.memory[operand1]
        elif op_code == 7:
            if sign == '+':
                if self.debug:
                    print(f"DEBUG: Incrementing memory[{operand1}] from {self.memory[operand1]} to {self.memory[operand1] + 1}")
                self.memory[operand1] += 1
                if self.debug:
                    print(f"DEBUG: Comparing memory[{operand1}]={self.memory[operand1]} < memory[{operand2}]={self.memory[operand2]}")
                if self.memory[operand1] < self.memory[operand2]:
                    if self.debug:
                        print(f"DEBUG: Jumping to instruction {operand3}")
                    self.pc = operand3
                else:
                    if self.debug:
                        print(f"DEBUG: No jump, continuing to next instruction")
        elif op_code == 8:
            if sign == '+':
                if self.debug:
                    print(f"DEBUG: Reading input into memory[{operand3}]")
                print("Please enter a number: ")
                self.memory[operand3] = int(input())
                if self.debug:
                    print(f"DEBUG: Stored {self.memory[operand3]} in memory[{operand3}]")
            else:
                if self.debug:
                    print(f"DEBUG: Printing memory[{operand1}]={self.memory[operand1]}")
                print(self.memory[operand1])
        elif op_code == 9:
            if sign == '+':
                self.running = False
        else:
            print(f"Unknown operation code: {sign}{op_code}")
    
    def run(self, instructions):
        if instructions is None:
            return
        
        if self.debug:
            print(f"DEBUG: Starting execution with {len(instructions)} instructions")
        self.pc = 0
        self.running = True
        
        while self.running and self.pc < len(instructions):
            if self.debug:
                print(f"DEBUG: About to execute instruction at PC={self.pc}")
            instruction = instructions[self.pc]
            old_pc = self.pc
            self.execute_instruction(instruction)
            if self.pc == old_pc:
                self.pc += 1
                if self.debug:
                    print(f"DEBUG: PC incremented to {self.pc}")
            else:
                if self.debug:
                    print(f"DEBUG: PC jumped from {old_pc} to {self.pc}")
            if self.debug:
                print("---")

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
