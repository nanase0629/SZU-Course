#include<stack>
#include <iostream>
#include<algorithm>
#include <fstream>
#include <chrono>
#include<vector>
#include <random>
#include <stdlib.h>
#include <Windows.h>
using namespace std;
int ans = 0;

struct Map {
    vector<vector<int>> map; // �ڽӾ��󣬱�ʾͼ�еı�
    bool visited[1000000] = { false }; // ��ǽڵ��Ƿ񱻷��ʹ�
    vector<pair<int, int>> edges; // �洢���бߵ��б�
    vector<pair<int, int>> notTreeEdges; // �洢�����ߵ��б�
    bool notLoopEdges[10000000] = { false }; // ��Ǳ��Ƿ��ڻ���
    int depth[10000000] = {0}; // �洢�ڵ�����
    int father[1000000]; // �洢�ڵ�ĸ��ڵ㣬���ڲ��鼯
    int fa[1000000] ;
    int vertexNumber; // �ڵ������

    // ���캯������ʼ��ͼ�����ݽṹ
    Map(int edgeNumber, int vertexNumber) : vertexNumber(vertexNumber) {
        //cout << vertexNumber << endl;
        map.resize(vertexNumber); // ��ʼ���ڽӾ���

        for (int i = 0; i < vertexNumber; i++) {
            fa[i] = i;
            father[i] = i; // ��ʼ��ÿ���ڵ�ĸ��ڵ�Ϊ�Լ�
        }
    }

     //�������鼯��
     inline void buildTree(int& current ,int currentFather) {
        if (currentFather == -1)depth[current] = 1;
        else depth[current] = depth[currentFather]+1; // ���õ�ǰ�ڵ�����
        father[current] = currentFather; // ���õ�ǰ�ڵ�ĸ��ڵ�
        visited[current] = true; // ��ǵ�ǰ�ڵ�Ϊ�ѷ���
        for (auto& son : map[current]) {
            if (!visited[son]) {
                ans++;
                notLoopEdges[son] = true; // ����ӽڵ�Ϊ�ǻ���
                buildTree(son, current); // �ݹ鹹������
            }
        }
     }


    // �������鼯��
    void createTree() {
        for (int i = 0; i < vertexNumber; i++) {
            if (!visited[i]) {
                buildTree(i,-1); // ��δ���ʵĽڵ㿪ʼ����
            }
        }
    }

    // ��ӱߵ�ͼ��
    void addEdge(int head, int tail, bool init = false) {
        map[head].push_back(tail);
        map[tail].push_back(head);
        if (init) edges.emplace_back(head, tail);
    }

    // ���ҷ�����
    void findNotTreeEdge() {
        for (auto& edge : edges) {
            if (father[edge.first] != edge.second && father[edge.second] != edge.first) {
                notTreeEdges.emplace_back(edge.first, edge.second); // ��ӷ����ߵ��б�
            }
        }
    }

    // ѹ��·��
    inline int find(int x) {
        if (x == fa[x]||x==-1)return x;
        return fa[x] = find(fa[x]);
    }

    // ���һ���
    void LCA(int x,int y) {
        int u = x;
        int v = y;
        //cout << x << " " << y << endl;
        u = find(u);
        v = find(v);
        while (u!=v) {
            if (depth[u] > depth[v]) {//������ȷ���
                notLoopEdges[u] = false; // ��Ǳ�Ϊ����
                fa[u] = father[u];
            }
            else if (depth[u] < depth[v]) {
                notLoopEdges[v] = false; 
                fa[v] = father[v];
            }
            else{
                notLoopEdges[u] = false; 
                fa[u] = father[u];
                notLoopEdges[v] = false; 
                fa[v] = father[v];
            }
            u = find(u);
            v = find(v);
        }
    }

    // ������
    void findBridge() {
        clock_t start, end;
        start = clock();
        createTree(); // �������鼯��
        end = clock();
        cout << (end - start) << endl;
        start = clock();
        findNotTreeEdge(); // ���ҷ�����
        end = clock();
        cout << (end - start) << endl;
        start = clock();
        for (int i = 0; i < notTreeEdges.size(); i++) {
            pair<int, int>edge = notTreeEdges[i];
            LCA(edge.first,edge.second); // ���һ���
        }
        end = clock();
        cout << (end - start) << endl;
    }

    // ��ʾ��
    void showBridge() {
        int n = 0;
        for (int i = 0; i < vertexNumber; i++) {
            if (notLoopEdges[i]) {
                //n++; // �����ŵ�����
                cout << i << '-' << father[i] << endl; // ����ŵ���Ϣ
            }
        }
        cout << "�ŵ�����Ϊ��" << n << endl; // ����ŵ�����
    }
};

int main() {
    cout << "����1Ϊ����ͼ ����2Ϊ���ͼ" << endl;
    int mode;
    cin >> mode;
    if (mode == 1) {
        freopen("largeG.txt", "r", stdin);

        int edgeNumber;
        int vertexNumber;
        int head;
        int tail;
        scanf("%d %d", &vertexNumber, &edgeNumber);
        //Graph map(vertexNumber+10);
        cout << vertexNumber << " " << edgeNumber << endl;
        Map map(edgeNumber, vertexNumber);
        int tmp = 0;
        //!file.eof()

        for(int i=1;i<=edgeNumber;i++){
            //if(tmp%100000==0)cout << tmp << endl;
            scanf("%d %d", &head, &tail);
            // cout << head << " " << tail << endl;
            map.addEdge(head, tail, true);
        }

        cout << "��ʼ����..." << endl;

        clock_t start_time, end_time;
        start_time = clock();
        map.findBridge();
        end_time = clock();
        map.showBridge();  
        cout << "�Ż�Ѱ��ʱ�䣺" << end_time - start_time << "ms" << endl;
    }
    else {
        random_device rd;//�������������
        mt19937 gen(rd());//���ȷֲ�����������Խϸ�
        uniform_int_distribution<>distrib(1, 100000);
        
        int vertexNumber= 5000;//��
        int edgeNumber= vertexNumber*vertexNumber;//��
        cout << vertexNumber << " " << edgeNumber << endl;

        Map map(edgeNumber, vertexNumber);
        int head,tail;
        for (int i = 0; i < edgeNumber; i++) {
            mt19937 gen2(rd());//���ȷֲ�����������Խϸ�
            uniform_int_distribution<>distrib2(0, vertexNumber-1);
            head = distrib2(gen2);
            tail = distrib2(gen2);
            map.addEdge(head, tail, true);
        }

        cout << "��ʼ����..." << endl;

        clock_t start_time, end_time;
        start_time = clock();
        map.findBridge();
        end_time = clock();

        //map.showBridge();  
        cout << "�Ż�Ѱ��ʱ�䣺" << end_time - start_time << "ms" << endl;

    }


}
