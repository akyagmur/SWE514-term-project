import sys  # read in <sourcefile> 2nd command parameter line by line


## Each line consist of hexadecimal bytecodes
## - Converting them to the binary representations
## -  XXXXXX   -   XX   -   XXXXXXXXXXXXXXXX
##    OpCode    Addr Mode       Operand
## 
## - Each opcode has an own function.



## All the computations are done in decimal integers.
## Then convert to the hexadecimal representations.


########### GLOBAL VARIABLES ###########

lines, output = [], []

# Program Counter will shows the current instruction.
program_counter = '0000'

# Signed and unsigned max and min decimal integers for 2-byte
unsignedMAX = 65535
signedMAX = 32767
signedMIN = -32768

# Condition codes
zf, cf, sf = 0, 0, 0

# Registers [A,B,C,D,E] -> for simplicity used 1,2,3,4,5
registers = {
    '1': 0,
    '2': 0,
    '3': 0,
    '4': 0,
    '5': 0
}

# Stack pointer represents the maximum address of the memory
# When something pushed to the stack it will grow the opposite way of the addresses.
stack_pointer = 65535

# 2-Byte words in stack saved in this list.
stack = []

# Memory is the main variable which stores:
# - Instructions
# - Data
# - Stack
#
#
# Starts from 0 to 65K like:
#
# - Instructions has 3 bytes representation
# - Data has 2 bytes
# - Stack data has also 2 bytes
# addr - Represent
#
# 0000 - [INSTR-1]
# 0003 - [INSTR-2]
# 0006 - [INSTR-3]
#  .   -     .
#  .   -     .
# 0033 - [DATA-1]
# 0035 - [DATA-2]
#  .   -     .
#  .   -     .
# FFFD - [STACK-TOP]
# FFFF - [STACK-BOTTOM]
memory = {}

# ------------------------------------ #

#######----- UTILITY FUNCTIONS -----#######

# Convert unsigned integer to signed.
def utos(unsigned):
    signed = unsigned - 2**16
    return signed

# Convert signed integer to unsigned
def stou(signed):
    unsigned = signed + 2**16
    return unsigned

# Convert hexadecimal instruction bytecodes to the binary representations
def hexToBinary(num):
    scale = 16
    numOfBits = 24
    return bin(int(num, scale))[2:].zfill(numOfBits)

# Seperate the OPCODE - MODE - OPERAND from the binary representations
def parseBits(num):
    binary = hexToBinary(num)
    opcode = binary[0:6]
    mode = binary[6:8]
    operand = binary[8:]
    return opcode, mode, operand

# Convert binary to hexadecimal with filled up to 1 byte.
def binaryToHex(binary):
    decimal = int(binary, 2)
    return hex(decimal)[2:].zfill(2).upper()

# Convert decimal to hexadecimal with filled up to 2 bytes.
def decimalToHex(decimal):
    if decimal < 0: return hex(stou(decimal))[2:].zfill(4)
    return hex(decimal)[2:].zfill(4)

# Convert hexadecimal to integer number.
def hexToDecimal(hexa):
    return int(hexa, 16)

# ------------------------------------ #



#######----- OPCODES -----#######

# The values of the registers and the memory should be hexadecimal (uppercased)
# Also they are string and with filled up to 2 bytes! (Word size)
# Example: 
# registers['1'] = '000A'
# memory['address'] = '002A' for data.
# memory['address'] = 'ABCDEF' for instructions.

# Loads operand onto A.
# No Condition codes setup needed.
def load(mode, operand):
    #print("Mode: ", mode, "\t Operand: ", decimalToHex(operand))
    global registers, memory
    if mode == 0:
        registers['1'] = decimalToHex(operand)
    elif mode == 1:
        registers['1'] = registers[str(operand)]
    elif mode == 2:
        registers['1'] = memory[registers[str(operand)]]
    else:
        registers['1'] = memory[decimalToHex(operand)]



# Stores value in A to the operand.
# No Condition codes setup needed.
def store(mode, operand):
    #print("Mode: ", mode, "\t Operand: ", decimalToHex(operand))
    global registers, memory
    if mode == 1:
        registers[str(operand)] = registers['1']
    elif mode == 2:
        memory[registers[str(operand)]] = registers['1']
    else:
        memory[decimalToHex(operand)] = registers['1']



# Adds operand to A. Perform the addition by treating all the bits as unsigned integer.
# CC set => CF, SF, ZF
def add(mode, operand):
    #print("Mode: ", mode, "\t Operand: ", decimalToHex(operand))
    global registers, memory, zf, cf, sf
    tempA = hexToDecimal(registers['1'])
    if mode == 0:
        tempA = tempA + operand
    elif mode == 1:
        tempA = tempA + hexToDecimal(registers[str(operand)])
    elif mode == 2:
        tempA = tempA + hexToDecimal(memory[registers[str(operand)]])
    else:
        tempA = tempA + hexToDecimal(memory[decimalToHex(operand)])
    if tempA > unsignedMAX:
        tempA = tempA - unsignedMAX
        cf = 1
    else:
        cf = 0
    if tempA == 0:
        zf = 1
    else:
        zf = 0
    if utos(tempA) < 0:
        sf = 1
    else:
        sf = 0
    registers['1'] = decimalToHex(tempA)
    

# Subtracts operand (OPR) from A.
# CC set => CF, SF, ZF
def sub(mode, operand):
    #print("Mode: ", mode, "\t Operand: ", decimalToHex(operand))
    global registers, memory, zf, cf, sf
    tempA = hexToDecimal(registers['1'])
    if mode == 0:
        tempA = tempA + ~(operand) + 1
    elif mode == 1:
        tempA = tempA + ~(hexToDecimal(registers[str(operand)])) + 1
    elif mode == 2:
        tempA = tempA + ~(hexToDecimal(memory[registers[str(operand)]])) + 1
    else:
        tempA = tempA + ~(hexToDecimal(memory[decimalToHex(operand)])) + 1
    if tempA > unsignedMAX:
        tempA = tempA - unsignedMAX
        cf = 1
    else:
        cf = 0
    if tempA == 0:
        zf = 1
    else:
        zf = 0
    if utos(tempA) < 0:
        sf = 1
    else:
        sf = 0
    registers['1'] = decimalToHex(tempA)


# increments operand (equivalent to add 1)
# CC set => CF, SF, ZF
def inc(mode, operand):
    #print("Mode: ", mode, "\t Operand: ", decimalToHex(operand))
    global registers, memory, zf, cf, sf
    tempA = 0
    if mode == 0:
        tempA = operand + 1
        operand = tempA
    elif mode == 1:
        tempA = hexToDecimal(registers[str(operand)]) + 1
        registers[str(operand)] = decimalToHex(tempA)
    elif mode == 2:
        tempA = hexToDecimal(memory[registers[str(operand)]]) + 1
        memory[registers[str(operand)]] = decimalToHex(tempA)
    else:
        tempA = hexToDecimal(memory[decimalToHex(operand)]) + 1
        memory[decimalToHex(operand)] = decimalToHex(tempA)
    if tempA > unsignedMAX:
        tempA = tempA - unsignedMAX
        cf = 1
    else:
        cf = 0
    if tempA == 0:
        zf = 1
    else:
        zf = 0
    if utos(tempA) < 0:
        sf = 1
    else:
        sf = 0


# decrements operand (equivalent to subtract 1)
# CC set => CF, SF, ZF
def dec(mode, operand):
    #print("Mode: ", mode, "\t Operand: ", decimalToHex(operand))
    global registers, memory, zf, cf, sf
    tempA = 0
    if mode == 0:
        tempA = operand + (~1) + 1
        operand = tempA
    elif mode == 1:
        tempA = hexToDecimal(registers[str(operand)]) + (~1) + 1
        registers[str(operand)] = decimalToHex(tempA)
    elif mode == 2:
        tempA = hexToDecimal(memory[registers[str(operand)]]) + (~1) + 1
        memory[registers[str(operand)]] = decimalToHex(tempA)
    else:
        tempA = hexToDecimal(memory[decimalToHex(operand)]) + (~1) + 1
        memory[decimalToHex(operand)] = decimalToHex(tempA)
    if tempA > unsignedMAX:
        tempA = tempA - unsignedMAX
        cf = 1
    else:
        cf = 0
    if tempA == 0:
        zf = 1
    else:
        zf = 0
    if utos(tempA) < 0:
        sf = 1
    else:
        sf = 0


# Bitwise XOR operand with A and store result in A.
# CC set => SF, ZF
def xor(mode, operand):
    #print("Mode: ", mode, "\t Operand: ", decimalToHex(operand))
    global registers, memory, zf, sf
    tempA = hexToDecimal(registers['1'])
    if mode == 0:
        tempA = tempA ^ operand
    elif mode == 1:
        tempA = tempA ^ hexToDecimal(registers[str(operand)])
    elif mode == 2:
        tempA = tempA ^ hexToDecimal(memory[registers[str(operand)]])
    else:
        tempA = tempA ^ hexToDecimal(memory[decimalToHex(operand)])
    if tempA == 0:
        zf = 1
    else:
        zf = 0
    if utos(tempA) < 0:
        sf = 1
    else:
        sf = 0
    registers['1'] = decimalToHex(tempA)


# Bitwise AND operand with A and store result in A.
# CC set => SF, ZF
def andd(mode, operand):
    #print("Mode: ", mode, "\t Operand: ", decimalToHex(operand))
    global registers, memory, zf, sf
    tempA = hexToDecimal(registers['1'])
    if mode == 0:
        tempA = tempA & operand
    elif mode == 1:
        tempA = tempA & hexToDecimal(registers[str(operand)])
    elif mode == 2:
        tempA = tempA & hexToDecimal(memory[registers[str(operand)]])
    else:
        tempA = tempA & hexToDecimal(memory[decimalToHex(operand)])
    if tempA == 0:
        zf = 1
    else:
        zf = 0
    if utos(tempA) < 0:
        sf = 1
    else:
        sf = 0
    registers['1'] = decimalToHex(tempA)


# Bitwise OR operand with A and store result in A.
# CC set => SF, ZF
def orr(mode, operand):
    #print("Mode: ", mode, "\t Operand: ", decimalToHex(operand))
    global registers, memory, zf, sf
    tempA = hexToDecimal(registers['1'])
    if mode == 0:
        tempA = tempA | operand
    elif mode == 1:
        tempA = tempA | hexToDecimal(registers[str(operand)])
    elif mode == 2:
        tempA = tempA | hexToDecimal(memory[registers[str(operand)]])
    else:
        tempA = tempA | hexToDecimal(memory[decimalToHex(operand)])
    if tempA == 0:
        zf = 1
    else:
        zf = 0
    if utos(tempA) < 0:
        sf = 1
    else:
        sf = 0
    registers['1'] = decimalToHex(tempA)


# Bitwise NOT operand with A and store result in A.
# CC set => SF, ZF
def nott(mode, operand):
    #print("Mode: ", mode, "\t Operand: ", decimalToHex(operand))
    global registers, memory, zf, sf
    tempA = 0
    if mode == 0:
        tempA = ~operand
    elif mode == 1:
        tempA = ~hexToDecimal(registers[str(operand)])
        registers[str(operand)] = decimalToHex(tempA)
    elif mode == 2:
        tempA = ~hexToDecimal(memory[registers[str(operand)]])
        memory[registers[str(operand)]] = decimalToHex(tempA)
    else:
        tempA = ~hexToDecimal(memory[decimalToHex(operand)])
        memory[decimalToHex(operand)] = decimalToHex(tempA)
    if tempA == 0:
        zf = 1
    else:
        zf = 0
    if utos(tempA) < 0:
        sf = 1
    else:
        sf = 0


# Shift the bits of register one position to the left.
# CC set => CF, SF, ZF
def shl(mode, operand):
    #print("Mode: ", mode, "\t Operand: ", decimalToHex(operand))
    global registers, memory, zf, cf, sf
    tempA = hexToDecimal(registers[str(operand)])
    if mode == 1:
        tempA = (tempA << 1)
    if tempA > unsignedMAX:
        tempA = tempA - unsignedMAX
        cf = 1
    else:
        cf = 0
    if tempA == 0:
        zf = 1
    else:
        zf = 0
    if utos(tempA) < 0:
        sf = 1
    else:
        sf = 0


# Shift the bits of register one position to the right.
# CC set => SF, ZF
def shr(mode, operand):
    #print("Mode: ", mode, "\t Operand: ", decimalToHex(operand))
    global registers, memory, zf, sf
    tempA = hexToDecimal(registers[str(operand)])
    if mode == 1:
        tempA = (tempA >> 1)
    if tempA == 0:
        zf = 1
    else:
        zf = 0
    if utos(tempA) < 0:
        sf = 1
    else:
        sf = 0


# NOP: No operation.
def nop():
    return


#   Push the word to the stack
#   And decrement stack pointer by 2
def pushh(mode, operand):
    global stack_pointer, stack, registers
    if mode != 1:
        return
    tempA = hexToDecimal(registers[str(operand)])
    stack.append(tempA)
    stack_pointer = stack_pointer - 2


#   Pop the word from the stack
#   And increment stack pointer by 2
def popp(mode, operand):
    if mode != 1:
        return
    global stack_pointer, stack, registers
    popped = stack.pop()
    registers[str(operand)] = popped
    stack_pointer = stack_pointer + 2 


# Perform comparison with A-operand and set flag accordingly.
# CC set => SF, ZF, CF
def cmp(mode, operand):
    #print("Mode: ", mode, "\t Operand: ", decimalToHex(operand))
    global registers, memory, zf, cf, sf
    tempA = hexToDecimal(registers['1'])
    if mode == 0:
        tempA = tempA + ~(operand) + 1
    elif mode == 1:
        tempA = tempA + ~(hexToDecimal(registers[str(operand)])) + 1
    elif mode == 2:
        tempA = tempA + ~(hexToDecimal(memory[registers[str(operand)]])) + 1
    else:
        tempA = tempA + ~(hexToDecimal(memory[decimalToHex(operand)])) + 1
    if tempA > unsignedMAX:
        tempA = tempA - unsignedMAX
        cf = 1
    else:
        cf = 0
    if tempA == 0:
        zf = 1
    else:
        zf = 0
    if utos(tempA) < 0:
        sf = 1
    else:
        sf = 0


# Unconditional jump. Set PC to address.
def jmp(mode, address):
    global program_counter, registers, memory
    tempA = 0
    if mode == 0:
        tempA = address
    elif mode == 1:
        tempA = hexToDecimal(registers[str(address)])
    elif mode == 2:
        tempA = hexToDecimal(memory[registers[str(address)]])
    else:
        tempA = hexToDecimal(memory[decimalToHex(address)])
    program_counter = decimalToHex(tempA)


# Prints the operand as a character.
def printchar(mode, operand):
    #print("Mode: ", mode, "\t Operand: ", decimalToHex(operand))
    global registers, memory
    if mode == 0:
        print(chr(operand))
    elif mode == 1:
        print(chr(hexToDecimal(registers[str(operand)])))
    elif mode == 2:
        print(chr(hexToDecimal(memory[registers[str(operand)]])))
    else:
        print(chr(hexToDecimal(memory[decimalToHex(operand)])))
    

# Reads a character into the operand.
def readchar(mode, operand):
    global registers, memory
    val = input()
    if mode == 1:
        registers[str(operand)] = decimalToHex(ord(val))
    elif mode == 2:
        memory[registers[str(operand)]] = decimalToHex(ord(val))
    else:
        memory[decimalToHex(operand)] = decimalToHex(ord(val))


if len(sys.argv) != 2: print('usage: executor.py <sourcefile>'); sys.exit(1)
f = open(sys.argv[1], 'r')
counter = 0x0
while True:  # read in the source line
    line = f.readline()
    if not line: break
    lines.append(line.strip())  # store each line without leading/trailing whitespaces

    ## Here the instructions are saved in the memory in hex
    memory[decimalToHex(counter)] = line.strip()
    counter = counter + 3
f.close()


while True:
    #print("PC:", program_counter)
    #print("CF:", cf, "\tZF:", zf, "\tSF:", sf)
    #print(registers)
    #print(memory)
    opcode, mode, operand = parseBits(memory[program_counter])
    hexOpCode = binaryToHex(opcode).upper()
    modeInt = int(mode,2)
    operandInt = int(operand,2)
    # HALT
    if hexOpCode == '01':
        break
    elif hexOpCode == '02':
        load(modeInt, operandInt)
    elif hexOpCode == '03':
        store(modeInt, operandInt)
    elif hexOpCode == '04':
        add(modeInt, operandInt)
    elif hexOpCode == '05':
        sub(modeInt, operandInt)
    elif hexOpCode == '06':
        inc(modeInt, operandInt)
    elif hexOpCode == '07':
        dec(modeInt, operandInt)
    elif hexOpCode == '08':
        xor(modeInt, operandInt)
    elif hexOpCode == '09':
        andd(modeInt, operandInt)
    elif hexOpCode == '0A':
        orr(modeInt, operandInt)
    elif hexOpCode == '0B':
        nott(modeInt, operandInt)
    elif hexOpCode == '0C':
        shl(modeInt, operandInt)
    elif hexOpCode == '0D':
        shr(modeInt, operandInt)
    elif hexOpCode == '0E':
        nop()
    elif hexOpCode == '0F':
        pushh(modeInt, operandInt)
    elif hexOpCode == '10':
        popp(modeInt, operandInt)
    elif hexOpCode == '11':
        cmp(modeInt, operandInt)
    elif hexOpCode == '12':
        jmp(modeInt, operandInt)
        continue
    elif hexOpCode == '13':
        if zf == 1:
            jmp(modeInt, operandInt)
            continue
    elif hexOpCode == '14':
        if zf == 0:
            jmp(modeInt, operandInt)
            continue
    elif hexOpCode == '15':
        if cf == 1:
            jmp(modeInt, operandInt)
            continue
    elif hexOpCode == '16':
        if cf == 0:
            jmp(modeInt, operandInt)
            continue
    elif hexOpCode == '17':
        if cf == 0 and zf == 0:
            jmp(modeInt, operandInt)
            continue
    elif hexOpCode == '18':
        if cf == 0:
            jmp(modeInt, operandInt)
            continue
    elif hexOpCode == '19':
        if cf == 1:
            jmp(modeInt, operandInt)
            continue
    elif hexOpCode == '1A':
        if cf == 1 or zf == 1:
            jmp(modeInt, operandInt)
            continue
    elif hexOpCode == '1B':
        readchar(modeInt, operandInt)
    elif hexOpCode == '1C':
        printchar(modeInt,operandInt)
    program_counter = decimalToHex(int(program_counter,16) + 3).zfill(4)
