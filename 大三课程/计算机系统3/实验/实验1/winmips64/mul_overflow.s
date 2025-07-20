.data
CONTROL: .word 0x10000  # 控制寄存器的地址
DATA: .word 0x10008  # 数据寄存器的地址
INPUT: .asciiz "please enter two numbers:\n"
OUTPUT: .asciiz "result:\n"
WARNING: .asciiz "warning: result overflow\n"

# 控制寄存器:r8，数据寄存器:r9，控制类型:r10，输出语句:r11 
# 输入数据1（被乘数）:r16，输入数据2（乘数）:r17，输出数据(乘积):r18
# 循环控制:r20，循环边界:r21，循环跳出判断:r22
# 判断:r24
.text
main:
# 控制信号和数据地址
lwu r8, CONTROL(r0)
lwu r9, DATA(r0)

# 设置输出类型，输出语句
daddi r10, r0, 4
daddi r11, r0, INPUT

# 输出提示语句
sd r11, (r9)
sd r10, (r8)

# 读取输入数据1
daddi r10, r0,8
sd r10, (r8)
ld r16, (r9)

# 读取输入数据2
daddi r10, r0,8
sd r10, (r8)
ld r17, (r9)

# 初始化乘积为0，循环控制变量i为0，循环次数n=32
daddi r18, r0, 0
daddi r20, r0, 0
daddi r21, r0, 32

LOOP:
# for(int i=0;i<32;i++)
slt r22, r20, r21 
beq r22, r0, END
daddi r20, r20, 1

# 判断乘数最低位是否为1，若是则将被乘数加到乘积中
andi r24, r17, 1
beq r24, r0, MOVE
dadd r18, r18, r16

# 移位，被乘数左移一位，乘数右移一位
MOVE:
dsll r16, r16, 1
dsra r17, r17, 1
j LOOP

# 输出结果信息
END:
daddi r10, r0, 4
daddi r11, r0, OUTPUT
sd r11, (r9)
sd r10, (r8)

# 输出乘积
daddi r10, r0, 2
sw r18, (r9)
sd r10, (r8)

# 判断是否有溢出，拷贝乘积，右移32位判断是否为0
dadd r24, r0, r18
dsll r24, r24, 16
dsll r24, r24, 16
beq r24, r0, EEND

# 若出现溢出则输出溢出信息
daddi r10, r0, 4
daddi r11, r0, WARNING
sd r11, (r9)
sd r10, (r8)

EEND:
halt
