.ORIG x3000 
TRAP x23 ;the trap instruction which is also known as "IN" 
ADD R1,R0,x0 ;move the first integer to register 1 
TRAP x23 ;another "IN" 
ADD R2��R0��R1 ;����������� 
LEA R0��MESG ;�����ַ����ĵ�ַ 
TRAP x22 ;����ַ��� 
ADD R0��R2��x0 ;sum ���浽 R0 �У���׼����� 
TRAP x21 ;��ʾ��� 
HALT 
MESG .STRINGZ ��The sum of those two numbers is�� 
.END