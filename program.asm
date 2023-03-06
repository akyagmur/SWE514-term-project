    LOAD 'A'
    STORE C
    LOAD MYDATA
    STORE B
    LOAD 0004
    STORE D
    NOP
LOOP1:
    PRINT C
    LOAD C
    STORE [B]
    INC C
    INC B
    INC B
    DEC D
    NOP
    JNZ LOOP1
    READ E
    PRINT E
    HALT
MYDATA: