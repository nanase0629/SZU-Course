.data
arr: .word 8, 6, 3, 7, 1, 0, 9, 4, 5, 2  # 初始化待排序的数组
before: .asciiz "Before sort the array is:\n"  # 排序前的提示信息
after: .asciiz "After sort the array is:\n"  # 排序后的提示信息
CONTROL: .word 0x10000  # 控制寄存器的地址
DATA: .word 0x10008  # 数据寄存器的地址
SP: .word 0x300  # 栈指针的初始值

.text
main:
    # 打印排序前的数组
    ld r16, CONTROL(r0)  # 加载控制寄存器的地址到r16
    ld r17, DATA(r0)  # 加载数据寄存器的地址到r17
    daddi r8, r0, 4  # 设置控制码为4，用于打印字符串
    daddi r9, r0, before  # 获取"Before sort"字符串的地址
    sd r9, (r17)  # 将字符串地址放入数据寄存器
    sd r8, (r16)  # 执行打印操作

    # 打印原始数组
    daddi r8, r0, 2  # 设置控制码为2，用于打印整数
    daddi r2, r0, 10  # 设置数组长度n为10
    daddi r1, r0, 0  # 初始化循环变量i为0
print1:
    dsll r3, r1, 3  # 计算数组索引，r3 = i * 8
    ld r9, arr(r3)  # 加载arr[i]到r9
    sd r9, (r17)  # 将arr[i]放入数据寄存器
    sd r8, (r16)  # 执行打印操作
    daddi r1, r1, 1  # i++
    bne r1, r2, print1  # 如果i不等于n，则继续循环

    # 调用冒泡排序
    ld r29, SP(r0)  # 加载栈指针到r29
    daddi r4, r0, arr  # 设置参数1：数组地址
    daddi r5, r0, 10  # 设置参数2：数组长度
    jal bubbleSort  # 跳转到bubbleSort子程序

    # 打印排序后的数组
    daddi r8, r0, 4  # 设置控制码为4，用于打印字符串
    daddi r9, r0, after  # 获取"After sort"字符串的地址
    sd r9, (r17)  # 将字符串地址放入数据寄存器
    sd r8, (r16)  # 执行打印操作

    # 再次打印数组
    daddi r8, r0, 2  # 设置控制码为2，用于打印整数
    daddi r2, r0, 10  # 设置数组长度n为10
    daddi r1, r0, 0  # 初始化循环变量i为0
print2:
    dsll r3, r1, 3  # 计算数组索引，r3 = i * 8
    ld r9, arr(r3)  # 加载arr[i]到r9
    sd r9, (r17)  # 将arr[i]放入数据寄存器
    sd r8, (r16)  # 执行打印操作
    daddi r1, r1, 1  # i++
    bne r1, r2, print2  # 如果i不等于n，则继续循环
    halt  # 停止程序执行

# 冒泡排序子程序
bubbleSort:
    # 备份寄存器
    daddi r29, r29, -24  # r29 <- r29 - 24, 为3个整数分配栈帧空间
    sd $ra, 16(r29)      # 保存返回地址到栈上
    sd r16, 8(r29)       # 保存r16到栈上
    sd r17, 0(r29)       # 保存r17到栈上

    dadd r22, r4, r0     # r22 <- r4 + r0, r22 = a[] (数组首地址)
    daddi r23, r5, 0     # r23 <- r5 + 0, r23 = n (数组长度)

    and r18, r18, r0     # r18 <- r18 & r0, 初始化i为0
loop1:
    # 外层循环: for (int i = 0; i < n; i++)
    slt r10, r18, r23    # 如果r18 < r23，则设置r10为1，继续循环
    beq r10, r0, end1    # 如果r10 == 0，则跳转到end1，结束外层循环

    daddi r19, r18, -1   # r19 <- r18 - 1, 初始化j为i - 1
loop2:
    # 内层循环: for (int j = i - 1; j >= 0; j--)
    slti r10, r19, 0     # 如果r19 < 0，则设置r10为1，跳出内层循环
    bne r10, r0, end2    # 如果r10 != 0，则跳转到end2，结束内层循环

    dsll r11, r19, 3     # r11 <- r19 << 3, 计算j * 8的偏移量
    dadd r12, r22, r11   # r12 <- r22 + r11, r12 = &a[j]
    ld r13, 0(r12)       # r13 <- M[r12], r13 = a[j]
    ld r14, 8(r12)       # r14 <- M[r12 + 8], r14 = a[j + 1]

    # 如果a[j] > a[j + 1]，则交换a[j]和a[j + 1]
    slt r10, r14, r13    # 如果r14 < r13，则设置r10为1，表示需要交换
    beq r10, r0, end2    # 如果r10 == 0，则跳转到end2，不交换

    # 调用交换函数
    dadd r4, r0, r12     # r4 <- r12, 传递参数a + j * 8
    daddi r5, r12, 8     # r5 <- r12 + 8, 传递参数a + (j + 1) * 8
    jal swap             # 跳转到swap函数

    daddi r19, r19, -1   # r19 <- r19 - 1, j--
    j loop2              # 跳转到loop2继续内层循环

end2:
    daddi r18, r18, 1    # r18 <- r18 + 1, i++
    j loop1              # 跳转到loop1继续外层循环

end1:
    # 恢复寄存器
    ld r17, 0(r29)       # 恢复r17
    ld r16, 8(r29)       # 恢复r16
    ld $ra, 16(r29)      # 恢复返回地址
    daddi r29, r29, 24   # 恢复栈帧空间
    jr $ra               # 返回到调用者

# 交换函数
swap:
    # 交换a[i]和a[j]
    ld r9, 0(r4)         # r9 <- M[r4], r9 = a[i]
    ld r10, 0(r5)        # r10 <- M[r5], r10 = a[j]
    sd r10, 0(r4)        # M[r4] <- r10, a[i] = r10
    sd r9, 0(r5)         # M[r5] <- r9, a[j] = r
    jr $ra               # 返回