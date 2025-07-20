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

string file = "le450_5a.col";  //��ͼ�����ļ���
long long FindNum = 0x7fffffff;//��Ҫ�ҵ���������Ľ�

struct Point {
	int id;//�±�
	int color; //��ǰ��ɫ
	int chooseNum; //��ѡ��ɫ
	int degree; //����
	bool choose[30]; //�±��Ӧ��ɫ��1�����ѡ��0������ѡ���˴�ֱ�ӿ�30ɫ���飬��֤ʵ��������ɫ��<30
	int* adjPoint; //��¼���ڵ��±�
};

struct LeightonGraph {
	int n;// ͼ�ж�����
	int cnt = 0;//��ĸ���
	int* color;//ÿ�������ɫ
	int colorNum = 5;//��ɫ����
	int** Map;//�ڽӾ����¼ͼ
	int* colorDrawn;  //�����ж���ɫ��Ѱ
	Point* p;  //�㼯
	int* b; //�����õ�`
}graph;

long long cnt = 0;  //��¼����

bool cmp(int a1, int a2) {
	if (graph.p[a1].chooseNum == graph.p[a2].chooseNum) {  //����MVR
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
	ifstream file(filename);  // ���ļ���
	string line;            // ���ڴ洢��ȡ��ÿһ�����ݵ��ַ���
	if (!file.is_open()) {
		cerr << "�����޷����ļ� " << filename << endl;  // ���������Ϣ
		return;
	}
	while (getline(file, line)) {
		istringstream iss(line);  // ʹ���ַ���������ÿһ������
		string token;  // �洢��ǰ�еĵ�һ������
		iss >> token;  // �ӵ�ǰ������ȡ��һ������

		// �������Ϊ "p"����ʾ��ȡ���˶�������Ϣ
		if (token == "p") {
			iss >> token >> graph.n;  // ��ȡ������
			graph.Map = new int* [graph.n + 1];
			for (int i = 0; i <= graph.n; i++) {
				graph.Map[i] = new int[graph.n + 1];
			}
			graph.p = new Point[graph.n + 1];
			graph.b = new int[graph.n + 1];
			for (int i = 1; i <= graph.n; i++)  //�㼯��ʼ��
			{
				graph.p[i].id = i;
				graph.p[i].color = 0;  //0������ɫ
				graph.p[i].chooseNum = graph.colorNum;
				graph.p[i].degree = 0;  //�ڵ�����ʼΪ0
				memset(graph.p[i].choose, 1, sizeof(graph.p[i].choose)); //��ʼ��������ɫ��ѡ
			}
			graph.colorDrawn = new int[graph.colorNum + 1] {0};
		}
		else if (token == "c") {//�޹����ݲ��ô�
			string description;
			getline(iss, description);
		}
		else if (token == "e") {  // �������Ϊ "e"����ʾ��ȡ���˱ߵ���Ϣ
			int v1, v2;  // ���ڴ洢�����ӵ��������������
			iss >> v1 >> v2;  // ��ȡ�����ӵ��������������
			graph.Map[v1][v2] = 1;  // ���ڽӾ����б�ǱߵĴ���
			graph.Map[v2][v1] = 1;  // ����ͼ�轫�Գ�λ��Ҳ���Ϊ1
			graph.p[v1].degree++;  //���Ӷ���
			graph.p[v2].degree++;  //���Ӷ���
		}
	}
	for (int i = 1; i <= graph.n; i++) {
		graph.p[i].adjPoint = new int[graph.p[i].degree];  //�ڵ�����ָ�붯̬����
		int k = 0;  //�ڵ������±��ʼΪ0
		for (int j = 1; k < graph.p[i].degree; j++)
		{
			if (graph.Map[i][j] == 1) {
				graph.p[i].adjPoint[k++] = j;  //д���ڵ�
			}
		}
	}
	for (int i = 1; i <= graph.n; i++) {
		graph.b[i] = i;
	}
	sort(graph.b + 1, graph.b + graph.n + 1, cmp);  //�����ȼ�����
}

void Random() {
	int e;
	cout << "��������� ���� ��Ϳ��ɫ����";
	cin >> graph.n >> e >> graph.colorNum;

	random_device rd;//�������������

	mt19937 gen(rd());//���ȷֲ�����������Խϸ�
	uniform_int_distribution<>distrib(0, 1e9);

	int z = 0, v1, v2;  //j��¼���ɱ���

	graph.Map = new int* [graph.n + 1];
	for (int i = 0; i <= graph.n; i++) {
		graph.Map[i] = new int[graph.n + 1] {0};
	}
	graph.p = new Point[graph.n + 1];
	graph.b = new int[graph.n + 1];
	for (int i = 1; i <= graph.n; i++)  //�㼯��ʼ��
	{
		graph.p[i].id = i;
		graph.p[i].color = 0;  //��ɫ��ʼ(0)����ɫ
		graph.p[i].chooseNum = graph.colorNum;
		graph.p[i].degree = 0;  //�ڵ�����ʼΪ0
		memset(graph.p[i].choose, 1, sizeof(graph.p[i].choose)); //��ѡɫȫ����ѡΪ��ѡ(1)
	}
	graph.colorDrawn = new int[graph.colorNum + 1] {0};

	while (z < e) {
		v1 = distrib(gen) % (graph.n) + 1;
		v2 = distrib(gen) % (graph.n) + 1;
		cout << v1 << " " << v2 << endl;
		//cout << v1 << " " << v2 << endl;
		if (graph.Map[v1][v2] == 0 && v1 != v2) {  //����Ϸ�
			graph.Map[v1][v2] = 1; //��¼����
			graph.Map[v2][v1] = 1; //��¼����
			graph.p[v1].degree++;  //��������
			graph.p[v2].degree++;  //��������
			z++;
		}
	}

	for (int i = 1; i <= graph.n; i++) {
		graph.p[i].adjPoint = new int[graph.p[i].degree];  //�ڵ�����ָ�붯̬����
		int k = 0;  //�ڵ������±��ʼΪ0
		for (int j = 1; k < graph.p[i].degree; j++)
		{
			if (graph.Map[i][j] == 1) {
				graph.p[i].adjPoint[k++] = j;  //д���ڵ�
			}
		}
	}
	for (int i = 1; i <= graph.n; i++) {
		graph.b[i] = i;
	}
	sort(graph.b + 1, graph.b + graph.n + 1, cmp);  //�����ȼ�����
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
	for (int i = 1; i <= graph.n; i++)  //�㼯��ʼ��
	{
		graph.p[i].id = i;
		graph.p[i].color = 0;  //��ɫ��ʼ(0)����ɫ
		graph.p[i].chooseNum = graph.colorNum;
		graph.p[i].degree = 0;  //�ڵ�����ʼΪ0
		memset(graph.p[i].choose, 1, sizeof(graph.p[i].choose)); //��ѡɫȫ����ѡΪ��ѡ(1)
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
		graph.p[i].adjPoint = new int[graph.p[i].degree];  //�ڵ�����ָ�붯̬����
		int k = 0;  //�ڵ������±��ʼΪ0
		for (int j = 1; k < graph.p[i].degree; j++)
		{
			if (graph.Map[i][j] == 1) {
				graph.p[i].adjPoint[k++] = j;  //д���ڵ�
			}
		}
	}
	for (int i = 1; i <= graph.n; i++) {
		graph.b[i] = i;
	}
	sort(graph.b + 1, graph.b + graph.n + 1, cmp);  //�����ȼ�����
}

inline bool colorAdj(int& id) {
	int flag = graph.colorDrawn[graph.p[id].color];
	if (flag == 0 || graph.p[flag].color == 0) {  //�������ɫδ���֣����
		graph.colorDrawn[graph.p[id].color] = id;  //����׽�㣨��ɫ�ֻ���
	}
	for (int j = 0; j < graph.p[id].degree; j++)  //�����ڵ����ɫ
	{
		int adj = graph.p[id].adjPoint[j];  //�ڵ�id
		if (graph.p[adj].choose[graph.p[id].color] == 1) {
			graph.p[adj].choose[graph.p[id].color] = 0;  //�ڵ��Ӧ��ѡɫɾ��
			graph.p[adj].chooseNum--;
			if (graph.p[adj].chooseNum == 0) {//��ǰ�����������ڽڵ������ɫ���������ֱ�ӽ�����ɫ
				return false;
			}
		}
	}
	return true;
}
inline void updateColor(int& id) {
	for (int i = 0; i < graph.p[id].degree; i++)  //�����õ�ȫ���ڵ�(��Щ����Ҫ��ɫ����)
	{
		int adj = graph.p[id].adjPoint[i];  //ȡ�����ڵ�id
		memset(graph.p[adj].choose, true, sizeof(graph.p[i].choose));  //���ڵ���ɫѡ���ʼ��
		for (int j = 0; j < graph.p[adj].degree; j++)  //�������ڵ��ȫ���ڵ㣬ȷ�����ڵ�Ŀ�ѡɫ���
		{
			int aadj = graph.p[adj].adjPoint[j];  //ȡ�����ڵ��ĳһ�ڵ��id
			int color = graph.p[aadj].color;  //ȡ�����ڵ��ĳһ�ڵ����ɫ
			if (graph.p[adj].choose[color] == 1) {
				graph.p[adj].choose[color] = 0;  //�����ڵ��Ӧ��ѡɫȥ��
			}
		}
		graph.p[adj].chooseNum = 0;  //���¼�����ڵ��ѡɫ�����ȳ�ʼΪ0
		for (int j = 1; j <= graph.colorNum; j++) {
			graph.p[adj].chooseNum += graph.p[adj].choose[j];  //������ڵ��ѡɫ��
		}
	}
}
long long c[1005];
int col = 0;
void init() {//�Զ����������
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
	for (int i = 1; i <= graph.n; i++)  //�㼯��ʼ��
	{
		graph.p[i].id = i;
		graph.p[i].color = 0;  //��ɫ��ʼ(0)����ɫ
		graph.p[i].chooseNum = graph.colorNum;
		graph.p[i].degree = 0;  //�ڵ�����ʼΪ0
		memset(graph.p[i].choose, 1, sizeof(graph.p[i].choose)); //��ѡɫȫ����ѡΪ��ѡ(1)
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
		graph.p[i].adjPoint = new int[graph.p[i].degree];  //�ڵ�����ָ�붯̬����
		int k = 0;  //�ڵ������±��ʼΪ0
		for (int j = 1; k < graph.p[i].degree; j++)
		{
			if (graph.Map[i][j] == 1) {
				graph.p[i].adjPoint[k++] = j;  //д���ڵ�
			}
		}
	}
	for (int i = 1; i <= graph.n; i++) {
		graph.b[i] = i;
	}
	sort(graph.b + 1, graph.b + graph.n + 1, cmp);  //�����ȼ�����
}
void printColor() {
	for (int i = 1; i <= graph.n; i++) {
		cout << graph.p[i].color << " ";
	}cout << endl;
}
int col_num[1005] = { 0 };
void dfs(int t) {
	if (cnt >= FindNum) return; // ����ﵽԤ��Ľ�������ֱ�ӷ���
	if (t > graph.n) {
		cnt += c[col]; // �ҵ�����ɫ������������
		cout << cnt << endl;
		//cout << col << endl;
		//printColor();
		return;
	}

	int id = graph.b[t]; // ��ȡ��ǰ�ڵ���ͼ�е�ʵ�ʱ��
	// ������ǰ�ڵ�����п�ѡ��ɫ
	for (int i = graph.p[id].color + 1; i <= graph.colorNum && graph.colorDrawn[graph.p[id].color] != id; i++) {
		if (graph.p[id].color != 0) {
			col_num[graph.p[id].color]--;
			if (col_num[graph.p[id].color] == 0)col--;
			graph.p[id].color = 0; // ����ǰ�ڵ����ɫ����Ϊ0������ɫ��
			updateColor(id); // �����ڽӽڵ����ɫ��Ϣ
		}
		// �����ǰ��ɫ�ǿ�ѡ��
		if (graph.p[id].choose[i] == 1) {
			graph.p[id].color = i; // ���õ�ǰ�ڵ����ɫ
			if (col_num[graph.p[id].color] == 0)col++;
			col_num[graph.p[id].color]++;

			// �����ɫ�����Լ��ͨ��
			if (colorAdj(id)) {
				sort(graph.b + t + 1, graph.b + graph.n + 1, cmp); // ��ʣ��ڵ��������
				dfs(t + 1); // �ݹ�ض���һ���ڵ������ɫ
			}
		}
	}
	// �����ǰ�ڵ����ɫ�������һ����ɫ���������һ����ɫ�Ľڵ��ǵ�ǰ�ڵ�
	if (t - 1 <= graph.colorNum && graph.colorDrawn[graph.colorNum] == graph.b[graph.colorNum]) {
		return; // ����
	}
	// �����ǰ�ڵ�����ɫ
	if (graph.p[id].color != 0) {
		col_num[graph.p[id].color]--;
		if (col_num[graph.p[id].color] == 0)col--;
		graph.p[id].color = 0; // ����ǰ�ڵ����ɫ����Ϊ0������ɫ��
		updateColor(id); // �����ڽӽڵ����ɫ��Ϣ
	}
}


int main() {
	clock_t startTime, endTime;//��¼ʱ��
	cout << "����1��ȡ��ͼ ����2���������ͼ ����3��֤����һ" << endl;
	int mode; cin >> mode;
	if (mode == 1) {
		cout << "�ļ����� " << file << endl;
		FindNum = 100000;
		cout << "��" << FindNum << "���" << endl;
		ReadGraph(file);  //�����ͼ
	}
	else if (mode == 2) {
		FindNum = 1e10;
		cout << "��1e10��" << endl;
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
	//cout << "��ɫ����" << graph.colorNum << endl;

	//clock_t startTime, endTime;//��¼ʱ��
	/*int begin = 0;��le450_15b.col����ʼ�㣬���ܴ�1��ʼ��
	for (int i = 1; i <= graph.n; i++) {
		if (graph.b[i] == 4) {
			begin = i;
			break;
		}
	}*/

	startTime = clock();//��ʼ
	dfs(1);
	endTime = clock();//����

	cout << "���ҵ�" << fixed << setprecision(0) << cnt << "���" << endl;
	cout << "����ʱ��Ϊ" << fixed << setprecision(5) << (double)(endTime - startTime) / CLOCKS_PER_SEC << "s" << endl;

	return 0;
}