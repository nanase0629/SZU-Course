.ORIG x3000 
TRAP x23 ;the trap instruction which is also known as "IN" 
ADD R1,R0,x0 ;move the first integer to register 1 
TRAP x23 ;another "IN" 
ADD R2，R0，R1 ;两个整数相加 
LEA R0，MESG ;载入字符串的地址 
TRAP x22 ;输出字符串 
ADD R0，R2，x0 ;sum 保存到 R0 中，并准备输出 
TRAP x21 ;显示结果 
HALT 
MESG .STRINGZ “The sum of those two numbers is” 
.END