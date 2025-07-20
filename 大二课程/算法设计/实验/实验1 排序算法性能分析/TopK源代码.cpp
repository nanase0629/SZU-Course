#include<iostream>
#include<algorithm>
#include<random>
#include<stdlib.h>
#include<Windows.h>
using namespace std;

int n;
int ori[60000000];//������ݴ�ŵ�����
void copy(int* a) {
	for (int i = 0; i < n; i++) {
		a[i] = ori[i];
	}
}
int tmp;
void bubble_Top(int* a) {//ð������ȡǰ10
	for (int i = 0; i < 10; i++) {//ֻ�ų�ǰ10��ļ���
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
void count_Top(int* a) {//��������ȡǰʮ
	int Max = 0;//ȡ�����С����������鷶Χ
	int Min = 1e9;
	for (int i = 0; i < n; i++) {
		if (a[i] > Max)Max = a[i];
		if (a[i] < Min)Min = a[i];
	}
	int range = Max - Min+1;//�õ����鷶Χ��Ϊƫ��ֵ
	
	//�˴������ö�̬�������飬������ʱ����ϳ�ʼ��Ϊ0��ʱ��ϳ���Ӱ�������ʵ����ʱ��Ӱ��
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
			if (find >= 10)break;//�ҵ�10�����ɽ���
			a[find++] = i + Min;
			p[i]--;
		}
		if (find >= 10)break;
	}
}

void adjust(int start, int end,int *a) {
	int tmp = a[start];//��Ҷ�ӽڵ����½��е���
	for (int i = 2 * start + 1; i < end; i = i * 2 + 1) {
		if (i<end - 1 && a[i]>a[i + 1]) {//�����һƬҶ�ӽڵ�ĸ��ڵ㿪ʼ�Ƚϣ��Ƚ���������Ҷ����С
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
	//����С����
	for (int i = len / 2 - 1; i >= 0; i--) {
		adjust(i, len,a);//������Ҷ�ӽڵ�
	}                                               
}
void heap_Top(int* a) {
	build_heap(10, a);//��С����
	for (int i = 10; i < n; i++) {
		if (a[i] > a[0]) {//ÿ��������Ѷ�Ԫ��(С���ѶѶ�Ϊ��Сֵ)���бȽϣ������ڶѶ��򽻻�
			a[0] = a[i];
			adjust(0, 10, a);//ά��С����
		}
	}
}

int main() {

	cout << "���������ݹ�ģ:" << endl;
	cin >> n;

	clock_t start_time, end_time;//�ֱ����ڼ�¼����ʼʱ����������ʱ��

	random_device rd;//�������������
	mt19937 gen(rd());//���ȷֲ�����������Խϸ�
	uniform_int_distribution<>distrib(0, 50000000);
	for (int i = 0; i < n; i++) {//����n��������ݣ���Χ��0��50000000�����˷�Χ���ܹ��󣬼�����������鷶Χ����
		ori[i] = distrib(gen);
	}
	/*for (int i = 0; i < n; i++) {
		cout << ori[i] << " ";
	}cout << endl << endl;;*/

	int *a = new int[n + 10];

	copy(a);//��δ��������鸴�Ƶ�a������
	start_time = clock();
	bubble_Top(a);
	end_time = clock();
	cout << "ð������Top10����ʱ�䣺" << (double)(end_time - start_time) <<"ms" << endl;
	for (int i = 0; i < 10; i++) {//���������
		cout << a[i] << " ";
	}cout << endl << endl;

	copy(a);
	start_time = clock();
	count_Top(a);
	end_time = clock();
	cout << "��������Top10����ʱ�䣺" << (double)(end_time - start_time) <<"ms" << endl;
	for (int i = 0; i < 10; i++) {
		cout << a[i] << " ";
	}cout << endl<<endl;

	copy(a);
	start_time = clock();
	heap_Top(a);
	end_time = clock();
	cout << "������Top10����ʱ�䣺"<<(double)(end_time-start_time) <<"ms" << endl;
	sort(a, a + 10, greater<int>());//С���ѵ�10������δ��������Ϊ�˷�������������Ƚ������Ƿ���ȷ���˴���top10����
	for (int i = 0; i < 10; i++) {
		cout << a[i] << " ";
	}cout << endl<<endl;
}