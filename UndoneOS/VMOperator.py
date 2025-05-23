#VMOperator
#Talmage Gaisford

class VMOperator:
    #Arithmetic
    ADD = 16
    SUB = 17
    MUL = 18
    DIV = 19

    #Move Data
    MOV = 1
    MVI = 22
    ADR = 0
    STR = 2
    STRB = 3
    LDR = 4
    LDRB = 5

    #Branch
    B = 7
    BL = 21
    BX = 6
    BNE = 8
    BGT = 9
    BLT = 10
    BEQ = 11

    #Logical
    CMP = 12
    AND = 13
    ORR = 14
    EOR = 15

    #Interrupts
    SWI = 20

class SWIOperator:
    INTERRUPT = 1
    PRINT = 2
    FORK = 3
    SHAREDPUSH = 4
    SHAREDPULL = 5