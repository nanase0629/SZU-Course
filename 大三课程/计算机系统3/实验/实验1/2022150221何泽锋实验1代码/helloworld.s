.data
string: .asciiz "Hello World!"
CONTROL: .word32 0x10000
DATA: .word32 0x10008

.text
main:
    lwu r23, DATA(r0)  # ��M[0x10000]����r23
	daddi r24, r0, string  # r24���ַ����׵�ַ
	sd r24, (r23)  # ���ַ����׵�ַ�浽DATA��
	
	lwu r23, CONTROL(r0)  # ��M[0x10000]����r23
	daddi r24, r0, 4  # r24 = 4
	sd r24, (r23)  # ����CONTROL = 4
	
	halt