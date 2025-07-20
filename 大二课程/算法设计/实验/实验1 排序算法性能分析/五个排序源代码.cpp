#include<iostream>
#include<algorithm>
#include<random>
#include<stdlib.h>
#include<Windows.h>
using namespace std;

int ori[10000000];
void select_sort(int n, int* a) {//ѡ������
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



void bubble_sort(int n, int* a) {//ð������
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
void bubble_sort_better(int n, int* a) {//�Ż���ð�����򣬲���˫��ð��
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
void insert_sort(int n, int* a) {//��������
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
void insert_sort_better(int n, int* a) {//�Ż��Ĳ�������ͨ��if���ٽ�������
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

int tmp[10000000] = { 0 };//���ںϲ�����ʱ���飬�˴����ں����ڿ���̬�����Ǽ��ٶ�����ʱ���Ӱ�죬ȷ������ʱ����ȶ���
void merge(int start, int mid, int end, int n, int* a) {//�ϲ�����

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
void merge_sort(int left, int right, int n, int* a) {//�鲢����
	if (left < right) {
		int mid = (left + right) / 2;
		merge_sort(left, mid, n, a);
		merge_sort(mid + 1, right, n, a);
		merge(left, mid, right, n, a);
	}
}//0--n-1
void quicksort(int l, int r, int n, int* a) {//��������
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
void copy(int* a) {//����ԭʼ����
	for (int i = 0; i < n; i++) {
		a[i] = ori[i];
	}
}
int main() {
	double select_t = 0, bubble_t = 0, insert_t = 0, merge_t = 0, quick_t = 0;//��¼����������ʱ��
	cout << "���������ݹ�ģ" << endl;
	cin >> n;
	for (int i = 1; i <= 20; i++) {//ѭ��20�Σ����õ���ʱ��ȡƽ��ֵ
		random_device rd;//�������������
		mt19937 gen(rd());//���ȷֲ�����������Խϸ�
		uniform_int_distribution<>distrib(0, 1e9);
		for (int i = 0; i < n; i++) {//����n��������ݣ���Χ��0��1e9��
			ori[i] = distrib(gen);
		}
		int* a = new int[n];//a[]Ϊ����ÿ����������飬�źú�ָ�ԭʼ��ȷ��ÿ�������ʼ������ͬ
		clock_t start_time, end_time;//�ֱ����ڼ�¼����ʼʱ����������ʱ��
		
		printf("��%d������\n", i);

		copy(a);
		start_time = clock();//��¼����ʼʱ��
		select_sort(n, a);
		end_time = clock();//��¼�������ʱ��
		cout << "ѡ��������ʱ" << (double)(end_time - start_time) / CLOCKS_PER_SEC << "s"  << endl;//ת��Ϊ�����
		select_t += (double)(end_time - start_time) / CLOCKS_PER_SEC;//���ܵ�����ʱ���¼����


		copy(a);//�ָ�a����Ϊori����
		start_time = clock();//ͬѡ������
		bubble_sort(n, a);
		end_time = clock();
		cout << "ð��������ʱ" << (double)(end_time - start_time) / CLOCKS_PER_SEC << "s" << endl;
		bubble_t += (double)(end_time - start_time) / CLOCKS_PER_SEC;	

		copy(a);//ͬ��
		start_time = clock();
		insert_sort(n, a);
		end_time = clock();
		cout << "����������ʱ" << (double)(end_time - start_time) / CLOCKS_PER_SEC << "s"  << endl;
		insert_t += (double)(end_time - start_time) / CLOCKS_PER_SEC;

		copy(a);//ͬ��
		start_time = clock();
		merge_sort(0, n - 1, n, a);
		end_time = clock();
		cout << "�鲢������ʱ" << (double)(end_time - start_time) / CLOCKS_PER_SEC << "s"  << endl;
		merge_t += (double)(end_time - start_time) / CLOCKS_PER_SEC;

		copy(a);//ͬ��
		start_time = clock();
		quicksort(0, n - 1, n, a);
		end_time = clock();
		cout << "����������ʱ" << (double)(end_time - start_time) / CLOCKS_PER_SEC << "s"  << endl;
		quick_t += (double)(end_time - start_time) / CLOCKS_PER_SEC;

		cout << endl;
	}
	cout << "ѡ������ƽ����ʱ" << select_t / 20 << "s" << endl;//ȡ��ֵ�����
	cout << "ð������ƽ����ʱ" << bubble_t / 20 << "s" << endl;
	cout << "��������ƽ����ʱ" << insert_t / 20 << "s" << endl;
	cout << "�鲢����ƽ����ʱ" << merge_t / 20 << "s" << endl;
	cout << "��������ƽ����ʱ" << quick_t / 20 << "s" << endl;
}