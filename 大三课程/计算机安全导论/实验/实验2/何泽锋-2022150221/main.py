import random
import math
import time
from sympy import isprime, randprime
from random import randint
import sys
import hashlib

sys.setrecursionlimit(100000)


# 求最大公约数-2022150221
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


# 判断是否为素数-2022150221
def is_prime(x):
    if x < 2:
        return False
    for i in range(2, int(math.sqrt(x)) + 1):
        if x % i == 0:
            return False
    return True


# 扩展欧几里得算法-2022150221
def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    gcd, y1, x1 = extended_gcd(b, a % b)
    y1 = y1 - (a // b) * x1
    return gcd, x1, y1


# 求乘法逆元-2022150221
def mod_inverse(e, phi_n):
    gcd, x, _ = extended_gcd(e, phi_n)
    if gcd != 1:
        return None  # 无逆元
    else:
        return x % phi_n


# 生成公钥和私钥-2022150221
def generate_keys(bit_length=8):
    # 生成两个大素数p和q
    p = randprime(2 ** (bit_length - 1), 2 ** bit_length)
    q = randprime(2 ** (bit_length - 1), 2 ** bit_length)
    # 去重
    while q == p:
        q = randprime(2 ** (bit_length - 1), 2 ** bit_length)

    n = p * q
    phi_n = (p - 1) * (q - 1)

    # 选择e，它必须是1和phi_n之间的一个整数，且与phi_n互质
    e = randint(1, (phi_n - 1))
    while gcd(e, phi_n) != 1:
        e = randint(1, (phi_n - 1))
    # 计算e模phi_n的逆元d
    d = mod_inverse(e, phi_n)

    return (e, n), (d, n)


# 快速幂-2022150221
def fast_pow(a, exp, mod):
    res = 1
    while exp > 0:
        if exp & 1:
            res = (res * a) % mod
        a = (a * a) % mod
        exp >>= 1
    return res


# 加密-2022150221
def encrypt(value, e, n):
    return fast_pow(value, e, n)


# 解密-2022150221
def decrypt(value, d, n):
    return fast_pow(value, d, n)


# 记录添加的位数-2022150221
A = 0


# 读取文件并加密-2022150221
def encoder(input_file, output_file, e, n, bit=8):
    global A
    integers = []
    with open(input_file, 'rb+') as file:
        byte = file.read()

        s = ""  # 初始化一个变量来存储拼接后的二进制字符串

        # 将每个字节转换为二进制字符串，并拼接起来
        for b in byte:
            # 将字节转换为二进制字符串，去掉前缀'0b'，并确保每个字节是8位
            binary_str = format(b, '08b')
            s += binary_str  # 拼接二进制字符串

        # 检查拼接后的字符串长度是否是bit位的倍数，如果不是，则补0
        while len(s) % bit != 0:
            A += 1
            s = s + '0'

        groups = [s[i:i + bit] for i in range(0, len(s), bit)]
        with open(output_file, 'w', encoding="utf-8") as f:
            for group in groups:
                number = int(group, 2)
                cipher = encrypt(number, e, n)
                s = str(cipher)
                f.write(s + " ")


# 读取文件并解密-2022150221
def decoder(input_file, output_file, d, n, bit=8):
    global A
    with open(input_file, 'r') as infile, open(output_file, 'wb') as outfile:
        content = infile.read()
        elements = content.split()
        for index, number_str in enumerate(elements):
            number = int(number_str)
            plain_number = decrypt(number, d, n)  # 字符的ascll码
            binary_str = bin(plain_number)[2:].zfill(bit)  # 2进制表达

            try:
                # 每bit位二进制字符串转换为1个字节
                if (index == len(elements) - 1) and (A != 0):
                    binary_str = binary_str[:-A]
                    Intnum = int(binary_str, 2)
                    outfile.write(Intnum.to_bytes((bit - A) // 8, byteorder='big'))
                else:
                    Intnum = int(binary_str, 2)
                    outfile.write(Intnum.to_bytes(bit // 8, byteorder='big'))
            except OverflowError:
                # 如果出现OverflowError，输出公钥错误
                print("密钥错误,无法解密")
                sys.exit()


# RSA加密并解密过程-2022150221
def RSA(input_file, signature_file, cipher_file, output_file, bit):
    public_key, private_key = generate_keys(bit)
    e, n = public_key
    d, n = private_key

    print(f"公钥(e, n)：({e}, {n})")
    print(f"私钥(d, n)：({d}, {n})")

    # 加密
    encoder(input_file, cipher_file, e, n, bit)
    print("公钥加密完成")
    # 解密
    decoder(cipher_file, output_file, d, n, bit)
    print("私钥解密完成")


# 记录文件摘要-2022150221
signature = ''
# 记录解密签名的摘要-2022150221
de_signature = ''


# 获取文件摘要并写入摘要文件中-2022150221
def abstract(input, output):
    global signature
    with open(input, 'r', encoding='utf-8') as file:
        content = file.read()
        sha = hashlib.sha512()
        sha.update(content.encode('utf-8'))
        signature = sha.hexdigest()

    with open(output, 'w', encoding='utf-8') as file:
        file.write(signature)


# 读取解密摘要-2022150221
def decoder_abstract(input):
    global de_signature
    with open(input, 'r+', encoding='utf-8') as file:
        content = file.read()
        de_signature = content


# 完整数字签名验证过程2022150221
def digital_signature(input_file, signature_file, cipher_file, output_file, bit):
    public_key, private_key = generate_keys(bit)
    e, n = public_key
    d, n = private_key

    print(f"公钥(e, n)：({e}, {n})")
    print(f"私钥(d, n)：({d}, {n})")

    abstract(input_file, signature_file)
    encoder(signature_file, cipher_file, d, n, bit)
    print("私钥签名完成")

    decoder(cipher_file, output_file, e, n, bit)
    print("公钥解密完成")
    decoder_abstract(output_file)
    print("摘要S ：", signature)
    print("摘要S‘：", de_signature)
    if signature == de_signature:
        print("签名验证成功")
    else:
        print("签名验证失败")


# 主函数-2022150221
def main():
    input_file = "2022150221何泽锋原始文件.txt"
    cipher_file = "2022150221何泽锋加密文件.txt"
    output_file = "2022150221何泽锋解密文件.txt"
    signature_file = "2022150221何泽锋哈希文件.txt"

    # RSA加密并解密文件
    # RSA(input_file, signature_file, cipher_file, output_file, 1024)
    # 数字签名
    digital_signature(input_file, signature_file, cipher_file, output_file, 1024)


if __name__ == "__main__":
    main()
