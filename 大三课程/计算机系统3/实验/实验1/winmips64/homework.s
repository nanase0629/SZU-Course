    
.text
    lw    r1, 0(r2)   # 将内存中地址为$r2的值加载到$r1
Loop:   daddi  r1,r1, 4  # 将$r1的值增加4
    sw    r1, 0(r2)   # 将$r1的值存储回内存地址$r2
    daddi  r2,r2, 4   # 将$r2的值增加4，指向下一个内存地址
    dsub   r4,r3, r2  # 计算$r3和$r2的差，结果存储在$r4
    bnez  r4, Loop     # 如果$r4不为0，则跳转到Loop继续执行
    lw    r1, 0(r2)   # 循环结束后，将内存中地址为$r2的值加载到$r1

    halt