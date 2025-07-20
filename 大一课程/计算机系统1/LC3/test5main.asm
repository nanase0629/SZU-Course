.ORIG    x3000
;------------------------------ initialize the stack pointer
LD R6,sp

;------------------------------ set up the keyboard interrupt vector table entry
LD R1,locatex0180
LD R2,newlocate
STR R2,R1,0   

;------------------------------ enable keyboard interrupts
LD R1,change
STI R1,KBSR   
   
;------------------------------ start of actual user program to print ICS checkerboard
print   LEA R0,Line1
	PUTS
	JSR DELAY
	LEA R0,Line2
	PUTS
	JSR DELAY
	BRnzp print
        
;------------------------------ 数据区
HALT
KBSR .FILL xFE00
KBDR .FILL xFE02
DSR .FILL xFE04
DDR .FILL xFE06
change .FILL x4000
sp .FILL x3000
locatex0180 .FILL x0180
newlocate .FILL x2000
Line1 .STRINGZ "ICS   ICS   ICS   ICS   ICS   ICS\n"
Line2 .STRINGZ "   ICS   ICS   ICS   ICS   ICS\n"
;------------------------------ 减速程序
DELAY   ST  R1, SaveR1
        LD  R1, COUNT
REP     ADD R1,R1,#-1
        BRp REP
        LD  R1, SaveR1
        RET
COUNT   .FILL #2500
SaveR1  .BLKW 1

.END
