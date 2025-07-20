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
 
 
 
// ��㼶������Ϊ�ڴ���С����Ӧcache��С���������ַ����飬�����������λ�ô���λ�����飬�����õ��ڴ���С�պ���cache��С��cache�㼶�߽�ʱ����нϴ�ı�
 
void testCache(int size) {
 
    int n = size / sizeof(char);                // ����ַ������С
 
    char* arr = new char[n];                    // �����Ӧ��С�ַ��������ڴ洢ͬ�ȴ�С�ڴ��
 
    memset(arr, 1, sizeof(char) * n);            // ��ʼ�ַ�����
 
 
 
    uniform_int_distribution<> num(0, n - 1);    // ���ģ�����0~n-1
 
 
 
    vector<int> pos;                    // λ������
 
    for (int i = 0; i < 100000000; i++)
 
    {
 
        pos.push_back(num(gen));         // �������λ�ò�ѹ������
 
    }
 
 
 
    int sum = 0;                                    // ����ȡ��
 
    high_resolution_clock::time_point t1 = high_resolution_clock::now();
 
    for (int i = 0; i < 100000000; i++) {
 
        sum += arr[pos[i]];                        // ȡ��
 
    }
 
    high_resolution_clock::time_point t2 = high_resolution_clock::now();
 
    duration<double> time_span = duration_cast<duration<double>>(t2 - t1);
 
    double dt = time_span.count();
 
 
 
    cout << "size=" << (size / 1024) << "KB,time=" << dt << "s" << endl;
 
 
 
    delete[]arr;
 
}
 
 
 
// ���Ի����д�С�����ܵ�Ӱ��
 
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
 
    memset(cache1, 1, 100000000 * 10);            // ��ʼ�ַ�����
 
 
 
    for (auto l : line)
 
    {
 
        testCacheLine(cache1, l, 100000000);
 
    }
 
 
 
    return 0;
 
}
