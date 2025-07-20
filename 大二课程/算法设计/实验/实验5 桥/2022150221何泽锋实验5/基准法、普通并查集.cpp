#include <iostream>
#include <algorithm>
#include <vector>
#include <random>
#include <stdlib.h>
#include <Windows.h>
#include<iomanip>
using namespace std;

// ���鼯���ݽṹ
struct UnionFind {
    vector<int> parent; // �洢ÿ���ڵ�ĸ��ڵ�
    vector<int> rank; // �洢ÿ���ڵ����

    // ��ʼ�����鼯
    void init(int n) {
        parent.resize(n);
        rank.resize(n);
        for (int i = 0; i < n; i++) {
            parent[i] = i; // ��ʼ��ÿ���ڵ�ĸ��ڵ�Ϊ�Լ�
            rank[i] = 0; // ��ʼ��ÿ���ڵ����Ϊ0
        }
    }

    // ���Ҳ�����ʵ��·��ѹ��
    int find(int x) {
        if (x == parent[x]) return x;
        return parent[x] = find(parent[x]); // ·��ѹ��
    }

    // �ϲ����������Ⱥϲ���������
    void unionSet(int x, int y) {
        int rootX = find(x);
        int rootY = find(y);
        if (rootX != rootY) {
            // ���Ƚ�С�����ĸ��ڵ����ӵ��Ƚϴ�����ĸ��ڵ�
            if (rank[rootX] < rank[rootY]) {
                parent[rootX] = rootY;
            }
            else if (rank[rootX] > rank[rootY]) {
                parent[rootY] = rootX;
            }
            else {
                // ����ͬ��ѡ������һ����Ϊ��������������
                parent[rootY] = rootX;
                rank[rootX]++;
            }
        }
    }
};

// ͼ�࣬ʹ���ڽӾ���
struct Graph {
    int V; // ������
    int E;//����
    vector<vector<int>> adjMatrix; // �ڽӾ���
    vector<int>visit;//����Ƿ����
    UnionFind uf;
    Graph() {};
    Graph(int V) {
        this->V = V;
        adjMatrix.resize(V, vector<int>(V, 0));
        visit.resize(V,0);
        uf.init(V);
    }

    void Resize() {// ��ʼ���ṹ��
        adjMatrix.resize(V, vector<int>(V, 0));
        visit.resize(V, false);
    }
    void addEdge(int v, int w) {//��ӱ�
        adjMatrix[v][w] = 1;
        adjMatrix[w][v] = 1;
    }
    void init() {//��ʼ������ͼ��Ϣ
        for (int i = 0; i < E; i++) {
            int v, w;
            cin >> v >> w;
            addEdge(v, w);
        }
    }
    void init_random() {
        random_device rd;//�������������
        mt19937 gen(rd());//���ȷֲ�����������Խϸ�
        uniform_int_distribution<>distrib(0, V-1);
        for (int i = 0; i < E; i++) {
            int v, w;
            v = distrib(gen);
            w= distrib(gen);
            addEdge(v, w);
        }
    }
}g;

void DFS(int vertex) {
    // ��ǵ�ǰ�ڵ�Ϊ�ѷ���
    g.visit[vertex] = true;
    // ���������ڽӽڵ�
    for (int i = 0; i < g.V; ++i) {
        // ����ڽӽڵ�δ�����ʣ���ݹ����
        if (g.adjMatrix[vertex][i] && !g.visit[i]) {
            DFS(i);
        }
    }
}
int Find_Block_num() {
    int count = 0; // ��ͨ�������
    // �������ж���
    for (int i = 0; i < g.V; ++i) {
        // �����ǰ����δ�����ʣ������DFS��������������ͨ�����
        if (!g.visit[i]) {
            DFS(i);
            count++;
        }
    }
    // ����visit���飬�Ա��´�ʹ��
    fill(g.visit.begin(), g.visit.end(), false);

    return count; // ������ͨ�������
}

int base() {//��׼��
    int block = Find_Block_num();//��ʼ��ͨ������
    int bridge = 0;//��¼�ŵ�����
    for (int i = 0; i < g.V; i++) {//����ͼֻ�����������
        for (int j = i+1; j < g.V; j++) {
            if (g.adjMatrix[i][j] ==1) {//����б�
                g.adjMatrix[i][j] = g.adjMatrix[j][i] = 0;//ȥ���˱�
                int tmp = Find_Block_num();
                g.adjMatrix[i][j] = g.adjMatrix[j][i]= 1;
                if (tmp > block) {
                   // printf("(%d,%d)\n", i, j);
                    bridge++;
                }
            }
        }
    }
    return bridge;
}

int Uf() {
    g.uf.init(g.V);
    vector<pair<int, int>> bridges;

    // ��һ�α������������������ϲ�����
    for (int v = 0; v < g.V; v++) {
        for (int w = v + 1; w < g.V; w++) {
            if (g.adjMatrix[v][w] == 1) {
                g.uf.unionSet(v, w);
            }
        }
    }

    int block = 0;// ��ʼ��ͨ������
    for (int i = 0; i < g.V; ++i) {
        if (g.uf.find(i) == i) {
            block++;
        }
    }

    // �ڶ��α��������ÿ�����Ƿ�����
    for (int v = 0; v < g.V; ++v) {
        for (int w = v + 1; w < g.V; ++w) {
            if (g.adjMatrix[v][w] == 1) {
                // ɾ����(v, w)
                g.adjMatrix[v][w] = g.adjMatrix[w][v] = 0;

                // ���³�ʼ�����鼯
                g.uf.init(g.V);
                for (int u = 0; u < g.V; ++u) {
                    for (int z = u + 1; z < g.V; ++z) {
                        if (g.adjMatrix[u][z] == 1) {
                            g.uf.unionSet(u, z);
                        }
                    }
                }

               
                int tmp_block = 0; //ɾ���ߺ����ͨ������
                for (int i = 0; i < g.V; ++i) {
                    if (g.uf.find(i) == i) {
                        tmp_block++;
                    }
                }

                // ���ɾ���ߺ����ͨ��������ԭ���࣬��ô��(v, w)����
                if (tmp_block > block) {
                    bridges.push_back(make_pair(v, w));
                }

                // �ָ���(v, w)
                g.adjMatrix[v][w] = g.adjMatrix[w][v] = 1;
            }
        }
    }
   /* for (auto& bridge : bridges) {
        cout << "(" << bridge.first << "," << bridge.second << ")\n";
    }*/
    return bridges.size();
}


int main() {
    cout << "����1Ϊ����ͼ ����2Ϊ���ͼ" << endl;
    int mode;
    cin >> mode;
    if (mode == 1) {
        freopen("MediumDG.txt", "r", stdin);
        cin >> g.V >> g.E;
        cout << "������" << g.V << " ������" << g.E << endl;
        g.Resize();
        g.init();
    }
    else if (mode == 2) {
        random_device rd;//�������������
        mt19937 gen(rd());//���ȷֲ�����������Խϸ�
        uniform_int_distribution<>distrib(1, 100);
        g.V = 200;
        g.E =40000;
        cout << "������" << g.V << " ������" << g.E << endl;
        g.Resize();
        g.init_random();
    }
    cout << "��ʼѰ��..." << endl;

    // �ҵ����е���
    int ans;
    clock_t start_time, end_time;//��¼ʱ��
    start_time = clock();
    ans=base();
    end_time = clock();
    cout << "��׼����ʱ��" << fixed << setprecision(5) << (double)end_time - start_time << "ms" << endl;

    start_time = clock();
    ans = Uf();
    end_time = clock();
    cout << "���鼯����ʱ��" << fixed << setprecision(5) << (double)end_time - start_time << "ms" << endl;
    
    cout << "�ŵ�������" << ans << endl;
    return 0;
}
