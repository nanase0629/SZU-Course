.data
arr: .word 8, 6, 3, 7, 1, 0, 9, 4, 5, 2  # 初始化待排序的数组
before: .asciiz "Before sort the array is:\n"  # 排序前的提示信息
after: .asciiz "After sort the array is:\n"  # 排序后的提示信息

.text
main:
    # 打印排序前的数组
    la a0, before
    jal print_str

    # 打印原始数组
    li a1, 10  # 设置数组长度n为10
    li a2, 0  # 初始化循环变量i为0
print1:
    sll a3, a2, 3  # 计算数组索引，a3 = i * 8
    lw a0, arr(a3)  # 加载arr[i]到a0
    jal print_int
    addi a2, a2, 1  # i++
    bne a2, a1, print1  # 如果i不等于n，则继续循环

    # 调用快速排序
    li a0, 0  # 设置参数1：数组起始索引
    addi a1, a1, -1  # 设置参数2：数组结束索引
    jal quick_sort

    # 打印排序后的数组
    la a0, after
    jal print_str

    # 再次打印数组
    li a1, 10  # 设置数组长度n为10
    li a2, 0  # 初始化循环变量i为0
print2:
    sll a3, a2, 3  # 计算数组索引，a3 = i * 8
    lw a0, arr(a3)  # 加载arr[i]到a0
    jal print_int
    addi a2, a2, 1  # i++
    bne a2, a1, print2  # 如果i不等于n，则继续循环

    # 停止程序执行
    li a0, 10
    ecall

# 快速排序子程序
quick_sort:
    # 参数：a0 - 起始索引，a1 - 结束索引
    addi sp, sp, -32  # 分配栈空间
    sd ra, 0(sp)  # 保存返回地址
    sd a0, 8(sp)  # 保存起始索引
    sd a1, 16(sp)  # 保存结束索引

    # 基本情况
    slt t0, a0, a1
    beqz t0, quick_sort_exit

    # 设置支点
    lw t1, arr(a0)
    addi t2, a0, -1

    # 分区操作
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

    # 递归排序左半部分
    move a1, t2
    jal quick_sort

    # 递归排序右半部分
    move a0, t7
    ld a1, 16(sp)
    jal quick_sort

quick_sort_exit:
    ld ra, 0(sp)  # 恢复返回地址
    addi sp, sp, 32  # 恢复栈空间
    jr ra

# 打印整数子程序
print_int:
    li a7, 1
    ecall
    jr ra

# 打印字符串子程序
print_str:
    li a7, 4
    ecall
