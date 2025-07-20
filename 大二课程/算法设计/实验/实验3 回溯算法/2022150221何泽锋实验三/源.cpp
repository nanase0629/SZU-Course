#include <iostream>   
#include <fstream>    
#include <string>    
#include <sstream>    
#include <vector>
#include<algorithm>
#include<iomanip>
#include<Windows.h>
#include<random>
#include<math.h>
#include<stdlib.h>
using namespace std;

string file = "le450_5a.col";  //地图数据文件名
long long FindNum = 0x7fffffff;//需要找的最大数量的解

struct Point {
	int id;//下标
	int color; //当前颜色
	int chooseNum; //可选颜色
	int degree; //度数
	bool choose[30]; //下标对应颜色，1代表可选，0代表不可选，此处直接开30色数组，保证实验所用颜色数<30
	int* adjPoint; //记录相邻点下标
};

struct LeightonGraph {
	int n;// 图中顶点数
	int cnt = 0;//解的个数
	int* color;//每个点的颜色
	int colorNum = 5;//颜色种类
	int** Map;//邻接矩阵记录图
	int* colorDrawn;  //用于判断颜色轮寻
	Point* p;  //点集
	int* b; //排序用的`
}graph;

long long cnt = 0;  //记录答案数

bool cmp(int a1, int a2) {
	if (graph.p[a1].chooseNum == graph.p[a2].chooseNum) {  //优先MVR
		return graph.p[a1].degree > graph.p[a2].degree;  //DH
	}
	return graph.p[a1].chooseNum < graph.p[a2].chooseNum;
}

void clear() {
	for (int i = 0; i <= graph.n; i++) {
		delete graph.Map[i];
	}delete[]graph.Map;
	delete graph.b;
	delete graph.color;
	delete graph.colorDrawn;
	delete graph.p;
}


void ReadGraph(string filename) {
	ifstream file(filename);  // 打开文件流
	string line;            // 用于存储读取的每一行数据的字符串
	if (!file.is_open()) {
		cerr << "错误：无法打开文件 " << filename << endl;  // 输出错误消息
		return;
	}
	while (getline(file, line)) {
		istringstream iss(line);  // 使用字符串流解析每一行数据
		string token;  // 存储当前行的第一个单词
		iss >> token;  // 从当前行中提取第一个单词

		// 如果单词为 "p"，表示读取到了顶点数信息
		if (token == "p") {
			iss >> token >> graph.n;  // 读取顶点数
			graph.Map = new int* [graph.n + 1];
			for (int i = 0; i <= graph.n; i++) {
				graph.Map[i] = new int[graph.n + 1];
			}
			graph.p = new Point[graph.n + 1];
			graph.b = new int[graph.n + 1];
			for (int i = 1; i <= graph.n; i++)  //点集初始化
			{
				graph.p[i].id = i;
				graph.p[i].color = 0;  //0代表无色
				graph.p[i].chooseNum = graph.colorNum;
				graph.p[i].degree = 0;  //邻点数初始为0
				memset(graph.p[i].choose, 1, sizeof(graph.p[i].choose)); //初始化所有颜色可选
			}
			graph.colorDrawn = new int[graph.colorNum + 1] {0};
		}
		else if (token == "c") {//无关数据不用存
			string description;
			getline(iss, description);
		}
		else if (token == "e") {  // 如果单词为 "e"，表示读取到了边的信息
			int v1, v2;  // 用于存储边连接的两个顶点的索引
			iss >> v1 >> v2;  // 读取边连接的两个顶点的索引
			graph.Map[v1][v2] = 1;  // 在邻接矩阵中标记边的存在
			graph.Map[v2][v1] = 1;  // 无向图需将对称位置也标记为1
			graph.p[v1].degree++;  //增加度数
			graph.p[v2].degree++;  //增加度数
		}
	}
	for (int i = 1; i <= graph.n; i++) {
		graph.p[i].adjPoint = new int[graph.p[i].degree];  //邻点数组指针动态分配
		int k = 0;  //邻点数组下标初始为0
		for (int j = 1; k < graph.p[i].degree; j++)
		{
			if (graph.Map[i][j] == 1) {
				graph.p[i].adjPoint[k++] = j;  //写入邻点
			}
		}
	}
	for (int i = 1; i <= graph.n; i++) {
		graph.b[i] = i;
	}
	sort(graph.b + 1, graph.b + graph.n + 1, cmp);  //按优先级排序
}

void Random() {
	int e;
	cout << "请输入点数 边数 可涂颜色数：";
	cin >> graph.n >> e >> graph.colorNum;

	random_device rd;//用于生成随机数

	mt19937 gen(rd());//均匀分布，数据随机性较高
	uniform_int_distribution<>distrib(0, 1e9);

	int z = 0, v1, v2;  //j记录生成边数

	graph.Map = new int* [graph.n + 1];
	for (int i = 0; i <= graph.n; i++) {
		graph.Map[i] = new int[graph.n + 1] {0};
	}
	graph.p = new Point[graph.n + 1];
	graph.b = new int[graph.n + 1];
	for (int i = 1; i <= graph.n; i++)  //点集初始化
	{
		graph.p[i].id = i;
		graph.p[i].color = 0;  //颜色初始(0)无颜色
		graph.p[i].chooseNum = graph.colorNum;
		graph.p[i].degree = 0;  //邻点数初始为0
		memset(graph.p[i].choose, 1, sizeof(graph.p[i].choose)); //可选色全部初选为可选(1)
	}
	graph.colorDrawn = new int[graph.colorNum + 1] {0};

	while (z < e) {
		v1 = distrib(gen) % (graph.n) + 1;
		v2 = distrib(gen) % (graph.n) + 1;
		cout << v1 << " " << v2 << endl;
		//cout << v1 << " " << v2 << endl;
		if (graph.Map[v1][v2] == 0 && v1 != v2) {  //如果合法
			graph.Map[v1][v2] = 1; //记录相邻
			graph.Map[v2][v1] = 1; //记录相邻
			graph.p[v1].degree++;  //度数增加
			graph.p[v2].degree++;  //度数增加
			z++;
		}
	}

	for (int i = 1; i <= graph.n; i++) {
		graph.p[i].adjPoint = new int[graph.p[i].degree];  //邻点数组指针动态分配
		int k = 0;  //邻点数组下标初始为0
		for (int j = 1; k < graph.p[i].degree; j++)
		{
			if (graph.Map[i][j] == 1) {
				graph.p[i].adjPoint[k++] = j;  //写入邻点
			}
		}
	}
	for (int i = 1; i <= graph.n; i++) {
		graph.b[i] = i;
	}
	sort(graph.b + 1, graph.b + graph.n + 1, cmp);  //按优先级排序
}

void Test1() {
	graph.n = 9;
	graph.colorNum = 4;
	graph.Map = new int* [graph.n + 1];
	for (int i = 0; i <= graph.n; i++) {
		graph.Map[i] = new int[graph.n + 1] {0};
	}
	graph.p = new Point[graph.n + 1];
	graph.b = new int[graph.n + 1];
	for (int i = 1; i <= graph.n; i++)  //点集初始化
	{
		graph.p[i].id = i;
		graph.p[i].color = 0;  //颜色初始(0)无颜色
		graph.p[i].chooseNum = graph.colorNum;
		graph.p[i].degree = 0;  //邻点数初始为0
		memset(graph.p[i].choose, 1, sizeof(graph.p[i].choose)); //可选色全部初选为可选(1)
	}
	graph.colorDrawn = new int[graph.colorNum + 1] {0};

	graph.Map[1][2] = graph.Map[1][3] = graph.Map[1][4] = graph.Map[2][1] = graph.Map[3][1] = graph.Map[4][1] = 1;
	graph.Map[2][3] = graph.Map[2][4] = graph.Map[2][6] = graph.Map[3][2] = graph.Map[4][2] = graph.Map[6][2] = 1;
	graph.Map[3][4] = graph.Map[4][3] = 1;
	graph.Map[4][5] = graph.Map[4][6] = graph.Map[4][7] = graph.Map[5][4] = graph.Map[6][4] = graph.Map[7][4] = 1;
	graph.Map[5][7] = graph.Map[5][9] = graph.Map[7][5] = graph.Map[9][5] = 1;
	graph.Map[6][7] = graph.Map[6][8] = graph.Map[7][6] = graph.Map[8][6] = 1;
	graph.Map[7][8] = graph.Map[7][9] = graph.Map[8][7] = graph.Map[9][7] = 1;
	graph.Map[8][9] = graph.Map[9][8] = 1;

	graph.p[1].degree = 3;
	graph.p[2].degree = 4;
	graph.p[3].degree = 3;
	graph.p[4].degree = 6;
	graph.p[5].degree = 3;
	graph.p[6].degree = 4;
	graph.p[7].degree = 5;
	graph.p[8].degree = 3;
	graph.p[9].degree = 3;


	for (int i = 1; i <= graph.n; i++) {
		graph.p[i].adjPoint = new int[graph.p[i].degree];  //邻点数组指针动态分配
		int k = 0;  //邻点数组下标初始为0
		for (int j = 1; k < graph.p[i].degree; j++)
		{
			if (graph.Map[i][j] == 1) {
				graph.p[i].adjPoint[k++] = j;  //写入邻点
			}
		}
	}
	for (int i = 1; i <= graph.n; i++) {
		graph.b[i] = i;
	}
	sort(graph.b + 1, graph.b + graph.n + 1, cmp);  //按优先级排序
}

inline bool colorAdj(int& id) {
	int flag = graph.colorDrawn[graph.p[id].color];
	if (flag == 0 || graph.p[flag].color == 0) {  //如果该颜色未出现，标记
		graph.colorDrawn[graph.p[id].color] = id;  //标记首结点（颜色轮换）
	}
	for (int j = 0; j < graph.p[id].degree; j++)  //遍历邻点更新色
	{
		int adj = graph.p[id].adjPoint[j];  //邻点id
		if (graph.p[adj].choose[graph.p[id].color] == 1) {
			graph.p[adj].choose[graph.p[id].color] = 0;  //邻点对应可选色删除
			graph.p[adj].chooseNum--;
			if (graph.p[adj].chooseNum == 0) {//向前遍历，若相邻节点出现无色可填情况则直接结束填色
				return false;
			}
		}
	}
	return true;
}
inline void updateColor(int& id) {
	for (int i = 0; i < graph.p[id].degree; i++)  //遍历该点全部邻点(这些点需要颜色更新)
	{
		int adj = graph.p[id].adjPoint[i];  //取出该邻点id
		memset(graph.p[adj].choose, true, sizeof(graph.p[i].choose));  //该邻点颜色选择初始化
		for (int j = 0; j < graph.p[adj].degree; j++)  //遍历该邻点的全部邻点，确定该邻点的可选色情况
		{
			int aadj = graph.p[adj].adjPoint[j];  //取出该邻点的某一邻点的id
			int color = graph.p[aadj].color;  //取出该邻点的某一邻点的颜色
			if (graph.p[adj].choose[color] == 1) {
				graph.p[adj].choose[color] = 0;  //将该邻点对应可选色去除
			}
		}
		graph.p[adj].chooseNum = 0;  //重新计算该邻点可选色数，先初始为0
		for (int j = 1; j <= graph.colorNum; j++) {
			graph.p[adj].chooseNum += graph.p[adj].choose[j];  //计算该邻点可选色数
		}
	}
}
long long c[1005];
int col = 0;
void init() {//自定义测试数据
	freopen("in.txt", "r", stdin);
	cin >> graph.n;
	int m;
	cin >> m;
	graph.colorNum = 4;
	graph.Map = new int* [graph.n + 1];
	for (int i = 0; i <= graph.n; i++) {
		graph.Map[i] = new int[graph.n + 1] {0};
	}
	graph.p = new Point[graph.n + 1];
	graph.b = new int[graph.n + 1];
	for (int i = 1; i <= graph.n; i++)  //点集初始化
	{
		graph.p[i].id = i;
		graph.p[i].color = 0;  //颜色初始(0)无颜色
		graph.p[i].chooseNum = graph.colorNum;
		graph.p[i].degree = 0;  //邻点数初始为0
		memset(graph.p[i].choose, 1, sizeof(graph.p[i].choose)); //可选色全部初选为可选(1)
	}
	for (int i = 1; i <= m; i++) {
		int l, r;
		cin >> l >> r;
		graph.Map[l][r] = graph.Map[r][l] = 1;
		graph.p[l].degree++;
		graph.p[r].degree++;
	}
	graph.colorDrawn = new int[graph.colorNum + 1] {0};

	for (int i = 1; i <= graph.n; i++) {
		graph.p[i].adjPoint = new int[graph.p[i].degree];  //邻点数组指针动态分配
		int k = 0;  //邻点数组下标初始为0
		for (int j = 1; k < graph.p[i].degree; j++)
		{
			if (graph.Map[i][j] == 1) {
				graph.p[i].adjPoint[k++] = j;  //写入邻点
			}
		}
	}
	for (int i = 1; i <= graph.n; i++) {
		graph.b[i] = i;
	}
	sort(graph.b + 1, graph.b + graph.n + 1, cmp);  //按优先级排序
}
void printColor() {
	for (int i = 1; i <= graph.n; i++) {
		cout << graph.p[i].color << " ";
	}cout << endl;
}
int col_num[1005] = { 0 };
void dfs(int t) {
	if (cnt >= FindNum) return; // 如果达到预设的解数，则直接返回
	if (t > graph.n) {
		cnt += c[col]; // 找到的着色方案数量增加
		cout << cnt << endl;
		//cout << col << endl;
		//printColor();
		return;
	}

	int id = graph.b[t]; // 获取当前节点在图中的实际编号
	// 遍历当前节点的所有可选颜色
	for (int i = graph.p[id].color + 1; i <= graph.colorNum && graph.colorDrawn[graph.p[id].color] != id; i++) {
		if (graph.p[id].color != 0) {
			col_num[graph.p[id].color]--;
			if (col_num[graph.p[id].color] == 0)col--;
			graph.p[id].color = 0; // 将当前节点的颜色重置为0（无颜色）
			updateColor(id); // 更新邻接节点的颜色信息
		}
		// 如果当前颜色是可选的
		if (graph.p[id].choose[i] == 1) {
			graph.p[id].color = i; // 设置当前节点的颜色
			if (col_num[graph.p[id].color] == 0)col++;
			col_num[graph.p[id].color]++;

			// 如果颜色相邻性检查通过
			if (colorAdj(id)) {
				sort(graph.b + t + 1, graph.b + graph.n + 1, cmp); // 对剩余节点进行排序
				dfs(t + 1); // 递归地对下一个节点进行着色
			}
		}
	}
	// 如果当前节点的颜色不是最后一个颜色，并且最后一个颜色的节点是当前节点
	if (t - 1 <= graph.colorNum && graph.colorDrawn[graph.colorNum] == graph.b[graph.colorNum]) {
		return; // 返回
	}
	// 如果当前节点有颜色
	if (graph.p[id].color != 0) {
		col_num[graph.p[id].color]--;
		if (col_num[graph.p[id].color] == 0)col--;
		graph.p[id].color = 0; // 将当前节点的颜色重置为0（无颜色）
		updateColor(id); // 更新邻接节点的颜色信息
	}
}


int main() {
	clock_t startTime, endTime;//记录时间
	cout << "输入1读取地图 输入2生成随机地图 输入3验证任务一" << endl;
	int mode; cin >> mode;
	if (mode == 1) {
		cout << "文件名： " << file << endl;
		FindNum = 100000;
		cout << "找" << FindNum << "组解" << endl;
		ReadGraph(file);  //读入地图
	}
	else if (mode == 2) {
		FindNum = 1e10;
		cout << "找1e10组" << endl;
		Random();
	}
	else if (mode == 3) {
		Test1();

	}
	else {
		init();
	}
	c[0] = 1;
	for (int i = 1; i <= graph.colorNum; i++) {
		c[i] = c[i - 1] * (graph.colorNum - i + 1);
		//cout << c[i] << " ";
	}
	//cout << endl;
	//cout << "颜色数：" << graph.colorNum << endl;

	//clock_t startTime, endTime;//记录时间
	/*int begin = 0;找le450_15b.col的起始点，不能从1开始跑
	for (int i = 1; i <= graph.n; i++) {
		if (graph.b[i] == 4) {
			begin = i;
			break;
		}
	}*/

	startTime = clock();//开始
	dfs(1);
	endTime = clock();//结束

	cout << "共找到" << fixed << setprecision(0) << cnt << "组答案" << endl;
	cout << "运行时间为" << fixed << setprecision(5) << (double)(endTime - startTime) / CLOCKS_PER_SEC << "s" << endl;

	return 0;
}