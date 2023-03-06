#!/usr/bin/python

import sys  # read in <sourcefile> 2nd command parameter line by line


# Save registers as a dictionary for accessing them easily
registers = {
    'A': '0001',
    'B': '0002',
    'C': '0003',
    'D': '0004',
    'E': '0005',
}


# Save opcodes as a dictionary for accessing them easily
opCodes = {
    'HALT': '01', 'LOAD': '02', 'STORE': '03', 'ADD': '04', 'SUB': '05', 'INC': '06', 'DEC': '07',
    'XOR': '08', 'AND': '09', 'OR': '0A', 'NOT': '0B', 'SHL': '0C', 'SHR': '0D', 'NOP': '0E',
    'PUSH': '0F', 'POP': '10', 'CMP': '11', 'JMP': '12', 'JZ': '13', 'JE': '13',
    'JNZ': '14', 'JNE': '14', 'JC': '15', 'JNC': '16', 'JA': '17', 'JAE': '18',
    'JB': '19', 'JBE': '1A', 'READ': '1B', 'PRINT': '1C'
}

# Save addressing modes as a dictionary for accessing them easily
addressingModes = {
    'immediate': '0',
    'register': '1',
    'regmem': '2',
    'memory': '3',
}

# Some global variables..
lines, output = [], []

labels = {}

start_address = 0

if len(sys.argv) != 2: print('usage: assembler.py <sourcefile>'); sys.exit(1)
f = open(sys.argv[1], 'r')
while True:  # read in the source line
    line = f.readline()
    if not line: break
    lines.append(line.strip())  # store each line without leading/trailing whitespaces
f.close()



# - Check the operands and get their addressing mode names.
# - From their addressing modes compute the operand bits as hex.
# Args:
#   operand (string)
#
# Returns:
#   addressingMode (string): key of dict(addressingModes)
#   convertedHex (string): hexcode of converted operand
def convertOperand(operand):
    addressingMode = 'nill'
    convertedHex = ''
    # Check for immediate chars
    if (operand.startswith("'")):
        # Seperate it from their apostrophes and convert it to hexadecimal
        addressingMode = addressingModes['immediate']
        convertedHex = hex(ord(operand[1:-1]))[2:]
    
    # Check for memory related addreses
    elif (operand.startswith("[")):
        addressingMode = addressingModes['memory']
        withoutBrackets = operand[1:-1]
        # They can refered with register. Check here.
        if withoutBrackets in ['A', 'B', 'C', 'D', 'E']:
            convertedHex = registers[withoutBrackets]
            addressingMode = addressingModes['regmem']
        else:
            convertedHex = withoutBrackets
    # Check here for register addressing modes.
    elif (operand in ['A', 'B', 'C', 'D', 'E']):
        addressingMode = addressingModes['register']
        convertedHex = registers[operand]
    # Check remaining immediate data.
    elif (operand.isdigit()):
        addressingMode = addressingModes['immediate']
        convertedHex = operand
    # Lastly they are labels.
    else:
        addressingMode = addressingModes['immediate']
        convertedHex = labels[operand]
    return addressingMode,convertedHex



# Helper functions for converting integers to binary strings.

def opCodeToBin(opcode):
    numOfBits = 6
    scale = 16
    return bin(int(opcode, scale))[2:].zfill(numOfBits)

def modeToBin(mode):
    numOfBits = 2
    scale = 16
    return bin(int(mode, scale))[2:].zfill(numOfBits)

def operandToBin(operand):
    numOfBits = 16
    scale = 16
    return bin(int(operand, scale))[2:].zfill(numOfBits)





################## PASS-1 #####################
#
# First pass for determining the labels and their addresses.
#
counter = 0
for line in lines:
    
    # Split the lines for spaces and get the instructions.
    instruction = line.split(" ")

    # Instruction halt does not require an address we should skip it.
    if instruction[0] == 'HALT':
        continue
    
    # check the NOP instruction
    if instruction[0] == 'NOP':
        counter = counter + 1
        continue
    # Here we check the labels
    if len(instruction) < 2:
        # If we find the label drop the ':' seperator from it
        # And add it to the labels dictionary.
        labels[line[:-1]] = hex(counter*3)[2:]
    counter = counter + 1


################## PASS-2 #####################
#
# If we encounter with label we will use the labeled addresses for them.
#
counter = 0
for line in lines:
    # Split the lines for spaces and get the instructions.
    instruction = line.split(" ")

    # Check the opcodes with operand
    if len(instruction) > 1:
        # Get the opcode from its name
        opcode = opCodes[instruction[0]]
        # Get the operand and addressing mode as an hex.
        addr, operand = convertOperand(instruction[1])
    else:
        # Check for 'HALT' instruction
        if instruction[0] == 'HALT':
            opcode = opCodes[instruction[0]]
            # Manually gave the addressing mode and operand
            addr, operand = '0','0000'
        elif instruction[0] == 'NOP':
            opcode = opCodes[instruction[0]]
            addr, operand = '0','0000'
        else:
            # Check for label instruction
            continue
    
    # Converting the hexadecimals to binary is more convenient.
    # Because we concat two binary strings with different lengths.
    resultBinary = opCodeToBin(opcode) + modeToBin(addr) + operandToBin(operand)
    decimal = int(resultBinary, 2)
    # Output list contains with filled zero hexadecimals.
    output.append(str(hex(decimal)[2:]).zfill(6))
    counter = counter + 1

# Save the original file descriptor
original_stdout = sys.stdout

# Get the result filename from argument
# And make the stdout(file descriptor) to this file
outFile = open(sys.argv[1][:-4]+".bin", 'w')
sys.stdout = outFile

# After appending every line to the output file
for element in output:
    print(element.upper())

# Change back to original File descriptor(Doesn't needed)
sys.stdout = original_stdout
outFile.close()

# Exit()