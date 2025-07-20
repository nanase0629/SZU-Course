#include <iostream>
 
#include <random>
 
#include <vector>
 
#include <cstring>
 
#include <chrono>
 
 
 
using namespace std;
 
using namespace std::chrono;
 
 
 
random_device rd;
 
mt19937 gen(rd());
 
vector<int> sizes{ 8,16,32,64,128,256,384,512,768,1024,1536,2048,3072,4096,5120,6144,7168,8192,10240,12288,16384 };
 
char* cache1;
 
vector<int> line{ 1,2,4,8,16,32,64,96,128,192,256,512,1024,1536,2048 };
 
 
 
// 测层级，参数为内存块大小（对应cache大小），存于字符数组，随机产生访问位置存于位置数组，若设置的内存块大小刚好是cache大小，cache层级边界时间会有较大改变
 
void testCache(int size) {
 
    int n = size / sizeof(char);                // 获得字符数组大小
 
    char* arr = new char[n];                    // 申请对应大小字符数组用于存储同等大小内存块
 
    memset(arr, 1, sizeof(char) * n);            // 初始字符数组
 
 
 
    uniform_int_distribution<> num(0, n - 1);    // 大规模随机数0~n-1
 
 
 
    vector<int> pos;                    // 位置数组
 
    for (int i = 0; i < 100000000; i++)
 
    {
 
        pos.push_back(num(gen));         // 随机产生位置并压入数组
 
    }
 
 
 
    int sum = 0;                                    // 由于取数
 
    high_resolution_clock::time_point t1 = high_resolution_clock::now();
 
    for (int i = 0; i < 100000000; i++) {
 
        sum += arr[pos[i]];                        // 取数
 
    }
 
    high_resolution_clock::time_point t2 = high_resolution_clock::now();
 
    duration<double> time_span = duration_cast<duration<double>>(t2 - t1);
 
    double dt = time_span.count();
 
 
 
    cout << "size=" << (size / 1024) << "KB,time=" << dt << "s" << endl;
 
 
 
    delete[]arr;
 
}
 
 
 
// 测试缓存行大小对性能的影响
 
void testCacheLine(char* cache1, int line, int size)
 
{
 
    int n = size / sizeof(char);
 
    int sum = 0;
 
    high_resolution_clock::time_point t1 = high_resolution_clock::now();
 
    for (int j = 0; j < line; j++)
 
    {
 
        for (int i = 0; i < n; i += line)
 
        {
 
            sum += cache1[i];
 
        }
 
    }
 
 
 
    high_resolution_clock::time_point t2 = high_resolution_clock::now();
 
    duration<double> time_span = duration_cast<duration<double>>(t2 - t1);
 
    double dt = time_span.count();
 
 
 
    cout << "length=" << line << "B time=" << dt << endl;
 
}
 
 
 
int main() {
 
    for (auto s : sizes)
 
    {
 
        testCache(s * 1024);
 
    }
 
 
 
    cache1 = new char[100000000 * 10 / sizeof(char)];
 
    memset(cache1, 1, 100000000 * 10);            // 初始字符数组
 
 
 
    for (auto l : line)
 
    {
 
        testCacheLine(cache1, l, 100000000);
 
    }
 
 
 
    return 0;
 
}
