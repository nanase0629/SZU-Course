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
#include<thread>
#include"graph.h" 
using namespace std;

int n;
Graph g(800, 800);
struct Point
{
	double x, y;
	Point() {
		x = y = 0;
	}
	Point(double xx, double yy) :x(xx), y(yy) {}
}p[100000000];
bool cmp(Point a, Point b) {
	return a.x == b.x ? a.y < b.y : a.x < b.x;
}
bool cmps(int a, int b) {
	return p[a].y < p[b].y;
}
double distance(Point a, Point b) {
	return sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y));
}
double Force_result(Point* p) {
	double Min = 0x7fffffff;
	int x1=p[0].x, y1=p[0].y, x2=p[1].x, y2=p[1].y;
	for (int i = 0; i < n; i++) {
		for (int j = i + 1; j < n; j++) {
			//Min = min(Min, distance(p[i], p[j]));
			double tmp = distance(p[i], p[j]);
			g.drawLine(p[i].x, p[i].y, p[j].x, p[j].y);
			g.drawNum1(10, 115, distance(p[i], p[j]));
			Sleep(100);
			if (Min > tmp) {
				Min = tmp;
				g.drawminNum(10, 119, distance(p[i], p[j]));
				g.setLineColor(WHITE);
				g.drawLine(x1, y1, x2, y2);
				g.setLineColor(BLACK);
				g.drawPoint(x1, y1);
				g.drawPoint(x2, y2);
				x1 = p[i].x, y1 = p[i].y, x2 = p[j].x, y2 = p[j].y;
			}
			g.setLineColor(WHITE);
			g.drawLine(p[i].x, p[i].y, p[j].x, p[j].y);
			g.setLineColor(BLACK);
			g.drawPoint(p[i].x, p[i].y);
			g.drawPoint(p[j].x, p[j].y);
			g.drawLine(x1, y1, x2, y2);
			Sleep(100);
		}
	}
	return Min;
}
void set_line(int i, int j) {
	g.drawLine(p[i].x, p[i].y, p[j].x, p[j].y);
	Sleep(500);
	getchar();
	g.setLineColor(WHITE);
	g.drawLine(p[i].x, p[i].y, p[j].x, p[j].y);
	g.setLineColor(BLACK);
	g.drawPoint(p[i].x, p[i].y);
	g.drawPoint(p[j].x, p[j].y);
	Sleep(500);
}
int r_i, r_j;
double r_d = 1e9;
void clear_mid_d() {
	g.setLineColor(WHITE);
	g.drawLine(p[r_i].x, p[r_i].y, p[r_j].x, p[r_j].y);
	g.setLineColor(BLACK);
	g.drawPoint(p[r_i].x, p[r_i].y);
	g.drawPoint(p[r_j].x, p[r_j].y);
}
void set_min_d() {
	g.drawLine(p[r_i].x, p[r_i].y, p[r_j].x, p[r_j].y);
}
void set_point() {
	for (int i = 0; i < n; i++) {
		g.drawPoint(p[i].x, p[i].y);
	}
}
void reset() {	
	g.beg();
	g.clear();
	set_point();
	g.drawCoordinateAxis(100, 100, 10, 10);
	g.setLineColor(BLACK);
	g.end();
}
int temp[10000000];
void merge_sort(int start, int mid, int end) {
	int tmp[10000] = { 0 };
	int pos = start;
	int l = start;
	int r = mid + 1;
	while (l <= mid && r <= end)
	{
		if (p[temp[l]].y < p[temp[r]].y)tmp[pos++] = temp[l++];
		else tmp[pos++] = temp[r++];
	}
	while (l <= mid)
	{
		tmp[pos++] = temp[l++];
	}
	while (r <= end)
	{
		tmp[pos++] = temp[r++];
	}
	for (int i = start; i <= end; i++) {
		temp[i] = tmp[i];
	}
}

double m_d = 0x7fffffff;
double merge(Point* p, int left, int right)
{
	double d = 0x7fffffff;
	if (left == right) return d;
	if (left + 1 == right) {
		g.drawNum1(50, 105, distance(p[left], p[right]));
		set_line(left, right);	

		Sleep(500);
		if (m_d > distance(p[left], p[right])) {
			m_d = distance(p[left], p[right]);
			r_i = left, r_j = right;
			g.drawminNum(20, 105, m_d);
			}
		return distance(p[left], p[right]);
	}

	int mid = (left + right) / 2;
	//画递归分界线
	g.setLineColor(BLACK);
	g.drawLine(p[mid].x, 0, p[mid].x, 100);
	g.setLineColor(BLUE);
	g.drawLine(p[left].x, 0, p[left].x, 100);
	g.drawLine(p[right].x, 0, p[right].x, 100);
	g.setLineColor(BLACK);
	Sleep(500);

	double d1 = merge(p, left, mid);
	double d2 = merge(p, mid + 1, right);
	d = min(d1, d2);
	if(m_d>d){
		m_d = d;
		g.drawminNum(20, 105, m_d);
	}

	int i, j, k = 0;
	for (i = left; i <= right; i++)
		//距离递归中点<d的点都放进来
		if (fabs(p[mid].x - p[i].x) < d) {
			cout << k << endl;
			temp[k++] = i;
		}
	//sort(temp, temp + k,cmps);
	merge_sort(left,mid,right);

	//中间区域范围
	g.setLineColor(YELLOW);
	int ddd = d;
	g.drawLine(p[mid].x-d, 0, p[mid].x-d, 100);
	g.drawLine(p[mid].x + d, 0, p[mid].x + d, 100);
	g.setLineColor(BLACK);

	for (i = 0; i < k; i++)//依次比较这些点
	{
		//每个点的比较范围
		g.setLineColor(GREEN);
		g.drawLine(0, p[temp[i]].y + d , 100, p[temp[i]].y + d );
		g.drawLine(0, p[temp[i]].y - d , 100, p[temp[i]].y - d );
		//重新画坐标轴，防止被遮挡
		g.setLineColor(BLACK);
		g.drawCoordinateAxis(100, 100, 10, 10);
		//当前比较的点
		g.setPointColor(GREEN);
		g.drawPoint(p[temp[i]].x, p[temp[i]].y);
		g.setPointColor(BLACK);
		getchar();

		for (j = i + 1; j < k && p[temp[j]].y - p[temp[i]].y < d; j++) 
		{
			double d3 = distance(p[temp[i]], p[temp[j]]);

			//显示每一次比较
			g.drawNum1(50, 105, d3);
			set_line(temp[i], temp[j]);
			if (d > d3) {
				d = d3;
				if (m_d > d) {
					m_d = d;
					r_i = temp[i];
					r_j = temp[j];
				}

			}
		}
		//清楚所有内容重新制图
		reset();
		g.drawminNum(20, 105, m_d);
		//画中线,左右界限
		g.setLineColor(BLACK);
		g.drawLine(p[mid].x, 0, p[mid].x, 100);
		g.setLineColor(BLUE);
		g.drawLine(p[left].x, 0, p[left].x, 100);
		g.drawLine(p[right].x, 0, p[right].x, 100);
		g.setLineColor(BLACK);
		//画中间范围
		g.setLineColor(YELLOW);
		g.drawLine(p[mid].x - ddd, p[mid].y, p[mid].x - ddd, 100);
		g.drawLine(p[mid].x - ddd, p[mid].y, p[mid].x - ddd, 0);
		g.drawLine(p[mid].x + ddd, p[mid].y, p[mid].x + ddd, 100);
		g.drawLine(p[mid].x + ddd, p[mid].y, p[mid].x + ddd, 0);
		g.setLineColor(BLACK);
	}
	reset();
	g.drawminNum(20, 105, m_d);
	Sleep(500);

	return d;
}

signed main() {
	g.drawCoordinateAxis(100, 100, 10, 10);
	g.setLineColor(BLACK);
	g.setPointColor(BLACK);
	g.setTextColor(BLACK);

	cout << "请输入数据规模：" << endl;
	cin >> n;
	int total_time = 0;
	cout << "输入0为固定数值 输入1为手动模式 输入2为随机模式" << endl;
	int mode;
	cin >> mode;
	if (mode == 0) {
		n = 10;
		p[0] = { 10,10 };
		p[1] = {20,50};
		p[2] = { 30,20 };
		p[3] = { 50,10 };
		p[4] = { 50,60 };
		p[5] = {60,70};
		p[6] = {70,30};
		p[7] = {80,10};
		p[8] = {100,30};
		p[9] = {90,90};
		for (int i = 0; i < n; i++) {
			g.drawPoint(p[i].x, p[i].y);
		}
		getchar();
	}
	else if (mode == 1) {
		for (int i = 0; i < n; i++) {
			cin >> p[i].x >> p[i].y;
		}
	}
	else {
		random_device rd;//用于生成随机数
		mt19937 gen(rd());//均匀分布，数据随机性较高
		uniform_int_distribution<>distrib(5, 95);
		for (int i = 0; i < n; i++) {//生成n个随机数据，范围（0，1e9）
			p[i].x = distrib(gen);
			p[i].y = distrib(gen);
			g.drawPoint(p[i].x, p[i].y);

		}
	}
	getchar();
	sort(p, p + n, cmp);

	clock_t start_time, end_time;//分别用于记录排序开始时间和排序结束时间

	start_time = clock();//记录排序开始时间

	//double force_result=Force_result(p);
	//end_time = clock();//记录排序结束时间
	//cout <<"暴力用时：" << end_time - start_time << "ms 最短距离：" << fixed << setprecision(5) << force_result << endl;

	start_time = clock();//记录排序开始时间
	double merge_result = merge(p, 0, n - 1);
	g.drawLine(p[r_i].x, p[r_i].y, p[r_j].x, p[r_j].y);
	g.drawminNum(20, 105, m_d);
	end_time = clock();//记录排序结束时间
	cout << "归并用时：" << end_time - start_time << "ms 最短距离：" << fixed << setprecision(5) << merge_result << endl;

	cout << p[r_i].x << " " << p[r_i].y << endl;
	cout << p[r_j].x << " " << p[r_j].y << endl;
	getchar();
	getchar();
	//system("pause");
}