.data
CONTROL: .word 0x10000  # ���ƼĴ����ĵ�ַ
DATA: .word 0x10008  # ���ݼĴ����ĵ�ַ
INPUT: .asciiz "please enter two numbers:\n"
OUTPUT: .asciiz "result:\n"
WARNING: .asciiz "warning: result overflow\n"

# ���ƼĴ���:r8�����ݼĴ���:r9����������:r10��������:r11 
# ��������1����������:r16����������2��������:r17���������(�˻�):r18
# ѭ������:r20��ѭ���߽�:r21��ѭ�������ж�:r22
# �ж�:r24
.text
main:
# �����źź����ݵ�ַ
lwu r8, CONTROL(r0)
lwu r9, DATA(r0)

# ����������ͣ�������
daddi r10, r0, 4
daddi r11, r0, INPUT

# �����ʾ���
sd r11, (r9)
sd r10, (r8)

# ��ȡ��������1
daddi r10, r0,8
sd r10, (r8)
ld r16, (r9)

# ��ȡ��������2
daddi r10, r0,8
sd r10, (r8)
ld r17, (r9)

# ��ʼ���˻�Ϊ0��ѭ�����Ʊ���iΪ0��ѭ������n=32
daddi r18, r0, 0
daddi r20, r0, 0
daddi r21, r0, 32

LOOP:
# for(int i=0;i<32;i++)
slt r22, r20, r21 
beq r22, r0, END
daddi r20, r20, 1

# �жϳ������λ�Ƿ�Ϊ1�������򽫱������ӵ��˻���
andi r24, r17, 1
beq r24, r0, MOVE
dadd r18, r18, r16

# ��λ������������һλ����������һλ
MOVE:
dsll r16, r16, 1
dsra r17, r17, 1
j LOOP

# ��������Ϣ
END:
daddi r10, r0, 4
daddi r11, r0, OUTPUT
sd r11, (r9)
sd r10, (r8)

# ����˻�
daddi r10, r0, 2
sw r18, (r9)
sd r10, (r8)

# �ж��Ƿ�������������˻�������32λ�ж��Ƿ�Ϊ0
dadd r24, r0, r18
dsll r24, r24, 16
dsll r24, r24, 16
beq r24, r0, EEND

# �������������������Ϣ
daddi r10, r0, 4
daddi r11, r0, WARNING
sd r11, (r9)
sd r10, (r8)

EEND:
halt
