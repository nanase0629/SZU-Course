.data
str:  .asciiz "the data of matrix 2:\n"
mx1:   .space 32  # 2x2������Ҫ32�ֽڵĿռ�
mx2:   .space 32
mx3:   .space 32

.text
initial:     
            daddi r22,r0,mx1  # ���initialģ���Ǹ��������󸳳�ֵ
            daddi r23,r0,mx2
            daddi r21,r0,mx3
input:      
            daddi r9,r0,4     # 2x2������4��Ԫ��
            daddi r8,r0,0
loop1:      
            dsll r11,r8,3
            dadd r10,r11,r22
            dadd r11,r11,r23
            daddi r12,r0,2
            daddi r13,r0,3
            sd r12,0(r10)
            sd r13,0(r11)

            daddi r8,r8,1
            slt r10,r8,r9
            bne r10,r0,loop1

mul:        
            daddi r16,r0,2    # 2x2����Ĵ�С
            daddi r17,r0,0
loop2:        
            daddi r18,r0,0    # ���ѭ����ִ��for(int i = 0, i < 2; i++)������
loop3:        
            daddi r19,r0,0    # ���ѭ����ִ��for(int j = 0, j < 2; j++)������
            daddi r20,r0,0    # r20�洢�ڼ���result[i][j]������ÿ���˷�����ĵ���ֵ
loop4:        
            dsll r8,r17,3     # ���ѭ����ִ�м���ÿ��result[i][j]
            dsll r9,r19,3
            dadd r8,r8,r9
            dadd r8,r8,r22
            ld r10,0(r8)      # ȡmx1[i][k]��ֵ
            dsll r8,r19,3
            dsll r9,r18,3
            dadd r8,r8,r9
            dadd r8,r8,r23
            ld r11,0(r8)      # ȡmx2[k][j]��ֵ
            dmul r13,r10,r11  # mx1[i][k]��mx2[k][j]���
            dadd r20,r20,r13  # �м����ۼ�

            daddi r19,r19,1
            slt r8,r19,r16
            bne r8,r0,loop4

            dsll r8,r17,3
            dsll r9,r18,3
            dadd r8,r8,r9
            dadd r8,r8,r21    # ����result[i][j]��λ��
            sd r20,0(r8)      # ���������result[i][j]��

            daddi r18,r18,1
            slt r8,r18,r16
            bne r8,r0,loop3

            daddi r17,r17,1
            slt r8,r17,r16
            bne r8,r0,loop2   

            halt
