.data
string: .asciiz "Hello World!"
CONTROL: .word32 0x10000
DATA: .word32 0x10008

.text
main:
    lwu r23, DATA(r0)  # 将M[0x10000]存入r23
	daddi r24, r0, string  # r24存字符串首地址
	sd r24, (r23)  # 将字符串首地址存到DATA区
	
	lwu r23, CONTROL(r0)  # 将M[0x10000]存入r23
	daddi r24, r0, 4  # r24 = 4
	sd r24, (r23)  # 设置CONTROL = 4
	
	halt