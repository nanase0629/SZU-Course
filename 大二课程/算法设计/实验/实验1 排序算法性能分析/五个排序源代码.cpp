#include<iostream>
#include<algorithm>
#include<random>
#include<stdlib.h>
#include<Windows.h>
using namespace std;

int ori[10000000];
void select_sort(int n, int* a) {//选择排序
	for (int i = 0; i < n - 1; i++) {
		int Min = 1e9, r;
		for (int j = i + 1; j < n; j++) {
			if (Min > a[j]) {
				Min = a[j];
				r = j;
			}
		}
		if (a[i] > Min) {
			swap(a[i], a[r]);
		}
	}
}



void bubble_sort(int n, int* a) {//冒泡排序
	for (int i = 0; i < n - 1; i++) {
		for (int j = 0; j < n - i - 1; j++) {
			if (a[j] > a[j + 1]) {
				int tmp;
				tmp = a[j];
				a[j] = a[j + 1];
				a[j + 1] = tmp;
			}
		}
	}
}
void bubble_sort_better(int n, int* a) {//优化的冒泡排序，采用双向冒泡
	int right = n;
	int left = 0;
	while (left<right){
		for (int i = left + 1; i < right; i++) {
			if (a[i] < a[i - 1]) {
				int tmp = a[i];
				a[i] = a[i-1];
				a[i- 1] = tmp;
			}
		}
		right--;
		for (int i = right - 1; i > left; i--) {
			if (a[i] < a[i - 1]) {
				int tmp = a[i];
				a[i] = a[i - 1];
				a[i - 1] = tmp;
			}
		}
		left++;
	}
}
void insert_sort(int n, int* a) {//插入排序
	for (int j = 1; j < n; j++) {
		int key = a[j];
		int i = j - 1;
		while (i > 0 && a[i] > key)
		{
			a[i + 1] = a[i];
			i = i - 1;
		}
		a[i + 1] = key;
	}
}
void insert_sort_better(int n, int* a) {//优化的插入排序，通过if减少交换次数
	for (int j = 1; j < n; j++) {
		int key = a[j];
		int i = j - 1;
		while (i >= 0 && a[i] > key)
		{
			a[i + 1] = a[i];
			i = i - 1;
		}
		if (i + 1 != j) {
			a[i + 1] = key;
		}
	}
}

int tmp[10000000] = { 0 };//用于合并的临时数组，此处不在函数内开动态数组是减少对排序时间的影响，确保排序时间的稳定性
void merge(int start, int mid, int end, int n, int* a) {//合并函数

	int pos = start;
	int l = start;
	int r = mid + 1;
	while (l <= mid && r <= end)
	{
		if (a[l] < a[r])tmp[pos++] = a[l++];
		else tmp[pos++] = a[r++];
	}
	while (l <= mid)
	{
		tmp[pos++] = a[l++];
	}
	while (r <= end)
	{
		tmp[pos++] = a[r++];
	}
	for (int i = start; i <= end; i++) {
		a[i] = tmp[i];
	}
}
void merge_sort(int left, int right, int n, int* a) {//归并排序
	if (left < right) {
		int mid = (left + right) / 2;
		merge_sort(left, mid, n, a);
		merge_sort(mid + 1, right, n, a);
		merge(left, mid, right, n, a);
	}
}//0--n-1
void quicksort(int l, int r, int n, int* a) {//快速排序
	if (l >= r)return;
	int base = a[l];
	int left = l, right = r;
	while (left < right)
	{
		while (base <= a[right] && left < right) {
			right--;
		}
		a[left] = a[right];
		while (base >= a[left] && left < right) {
			left++;
		}
		a[right] = a[left];
	}
	a[left] = base;
	quicksort(l, left - 1, n, a);
	quicksort(left + 1, r, n, a);
}
int n;
void copy(int* a) {//复制原始数据
	for (int i = 0; i < n; i++) {
		a[i] = ori[i];
	}
}
int main() {
	double select_t = 0, bubble_t = 0, insert_t = 0, merge_t = 0, quick_t = 0;//记录各个排序总时间
	cout << "请输入数据规模" << endl;
	cin >> n;
	for (int i = 1; i <= 20; i++) {//循环20次，将得到的时间取平均值
		random_device rd;//用于生成随机数
		mt19937 gen(rd());//均匀分布，数据随机性较高
		uniform_int_distribution<>distrib(0, 1e9);
		for (int i = 0; i < n; i++) {//生成n个随机数据，范围（0，1e9）
			ori[i] = distrib(gen);
		}
		int* a = new int[n];//a[]为用于每次排序的数组，排好后恢复原始，确保每种排序初始数据相同
		clock_t start_time, end_time;//分别用于记录排序开始时间和排序结束时间
		
		printf("第%d次排序：\n", i);

		copy(a);
		start_time = clock();//记录排序开始时间
		select_sort(n, a);
		end_time = clock();//记录排序结束时间
		cout << "选择排序用时" << (double)(end_time - start_time) / CLOCKS_PER_SEC << "s"  << endl;//转换为秒输出
		select_t += (double)(end_time - start_time) / CLOCKS_PER_SEC;//将总的排序时间记录下来


		copy(a);//恢复a数组为ori数组
		start_time = clock();//同选择排序
		bubble_sort(n, a);
		end_time = clock();
		cout << "冒泡排序用时" << (double)(end_time - start_time) / CLOCKS_PER_SEC << "s" << endl;
		bubble_t += (double)(end_time - start_time) / CLOCKS_PER_SEC;	

		copy(a);//同上
		start_time = clock();
		insert_sort(n, a);
		end_time = clock();
		cout << "插入排序用时" << (double)(end_time - start_time) / CLOCKS_PER_SEC << "s"  << endl;
		insert_t += (double)(end_time - start_time) / CLOCKS_PER_SEC;

		copy(a);//同上
		start_time = clock();
		merge_sort(0, n - 1, n, a);
		end_time = clock();
		cout << "归并排序用时" << (double)(end_time - start_time) / CLOCKS_PER_SEC << "s"  << endl;
		merge_t += (double)(end_time - start_time) / CLOCKS_PER_SEC;

		copy(a);//同上
		start_time = clock();
		quicksort(0, n - 1, n, a);
		end_time = clock();
		cout << "快速排序用时" << (double)(end_time - start_time) / CLOCKS_PER_SEC << "s"  << endl;
		quick_t += (double)(end_time - start_time) / CLOCKS_PER_SEC;

		cout << endl;
	}
	cout << "选择排序平均用时" << select_t / 20 << "s" << endl;//取均值后输出
	cout << "冒泡排序平均用时" << bubble_t / 20 << "s" << endl;
	cout << "插入排序平均用时" << insert_t / 20 << "s" << endl;
	cout << "归并排序平均用时" << merge_t / 20 << "s" << endl;
	cout << "快速排序平均用时" << quick_t / 20 << "s" << endl;
}