#include<iostream>
#include<algorithm>
#include<string>
#include<random>
#include<stdlib.h>
#include<Windows.h>
#include<math.h>
#include<iomanip>
#include <graphics.h>		
#include <conio.h>
using namespace std;

int n;//���ݷ�Χ
struct Point//��ṹ
{
	double x, y;
	Point() {
		x = y = 0;
	}
	Point(double xx, double yy) :x(xx), y(yy) {}
}p[20000000];
bool cmp(Point a, Point b) {//����x������
	return a.x == b.x ? a.y < b.y : a.x < b.x;
}
bool cmps(int a, int b) {//����y������
	return p[a].y < p[b].y;
}
inline double distance(Point a, Point b) {//�����������
	return sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y));
}
inline double distance1(Point a, Point b) {//����������룬�������� 
	return ((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y));
}
double Force_result(Point*p) {//������
	double Min = 0x7fffffff;//��ʼ���������
	for (int i = 0; i < n; i++) {//����������
		for (int j = i + 1; j < n; j++) {
			double tmp = distance(p[i], p[j]);//�����������
			if (Min > tmp) {
				Min = tmp;//������Сֵ
			}
		}
	}
	return Min;
}
double Force_result1(Point* p) {//�������Ż� 
	double Min = 0x7fffffff;//��ʼ���������
	for (int i = 0; i < n; i++) {//����������
		for (int j = i + 1; j < n; j++) {
			double tmp = distance1(p[i], p[j]);//�����������
			if (Min > tmp) {
				Min = tmp;//������Сֵ
			}
		}
	}
	return sqrt(Min);//���ս���ٿ����� 

}

//int temp[10000000];
Point pp[20000000];
//�鲢���� 
void merge_sort(int start, int mid, int end) {
	int pos = start;
	int l = start;
	int r = mid + 1;
	while (l <= mid && r <= end)
	{
		if (p[l].y <= p[r].y)pp[pos++] = p[l++];
		else pp[pos++] = p[r++];
	}
	while (l <= mid)
	{
		pp[pos++] = p[l++];
	}
	while (r <= end)
	{
		pp[pos++] = p[r++];
	}
	for (int i = start; i <= end; i++) {
		p[i] = pp[i];
	}
}

double merge(Point*p,int left, int right)//���η�
{
	double d = 0x7fffffff;
	if (left == right) return d;//�ݹ鵽1����ʱֱ�ӷ���
	if (left + 1 == right) {
		return distance(p[left], p[right]);//�ݹ鵽��������ֱ��ȡ�������Ϊ��ǰ��С
		merge_sort(left, left, right);
	}
	int mid = (left + right) / 2;//�ָ�
	double d_l = merge(p,left, mid);//��벿������С
	double d_r = merge(p,mid + 1, right);//�Ұ벿������С	

	d = min(d_l, d_r);//ȡ��������С���Ǹ���Ϊ��Խ���ֵķ�Χ
	
	//���ŷ�
	//int k = 0;//���ڼ�¼���������Ŀ�Խ�����
	//for (int i = left; i <= right; i++)//���������㣬Ѱ����x��Χ��[p[mid].x-d,p[mid].x+d]�����е�
	//	if (fabs(p[mid].x - p[i].x) < d) 
	//		temp[k++] = i;//��¼�õ���±�
	//sort(temp, temp + k,cmps);//����yֵ�����������

	//�鲢��
	merge_sort(left, mid, right);
	
	for (int i = left; i <= right; i++) {//������Щ���������ĵ㣬�ȶ�
		if (abs(p[mid].x - p[i].x) >= d)continue;
		for (int j = i + 1; j <= right && p[j].y - p[i].y < d; j++)//�����ж�������������yֵ��Ҳ����dʱ�����ж�
		{
			double d_m = distance(p[i], p[j]);
			if (d > d_m) d = d_m;//������Сֵ
		}
	}
	return d;
}

signed main() {
	cout << "���������ݹ�ģ��" << endl;
	cin >> n;
	int total_time = 0;
	int t = 20;//�ܶ�ʮ��ȡƽ��ֵ
	while (t--) {
		random_device rd;//�������������
		mt19937 gen(rd());//���ȷֲ�����������Խϸ�
		uniform_int_distribution<>distrib(0, 1e9);
		for (int i = 0; i < n; i++) {//����n��������ݣ���Χ��0��1e9��
			p[i].x = distrib(gen);
			p[i].y = distrib(gen);
		}
		sort(p, p + n, cmp);//����xֵ��������
		clock_t start_time, end_time;//�ֱ����ڼ�¼����ʼʱ����������ʱ��

		start_time = clock();//��¼����ʼʱ��
		double force_result=Force_result(p);
		end_time = clock();//��¼�������ʱ��
		cout <<"������ʱ��" << end_time - start_time << "ms ��̾��룺" << fixed << setprecision(5) << force_result << endl;

		//start_time = clock();//��¼����ʼʱ��
		//double force_result1 = Force_result1(p);
		//end_time = clock();//��¼�������ʱ��
		//cout << "�Ż�������ʱ��" << end_time - start_time << "ms ��̾��룺" << fixed << setprecision(5) << force_result1 << endl;

		start_time = clock();//��¼����ʼʱ��
		double merge_result = merge(p, 0, n - 1);
		end_time = clock();//��¼�������ʱ��
		cout << "�鲢��ʱ��" << end_time - start_time << "ms ��̾��룺 " << fixed << setprecision(5) << merge_result << endl;
		total_time += end_time - start_time;//�ֱ��ܱ����ͷ��Σ����ڼ�����ʱ��


	}
	cout << total_time / 20;
}
