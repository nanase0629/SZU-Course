import os
import time
import math
import struct
from collections import Counter
from fractions import Fraction
from PIL import Image


# ====================== 位操作工具类 ======================

class BitWriter:
    """用于按位写入数据的工具类"""

    def __init__(self):
        self.buffer = bytearray()  # 存储字节数据
        self.current_byte = 0  # 当前正在组装的字节
        self.bits_count = 0  # 当前字节已填充的位数

    def write_bit(self, bit):
        """写入单个bit"""
        self.current_byte = (self.current_byte << 1) | (bit & 1)  # 将当前字节左移1位，腾出最低位存储新bit
        self.bits_count += 1  # 位数计数加1

        # 满8位就写入缓冲区
        if self.bits_count == 8:
            self.buffer.append(self.current_byte)
            self.current_byte = 0
            self.bits_count = 0

    def write_bits(self, bits_str):
        """写入一串二进制字符串"""
        for bit in bits_str:  # 将字符转换为0/1整数，调用单bit写入方法
            self.write_bit(1 if bit == '1' else 0)

    def write_int(self, num, bit_length):
        """按指定bit长度写入整数"""
        for i in range(bit_length):  # 从最高位到最低位依次提取每一位
            bit = (num >> (bit_length - 1 - i)) & 1
            self.write_bit(bit)

    def flush(self):
        """将不满8位的剩余bits写入缓冲区"""
        if self.bits_count > 0:  # 左移补0，使当前字节填满8位
            self.current_byte <<= (8 - self.bits_count)
            self.buffer.append(self.current_byte)
            self.current_byte = 0
            self.bits_count = 0

    def get_bytes(self):
        """获取最终的字节数据"""
        return bytes(self.buffer)


class BitReader:
    """用于按位读取数据的工具类"""

    def __init__(self, data):
        self.data = data  # 原始字节数据
        self.pos = 0  # 当前读取位置
        self.current_byte = 0  # 当前正在读取的字节
        self.bits_left = 0  # 当前字节剩余的bits数

    def read_bit(self):
        """读取单个bit"""
        if self.bits_left == 0:
            if self.pos >= len(self.data):
                return None
            self.current_byte = self.data[self.pos]
            self.pos += 1
            self.bits_left = 8

        self.bits_left -= 1
        return (self.current_byte >> self.bits_left) & 1

    def read_bits(self, n):
        """读取n位bits并返回整数"""
        value = 0
        for _ in range(n):
            bit = self.read_bit()
            if bit is None:
                break
            value = (value << 1) | bit
        return value


# ====================== 压缩算法基类 ======================

class CompressorBase:
    """压缩算法基类，定义统一接口"""

    def compress_channel(self, channel_data):
        """压缩单通道图像数据"""
        raise NotImplementedError

    def decompress_channel(self, header, compressed_data):
        """解压单通道图像数据"""
        raise NotImplementedError


# ====================== 霍夫曼编码实现 ======================

class HuffmanCompressor(CompressorBase):
    """Huffman编码压缩器"""

    class TreeNode:
        """Huffman树节点"""

        def __init__(self, symbol=None, freq=0, left=None, right=None):
            self.symbol = symbol  # 符号值
            self.freq = freq  # 出现频率
            self.left = left  # 左子树
            self.right = right  # 右子树

        # 用于堆排序的比较方法
        def __lt__(self, other):
            return self.freq < other.freq

    def build_huffman_tree(self, freq_dict):
        """构建Huffman树"""
        from heapq import heappush, heappop

        # 初始化优先队列
        min_heap = []
        for symbol, freq in freq_dict.items():
            heappush(min_heap, self.TreeNode(symbol, freq))

        # 处理只有一个符号的特殊情况
        if len(min_heap) == 1:
            node = heappop(min_heap)
            heappush(min_heap, self.TreeNode(None, node.freq, node))

        # 构建Huffman树
        while len(min_heap) > 1:  # 合并节点直到只剩根节点
            left = heappop(min_heap)  # 取出频率最小的两个节点
            right = heappop(min_heap)
            merged = self.TreeNode(None, left.freq + right.freq, left, right)   # 创建父节点，频率为两者之和
            heappush(min_heap, merged)

        return min_heap[0] if min_heap else None

    def generate_codes(self, node, prefix="", code_map=None):
        """递归生成Huffman编码表"""
        if code_map is None:
            code_map = {}

        if node is None:
            return code_map

        # 叶子节点，保存编码
        if node.symbol is not None:
            code_map[node.symbol] = prefix or "0"
        else:
            # 非叶子节点，继续递归
            self.generate_codes(node.left, prefix + "0", code_map)
            self.generate_codes(node.right, prefix + "1", code_map)

        return code_map

    def compress_channel(self, channel_data):
        # 统计频率
        freq_counter = Counter(channel_data)
        total_pixels = len(channel_data)

        # 计算信息熵
        entropy = 0.0
        for count in freq_counter.values():
            prob = count / total_pixels
            entropy -= prob * math.log2(prob)

        # 构建Huffman树和编码表
        root = self.build_huffman_tree(freq_counter)
        code_table = self.generate_codes(root)

        # 开始压缩
        start_time = time.time()
        writer = BitWriter()

        for pixel in channel_data:
            writer.write_bits(code_table[pixel])

        writer.flush()
        compress_time = time.time() - start_time

        return {
            'freq': freq_counter,  # 频率表
            'bits': writer.get_bytes(),  # 压缩后的字节数据
            'bitlen': writer.bits_count + len(writer.buffer) * 8,  # 总位数
            'entropy': entropy,  # 信息熵
            'compress_time': compress_time  # 压缩时间
        }

    def decompress_channel(self, header, compressed_data):
        freq_dict = header['freq']
        total_bits = header['bitlen']
        pixel_count = header['pixel_count']

        # 重建Huffman树
        root = self.build_huffman_tree(freq_dict)
        reader = BitReader(compressed_data)
        decompressed = []
        current_node = root  # 从根节点开始解码
        decoded_count = 0

        start_time = time.time()

        # 逐bit解码
        for _ in range(total_bits):
            bit = reader.read_bit()
            if bit is None:
                break

            # 根据bit值选择左右子树
            current_node = current_node.left if bit == 0 else current_node.right

            # 到达叶子节点
            if current_node.symbol is not None:
                decompressed.append(current_node.symbol)
                decoded_count += 1

                # 已解码足够像素则停止
                if decoded_count == pixel_count:
                    break

                # 重置到根节点继续解码
                current_node = root

        decompress_time = time.time() - start_time

        return decompressed, decompress_time


# ====================== 算术编码实现 ======================

class ArithmeticCompressor(CompressorBase):
    """算术编码压缩器（改进解码为 ratio 方式）"""

    def compress_channel(self, data):
        freq = Counter(data)
        total = sum(freq.values())

        # 计算信息熵
        entropy = 0.0
        for count in freq.values():
            prob = count / total
            entropy -= prob * math.log2(prob)

        # 累积频率
        cum = [0] * 257
        for i in range(256):
            cum[i + 1] = cum[i] + freq.get(i, 0)

        # 算术编码过程
        low, high = Fraction(0, 1), Fraction(1, 1)  # 区间边界
        for s in data:
            old_low, old_high = low, high
            interval = old_high - old_low  # 当前区间宽度
            low = old_low + interval * Fraction(cum[s], total)  # 计算新区间
            high = old_low + interval * Fraction(cum[s + 1], total)

        width = high - low
        bits_needed = (math.ceil(math.log2(width.denominator)
                                 - math.log2(width.numerator)) + 1) if width.numerator else 1
        tag_value = int(((low + width / 2) * (1 << bits_needed)).numerator
                        // ((low + width / 2) * (1 << bits_needed)).denominator)

        writer = BitWriter()
        start_time = time.time()
        writer.write_int(tag_value, bits_needed)
        writer.flush()
        compress_time = time.time() - start_time

        return {
            'freq': freq,
            'bits': writer.get_bytes(),
            'bitlen': bits_needed,
            'entropy': entropy,
            'compress_time': compress_time
        }

    def decompress_channel(self, header, data_bytes):
        freq = header['freq']
        total = sum(freq.values())
        pix_cnt = header['pixel_count']
        bits = header['bitlen']

        # 重建累积频率
        cum = [0] * 257
        for i in range(256):
            cum[i + 1] = cum[i] + freq.get(i, 0)

        # 读取 tag
        reader = BitReader(data_bytes)
        tag_int = 0
        for _ in range(bits):
            tag_int = (tag_int << 1) | (reader.read_bit() or 0)
        tag = Fraction(tag_int, 1 << bits)

        low, high = Fraction(0, 1), Fraction(1, 1)
        out = []
        start_time = time.time()

        for _ in range(pix_cnt):
            old_low, old_high = low, high
            interval = old_high - old_low

            #  计算 ratio
            ratio = (tag - old_low) / interval
            #  转为 target
            target = ratio * total

            #  查找符号
            for s in range(256):
                if cum[s] <= target < cum[s + 1]:
                    out.append(s)
                    #  更新区间
                    low = old_low + interval * Fraction(cum[s], total)
                    high = old_low + interval * Fraction(cum[s + 1], total)
                    break

        decompress_time = time.time() - start_time
        return out, decompress_time


# ====================== LZW编码实现 ======================

class LZWCompressor(CompressorBase):
    """LZW压缩器"""

    def __init__(self, code_bits=16):
        self.code_bits = code_bits  # 编码位数

    def compress_channel(self, channel_data):
        # 统计频率用于计算熵
        freq_counter = Counter(channel_data)
        total_pixels = len(channel_data)

        # 计算信息熵
        entropy = 0.0
        for count in freq_counter.values():
            prob = count / total_pixels
            entropy -= prob * math.log2(prob)
        # 初始化字典
        dict_size = 256
        dictionary = {bytes([i]): i for i in range(dict_size)}

        current_str = b''
        codes = []

        start_time = time.time()

        # LZW压缩过程
        for pixel in channel_data:
            new_str = current_str + bytes([pixel])  # 尝试扩展当前字符串

            if new_str in dictionary:
                current_str = new_str  # 匹配成功，继续扩展
            else:
                # 输出当前字符串的编码
                codes.append(dictionary[current_str])

                # 添加到字典(如果还有空间)
                if dict_size < (1 << self.code_bits):
                    dictionary[new_str] = dict_size
                    dict_size += 1

                current_str = bytes([pixel])   # 重置当前字符串为当前像素

        # 输出最后一个字符串的编码
        if current_str:
            codes.append(dictionary[current_str])

        # 写入编码
        writer = BitWriter()
        for code in codes:
            writer.write_int(code, self.code_bits)

        writer.flush()
        compress_time = time.time() - start_time

        return {
            'bits': writer.get_bytes(),
            'bitlen': len(codes) * self.code_bits,
            'code_width': self.code_bits,
            'entropy': entropy,
            'compress_time': compress_time
        }

    def decompress_channel(self, header, compressed_data):
        code_bits = header['code_width']
        pixel_count = header['pixel_count']

        # 读取所有编码
        reader = BitReader(compressed_data)
        code_count = header['bitlen'] // code_bits
        codes = [reader.read_bits(code_bits) for _ in range(code_count)]

        # 初始化字典
        dict_size = 256
        dictionary = {i: bytes([i]) for i in range(dict_size)}

        result = bytearray()
        if not codes:
            return [], 0

        # 初始化解码
        prev_str = dictionary[codes[0]]
        result.extend(prev_str)

        start_time = time.time()

        # LZW解压过程
        for code in codes[1:]:
            if code in dictionary:
                entry = dictionary[code]  # 已知编码，直接获取字符串
            else:
                entry = prev_str + prev_str[:1]   # 处理特殊情况

            result.extend(entry)

            # 添加到字典(如果还有空间)
            if dict_size < (1 << code_bits):
                dictionary[dict_size] = prev_str + entry[:1]
                dict_size += 1

            prev_str = entry   # 更新前一个字符串

            # 检查是否已经解码足够像素
            if len(result) >= pixel_count:
                break

        decompress_time = time.time() - start_time

        return list(result[:pixel_count]), decompress_time


# ====================== 图像压缩管理类 ======================

class ImageCompressor:
    """图像压缩管理类"""

    def __init__(self):
        # 可用的压缩算法
        self.compression_algorithms = [
            HuffmanCompressor(),
            ArithmeticCompressor(),
            LZWCompressor()
        ]
        self.algorithm_names = ["Huffman", "Arithmetic", "LZW"]

    def compress_image(self, image_path, algorithm_idx):
        """压缩图像文件"""
        # 打开并转换图像
        img = Image.open(image_path)
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')

        width, height = img.size
        channels = img.split() if img.mode == 'RGB' else [img]
        channel_count = len(channels)

        headers = []
        compressed_data = []

        # 统计信息
        channel_entropies = []
        total_compress_time = 0.0

        # 压缩每个通道
        for i, channel in enumerate(channels):
            pixel_data = list(channel.getdata())
            header_info = {'pixel_count': len(pixel_data)}

            # 调用具体算法进行压缩
            result = self.compression_algorithms[algorithm_idx].compress_channel(pixel_data)

            header_info.update(result)
            headers.append(header_info)
            compressed_data.append(result['bits'])

            # 累加统计信息
            if 'entropy' in result:
                channel_entropies.append(result['entropy'])

            total_compress_time += result['compress_time']

        # 计算压缩率
        original_size = width * height * (3 if img.mode == 'RGB' else 1)
        compressed_size = sum(len(data) for data in compressed_data)
        compression_ratio = original_size / compressed_size

        # 输出统计信息
        print("\n======== 压缩统计 ========")
        print(f"原始大小: {original_size} 字节")
        print(f"压缩后大小: {compressed_size} 字节")
        print(f"压缩率: {compression_ratio:.2f}:1")

        if channel_entropies:
            print("\n各通道信息熵:")
            if len(channel_entropies) == 1:
                print(f"灰度通道: {channel_entropies[0]:.4f} bits/piexel")
            else:
                print(f"红色通道: {channel_entropies[0]:.4f} bits/piexel")
                print(f"绿色通道: {channel_entropies[1]:.4f} bits/piexel")
                print(f"蓝色通道: {channel_entropies[2]:.4f} bits/piexel")
            print(f"平均信息熵: {sum(channel_entropies) / len(channel_entropies):.4f} bits/piexel")

        print(f"总压缩时间: {total_compress_time:.4f} s")
        print("========================")

        # 生成输出文件名
        base_name = os.path.splitext(image_path)[0]
        output_path = f"{base_name}_{self.algorithm_names[algorithm_idx]}.bin"

        # 写入压缩文件
        with open(output_path, 'wb') as f:
            # 写入图像基本信息
            f.write(struct.pack('>I', width))  # 宽度
            f.write(struct.pack('>I', height))  # 高度
            f.write(b'\x01' if img.mode == 'RGB' else b'\x00')  # 颜色模式
            f.write(struct.pack('B', algorithm_idx))  # 算法索引
            f.write(struct.pack('B', channel_count))  # 通道数

            # 写入各通道头信息
            for header in headers:
                if algorithm_idx in (0, 1):  # Huffman或算术编码
                    # 只写入非零频率
                    non_zero = {s: c for s, c in header['freq'].items() if c > 0}
                    f.write(struct.pack('>I', len(non_zero)))  # 非零符号数

                    for symbol, count in non_zero.items():
                        f.write(struct.pack('B', symbol))  # 符号
                        f.write(struct.pack('>I', count))  # 频率
                else:  # LZW
                    f.write(struct.pack('B', header['code_width']))  # 编码位数

                # 写入通用信息
                f.write(struct.pack('>I', header['pixel_count']))  # 像素数
                f.write(struct.pack('>I', header['bitlen']))  # 总bit数
                f.write(header['bits'])  # 压缩数据

        print(f"压缩文件已保存: {output_path}")
        return output_path

    def decompress_image(self, compressed_path):
        """解压图像文件"""
        with open(compressed_path, 'rb') as f:
            # 读取基本信息
            width = struct.unpack('>I', f.read(4))[0]
            height = struct.unpack('>I', f.read(4))[0]
            is_rgb = f.read(1) == b'\x01'
            algorithm_idx = struct.unpack('B', f.read(1))[0]
            channel_count = struct.unpack('B', f.read(1))[0]

            headers = []

            # 读取各通道头信息
            for _ in range(channel_count):
                header = {}

                if algorithm_idx in (0, 1):  # Huffman或算术编码
                    # 读取频率表
                    symbol_count = struct.unpack('>I', f.read(4))[0]
                    freq = {}

                    for _ in range(symbol_count):
                        symbol = struct.unpack('B', f.read(1))[0]
                        count = struct.unpack('>I', f.read(4))[0]
                        freq[symbol] = count

                    header['freq'] = freq
                else:  # LZW
                    header['code_width'] = struct.unpack('B', f.read(1))[0]

                # 读取通用信息
                header['pixel_count'] = struct.unpack('>I', f.read(4))[0]
                header['bitlen'] = struct.unpack('>I', f.read(4))[0]

                # 计算数据字节数
                data_bytes = (header['bitlen'] + 7) // 8
                header['bits'] = f.read(data_bytes)

                headers.append(header)

        # 解压各通道
        decompressed_channels = []
        total_decompress_time = 0.0

        for header in headers:
            # 调用具体算法解压
            data, time_used = self.compression_algorithms[algorithm_idx].decompress_channel(header, header['bits'])
            decompressed_channels.append(data)
            total_decompress_time += time_used

        print(f"\n解压时间: {total_decompress_time:.4f} 秒")

        # 重建图像
        if is_rgb:
            # RGB图像，合并三个通道
            pixels = list(zip(*decompressed_channels))
            image = Image.new('RGB', (width, height))
        else:
            # 灰度图像，直接使用单通道
            pixels = decompressed_channels[0]
            image = Image.new('L', (width, height))

        image.putdata(pixels)

        # 生成输出文件名
        base_name = os.path.splitext(compressed_path)[0]
        if any(base_name.endswith(f"_{name}") for name in self.algorithm_names):
            base_name = base_name.rsplit('_', 1)[0]

        output_path = f"{base_name}_{self.algorithm_names[algorithm_idx]}_decoded.bmp"
        image.save(output_path, format='BMP')

        print(f"解压图像已保存: {output_path}")


# ====================== 主程序 ======================

def find_image_files(extensions):
    """查找指定扩展名的图像文件"""
    return [f for f in os.listdir()
            if os.path.isfile(f) and f.lower().endswith(extensions)]


def main():
    compressor = ImageCompressor()

    while True:
        print("========================")
        print("请选择操作:")
        print("1. 压缩图像")
        print("2. 解压图像")
        print("3. 退出程序")

        choice = input("请输入选项(1/2/3): ").strip()

        if choice == '1':  # 压缩图像
            # 查找BMP文件
            bmp_files = find_image_files(('.bmp', '.BMP'))

            if not bmp_files:
                print("\n当前目录没有找到BMP图像文件!")
                continue

            print("\n找到以下BMP文件:")
            for i, filename in enumerate(bmp_files, 1):
                print(f"{i}. {filename}")

            try:
                file_idx = int(input("\n请选择要压缩的文件编号: ")) - 1
                if file_idx < 0 or file_idx >= len(bmp_files):
                    print("无效的文件编号!")
                    continue

                selected_file = bmp_files[file_idx]
                print("\n========================")
                print("请选择压缩算法:")
                print("1. 霍夫曼编码")
                print("2. 算术编码")
                print("3. LZW编码")

                algo_idx = int(input("请输入编号(1/2/3): ")) - 1
                if algo_idx not in (0, 1, 2):
                    print("无效的编号!")
                    continue

                # 执行压缩
                compressor.compress_image(selected_file, algo_idx)

            except ValueError:
                print("请输入有效的数字!")

        elif choice == '2':  # 解压图像
            # 查找压缩文件
            bin_files = find_image_files(('.bin', '.BIN'))

            if not bin_files:
                print("\n当前目录没有找到压缩文件!")
                continue

            print("\n找到以下压缩文件:")
            for i, filename in enumerate(bin_files, 1):
                print(f"{i}. {filename}")

            try:
                file_idx = int(input("\n请选择要解压的文件编号: ")) - 1
                if file_idx < 0 or file_idx >= len(bin_files):
                    print("无效的文件编号!")
                    continue

                selected_file = bin_files[file_idx]

                # 执行解压
                compressor.decompress_image(selected_file)

            except ValueError:
                print("请输入有效的数字!")

        elif choice == '3':  # 退出程序
            break

        else:
            print("\n无效的选项，请重新输入!")


if __name__ == '__main__':
    main()
