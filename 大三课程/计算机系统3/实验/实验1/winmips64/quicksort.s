.data
arr: .word 8, 6, 3, 7, 1, 0, 9, 4, 5, 2  # ��ʼ�������������
before: .asciiz "Before sort the array is:\n"  # ����ǰ����ʾ��Ϣ
after: .asciiz "After sort the array is:\n"  # ��������ʾ��Ϣ

.text
main:
    # ��ӡ����ǰ������
    la a0, before
    jal print_str

    # ��ӡԭʼ����
    li a1, 10  # �������鳤��nΪ10
    li a2, 0  # ��ʼ��ѭ������iΪ0
print1:
    sll a3, a2, 3  # ��������������a3 = i * 8
    lw a0, arr(a3)  # ����arr[i]��a0
    jal print_int
    addi a2, a2, 1  # i++
    bne a2, a1, print1  # ���i������n�������ѭ��

    # ���ÿ�������
    li a0, 0  # ���ò���1��������ʼ����
    addi a1, a1, -1  # ���ò���2�������������
    jal quick_sort

    # ��ӡ����������
    la a0, after
    jal print_str

    # �ٴδ�ӡ����
    li a1, 10  # �������鳤��nΪ10
    li a2, 0  # ��ʼ��ѭ������iΪ0
print2:
    sll a3, a2, 3  # ��������������a3 = i * 8
    lw a0, arr(a3)  # ����arr[i]��a0
    jal print_int
    addi a2, a2, 1  # i++
    bne a2, a1, print2  # ���i������n�������ѭ��

    # ֹͣ����ִ��
    li a0, 10
    ecall

# ���������ӳ���
quick_sort:
    # ������a0 - ��ʼ������a1 - ��������
    addi sp, sp, -32  # ����ջ�ռ�
    sd ra, 0(sp)  # ���淵�ص�ַ
    sd a0, 8(sp)  # ������ʼ����
    sd a1, 16(sp)  # �����������

    # �������
    slt t0, a0, a1
    beqz t0, quick_sort_exit

    # ����֧��
    lw t1, arr(a0)
    addi t2, a0, -1

    # ��������
partition:
    addi t3, a0, -1
    addi t4, a1, 1
partition_loop:
    addi t3, t3, 1
partition_loop1:
    lw t5, arr(t3)
    slt t6, t5, t1
    bnez t6, partition_loop1
    addi t4, t4, -1
partition_loop2:
    lw t5, arr(t4)
    slt t6, t1, t5
    bnez t6, partition_loop2
    slt t6, t3, t4
    beqz t6, partition_exit
    sw t5, arr(t3)
    sw t5, arr(t4)
    j partition_loop

partition_exit:
    sw t1, arr(t4)
    addi t7, t4, 1

    # �ݹ�������벿��
    move a1, t2
    jal quick_sort

    # �ݹ������Ұ벿��
    move a0, t7
    ld a1, 16(sp)
    jal quick_sort

quick_sort_exit:
    ld ra, 0(sp)  # �ָ����ص�ַ
    addi sp, sp, 32  # �ָ�ջ�ռ�
    jr ra

# ��ӡ�����ӳ���
print_int:
    li a7, 1
    ecall
    jr ra

# ��ӡ�ַ����ӳ���
print_str:
    li a7, 4
    ecall
