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

int n;//数据范围
struct Point//点结构
{
	double x, y;
	Point() {
		x = y = 0;
	}
	Point(double xx, double yy) :x(xx), y(yy) {}
}p[20000000];
bool cmp(Point a, Point b) {//按照x轴排序
	return a.x == b.x ? a.y < b.y : a.x < b.x;
}
bool cmps(int a, int b) {//按照y轴排序
	return p[a].y < p[b].y;
}
inline double distance(Point a, Point b) {//计算两点距离
	return sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y));
}
inline double distance1(Point a, Point b) {//计算两点距离，不开根号 
	return ((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y));
}
double Force_result(Point*p) {//暴力法
	double Min = 0x7fffffff;//初始化最近距离
	for (int i = 0; i < n; i++) {//遍历各个点
		for (int j = i + 1; j < n; j++) {
			double tmp = distance(p[i], p[j]);//计算两点距离
			if (Min > tmp) {
				Min = tmp;//更新最小值
			}
		}
	}
	return Min;
}
double Force_result1(Point* p) {//暴力法优化 
	double Min = 0x7fffffff;//初始化最近距离
	for (int i = 0; i < n; i++) {//遍历各个点
		for (int j = i + 1; j < n; j++) {
			double tmp = distance1(p[i], p[j]);//计算两点距离
			if (Min > tmp) {
				Min = tmp;//更新最小值
			}
		}
	}
	return sqrt(Min);//最终结果再开根号 

}

//int temp[10000000];
Point pp[20000000];
//归并排序 
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

double merge(Point*p,int left, int right)//分治法
{
	double d = 0x7fffffff;
	if (left == right) return d;//递归到1个点时直接返回
	if (left + 1 == right) {
		return distance(p[left], p[right]);//递归到两个点则直接取两点距离为当前最小
		merge_sort(left, left, right);
	}
	int mid = (left + right) / 2;//分割
	double d_l = merge(p,left, mid);//左半部分找最小
	double d_r = merge(p,mid + 1, right);//右半部分找最小	

	d = min(d_l, d_r);//取左右中最小的那个作为跨越部分的范围
	
	//快排法
	//int k = 0;//用于记录满足条件的跨越点个数
	//for (int i = left; i <= right; i++)//遍历各个点，寻找在x范围在[p[mid].x-d,p[mid].x+d]的所有点
	//	if (fabs(p[mid].x - p[i].x) < d) 
	//		temp[k++] = i;//记录该点的下标
	//sort(temp, temp + k,cmps);//按照y值对其进行排序

	//归并法
	merge_sort(left, mid, right);
	
	for (int i = left; i <= right; i++) {//遍历这些满足条件的点，比对
		if (abs(p[mid].x - p[i].x) >= d)continue;
		for (int j = i + 1; j <= right && p[j].y - p[i].y < d; j++)//增加判定条件，但两点y值差也大于d时无须判断
		{
			double d_m = distance(p[i], p[j]);
			if (d > d_m) d = d_m;//更新最小值
		}
	}
	return d;
}

signed main() {
	cout << "请输入数据规模：" << endl;
	cin >> n;
	int total_time = 0;
	int t = 20;//跑二十轮取平均值
	while (t--) {
		random_device rd;//用于生成随机数
		mt19937 gen(rd());//均匀分布，数据随机性较高
		uniform_int_distribution<>distrib(0, 1e9);
		for (int i = 0; i < n; i++) {//生成n个随机数据，范围（0，1e9）
			p[i].x = distrib(gen);
			p[i].y = distrib(gen);
		}
		sort(p, p + n, cmp);//按照x值进行排序
		clock_t start_time, end_time;//分别用于记录排序开始时间和排序结束时间

		start_time = clock();//记录排序开始时间
		double force_result=Force_result(p);
		end_time = clock();//记录排序结束时间
		cout <<"暴力用时：" << end_time - start_time << "ms 最短距离：" << fixed << setprecision(5) << force_result << endl;

		//start_time = clock();//记录排序开始时间
		//double force_result1 = Force_result1(p);
		//end_time = clock();//记录排序结束时间
		//cout << "优化暴力用时：" << end_time - start_time << "ms 最短距离：" << fixed << setprecision(5) << force_result1 << endl;

		start_time = clock();//记录排序开始时间
		double merge_result = merge(p, 0, n - 1);
		end_time = clock();//记录排序结束时间
		cout << "归并用时：" << end_time - start_time << "ms 最短距离： " << fixed << setprecision(5) << merge_result << endl;
		total_time += end_time - start_time;//分别跑暴力和分治，用于计算总时间


	}
	cout << total_time / 20;
}
