.ORIG x2000
;-------------------
ST R0,saveR0
ST R1,saveR1
ST R2,saveR2
ST R3,saveR3
ST R4,saveR4
ST R5,saveR5
ST R6,saveR6
ST R7,saveR7
;-------------------
LD R5,enter
NOT R5,R5
ADD R5,R5,1
LD R2,stringsave
START   LDI R3,KBSR
	BRzp START
LDI R0,KBDR
ADD R4,R0,R5
BRz begin
STR R0,R2,0
ADD R2,R2,1
BRnzp START


begin
	LDI R0,KBDR
	STR R0,R2,0
  	LD R1,ten
show 	BRz end
	LD R3,stringsave	
START2  LDI R2,DSR
	BRZP START2
	LDR R0,R3,0
	ADD R3,R3,1
	ADD R4,R0,R5
	BRz next
	STI R0,DDR
	BRnzp START2
next	ADD R1,R1,-1
	BRnzp show
end 	LD R0,saveR0
	LD R1,saveR1
	LD R2,saveR2
	LD R3,saveR3
	LD R4,saveR4
	LD R5,saveR5
	LD R6,saveR6
	LD R7,saveR7	
	RTI		 


HALT
ten .FILL #10
saveR0 .FILL 0
saveR1 .FILL 0
saveR2 .FILL 0
saveR3 .FILL 0
saveR4 .FILL 0
saveR5 .FILL 0
saveR6 .FILL 0
saveR7 .FILL 0
enter .FILL x0A
KBSR .FILL xFE00
KBDR .FILL xFE02
DSR .FILL xFE04
DDR .FILL xFE06
change .FILL x4000
stringsave .FILL x5000
.END