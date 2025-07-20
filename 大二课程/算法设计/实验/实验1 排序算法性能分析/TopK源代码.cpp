#include<iostream>
#include<algorithm>
#include<random>
#include<stdlib.h>
#include<Windows.h>
using namespace std;

int n;
int ori[60000000];//随机数据存放的数组
void copy(int* a) {
	for (int i = 0; i < n; i++) {
		a[i] = ori[i];
	}
}
int tmp;
void bubble_Top(int* a) {//冒泡排序取前10
	for (int i = 0; i < 10; i++) {//只排出前10大的即可
		for (int j = n - 1; j > i; j--) {
			if (a[j] > a[j - 1]) {
				tmp = a[j];
				a[j] = a[j - 1];
				a[j - 1] = tmp;
			}
		}
	}
}
int p[60000000] = { 0 };
void count_Top(int* a) {//计数排序取前十
	int Max = 0;//取最大最小相减计算数组范围
	int Min = 1e9;
	for (int i = 0; i < n; i++) {
		if (a[i] > Max)Max = a[i];
		if (a[i] < Min)Min = a[i];
	}
	int range = Max - Min+1;//得到数组范围作为偏移值
	
	//此处尝试用动态分配数组，但分配时间加上初始化为0的时间较长，影响对排序实际用时的影响
	/*int *tmp = new int[range];
	for (int i = 0; i < range; i++) {
		tmp[i] = 0;
	}*/
	
	for (int i = 0; i < n; i++) {
		p[a[i] - Min]++;
	}
	int find = 0;
	for (int i = range-1; i >= 0; i--) {
		while (p[i]){
			if (find >= 10)break;//找到10个即可结束
			a[find++] = i + Min;
			p[i]--;
		}
		if (find >= 10)break;
	}
}

void adjust(int start, int end,int *a) {
	int tmp = a[start];//非叶子节点往下进行调整
	for (int i = 2 * start + 1; i < end; i = i * 2 + 1) {
		if (i<end - 1 && a[i]>a[i + 1]) {//从最后一片叶子节点的父节点开始比较，比较左右两子叶的最小
			i++;
		}
		if (a[i] < tmp) {
			a[start] = a[i];
			start = i;
		}
		else break;
	}
	a[start] = tmp;
}

void build_heap(int len,int *a) {
	//创建小根堆
	for (int i = len / 2 - 1; i >= 0; i--) {
		adjust(i, len,a);//调整非叶子节点
	}                                               
}
void heap_Top(int* a) {
	build_heap(10, a);//建小根堆
	for (int i = 10; i < n; i++) {
		if (a[i] > a[0]) {//每个数都与堆顶元素(小根堆堆顶为最小值)进行比较，若大于堆顶则交换
			a[0] = a[i];
			adjust(0, 10, a);//维护小根堆
		}
	}
}

int main() {

	cout << "请输入数据规模:" << endl;
	cin >> n;

	clock_t start_time, end_time;//分别用于记录排序开始时间和排序结束时间

	random_device rd;//用于生成随机数
	mt19937 gen(rd());//均匀分布，数据随机性较高
	uniform_int_distribution<>distrib(0, 50000000);
	for (int i = 0; i < n; i++) {//生成n个随机数据，范围（0，50000000），此范围不能过大，计数排序的数组范围有限
		ori[i] = distrib(gen);
	}
	/*for (int i = 0; i < n; i++) {
		cout << ori[i] << " ";
	}cout << endl << endl;;*/

	int *a = new int[n + 10];

	copy(a);//将未排序的数组复制到a数组中
	start_time = clock();
	bubble_Top(a);
	end_time = clock();
	cout << "冒泡排序Top10所用时间：" << (double)(end_time - start_time) <<"ms" << endl;
	for (int i = 0; i < 10; i++) {//输出排序结果
		cout << a[i] << " ";
	}cout << endl << endl;

	copy(a);
	start_time = clock();
	count_Top(a);
	end_time = clock();
	cout << "计数排序Top10所用时间：" << (double)(end_time - start_time) <<"ms" << endl;
	for (int i = 0; i < 10; i++) {
		cout << a[i] << " ";
	}cout << endl<<endl;

	copy(a);
	start_time = clock();
	heap_Top(a);
	end_time = clock();
	cout << "堆排序Top10所用时间："<<(double)(end_time-start_time) <<"ms" << endl;
	sort(a, a + 10, greater<int>());//小根堆的10个数并未进行排序，为了方便与其他排序比较数据是否正确，此处将top10降序
	for (int i = 0; i < 10; i++) {
		cout << a[i] << " ";
	}cout << endl<<endl;
}