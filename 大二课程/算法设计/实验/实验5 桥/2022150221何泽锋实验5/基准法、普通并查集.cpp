#include <iostream>
#include <algorithm>
#include <vector>
#include <random>
#include <stdlib.h>
#include <Windows.h>
#include<iomanip>
using namespace std;

// 并查集数据结构
struct UnionFind {
    vector<int> parent; // 存储每个节点的父节点
    vector<int> rank; // 存储每个节点的秩

    // 初始化并查集
    void init(int n) {
        parent.resize(n);
        rank.resize(n);
        for (int i = 0; i < n; i++) {
            parent[i] = i; // 初始化每个节点的父节点为自己
            rank[i] = 0; // 初始化每个节点的秩为0
        }
    }

    // 查找操作，实现路径压缩
    int find(int x) {
        if (x == parent[x]) return x;
        return parent[x] = find(parent[x]); // 路径压缩
    }

    // 合并操作，按秩合并两个集合
    void unionSet(int x, int y) {
        int rootX = find(x);
        int rootY = find(y);
        if (rootX != rootY) {
            // 将秩较小的树的根节点连接到秩较大的树的根节点
            if (rank[rootX] < rank[rootY]) {
                parent[rootX] = rootY;
            }
            else if (rank[rootX] > rank[rootY]) {
                parent[rootY] = rootX;
            }
            else {
                // 秩相同，选择其中一个作为根，并增加其秩
                parent[rootY] = rootX;
                rank[rootX]++;
            }
        }
    }
};

// 图类，使用邻接矩阵
struct Graph {
    int V; // 顶点数
    int E;//边数
    vector<vector<int>> adjMatrix; // 邻接矩阵
    vector<int>visit;//结点是否遍历
    UnionFind uf;
    Graph() {};
    Graph(int V) {
        this->V = V;
        adjMatrix.resize(V, vector<int>(V, 0));
        visit.resize(V,0);
        uf.init(V);
    }

    void Resize() {// 初始化结构体
        adjMatrix.resize(V, vector<int>(V, 0));
        visit.resize(V, false);
    }
    void addEdge(int v, int w) {//添加边
        adjMatrix[v][w] = 1;
        adjMatrix[w][v] = 1;
    }
    void init() {//初始化输入图信息
        for (int i = 0; i < E; i++) {
            int v, w;
            cin >> v >> w;
            addEdge(v, w);
        }
    }
    void init_random() {
        random_device rd;//用于生成随机数
        mt19937 gen(rd());//均匀分布，数据随机性较高
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
    // 标记当前节点为已访问
    g.visit[vertex] = true;
    // 遍历所有邻接节点
    for (int i = 0; i < g.V; ++i) {
        // 如果邻接节点未被访问，则递归访问
        if (g.adjMatrix[vertex][i] && !g.visit[i]) {
            DFS(i);
        }
    }
}
int Find_Block_num() {
    int count = 0; // 连通块计数器
    // 遍历所有顶点
    for (int i = 0; i < g.V; ++i) {
        // 如果当前顶点未被访问，则进行DFS搜索，并增加连通块计数
        if (!g.visit[i]) {
            DFS(i);
            count++;
        }
    }
    // 重置visit数组，以便下次使用
    fill(g.visit.begin(), g.visit.end(), false);

    return count; // 返回连通块的数量
}

int base() {//基准法
    int block = Find_Block_num();//初始连通块数量
    int bridge = 0;//记录桥的数量
    for (int i = 0; i < g.V; i++) {//无向图只需遍历上三角
        for (int j = i+1; j < g.V; j++) {
            if (g.adjMatrix[i][j] ==1) {//如果有边
                g.adjMatrix[i][j] = g.adjMatrix[j][i] = 0;//去掉此边
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

    // 第一次遍历，建立生成树并合并集合
    for (int v = 0; v < g.V; v++) {
        for (int w = v + 1; w < g.V; w++) {
            if (g.adjMatrix[v][w] == 1) {
                g.uf.unionSet(v, w);
            }
        }
    }

    int block = 0;// 初始连通块数量
    for (int i = 0; i < g.V; ++i) {
        if (g.uf.find(i) == i) {
            block++;
        }
    }

    // 第二次遍历，检查每条边是否是桥
    for (int v = 0; v < g.V; ++v) {
        for (int w = v + 1; w < g.V; ++w) {
            if (g.adjMatrix[v][w] == 1) {
                // 删除边(v, w)
                g.adjMatrix[v][w] = g.adjMatrix[w][v] = 0;

                // 重新初始化并查集
                g.uf.init(g.V);
                for (int u = 0; u < g.V; ++u) {
                    for (int z = u + 1; z < g.V; ++z) {
                        if (g.adjMatrix[u][z] == 1) {
                            g.uf.unionSet(u, z);
                        }
                    }
                }

               
                int tmp_block = 0; //删除边后的连通块数量
                for (int i = 0; i < g.V; ++i) {
                    if (g.uf.find(i) == i) {
                        tmp_block++;
                    }
                }

                // 如果删除边后的连通块数量比原来多，那么边(v, w)是桥
                if (tmp_block > block) {
                    bridges.push_back(make_pair(v, w));
                }

                // 恢复边(v, w)
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
    cout << "输入1为测试图 输入2为随机图" << endl;
    int mode;
    cin >> mode;
    if (mode == 1) {
        freopen("MediumDG.txt", "r", stdin);
        cin >> g.V >> g.E;
        cout << "点数：" << g.V << " 边数：" << g.E << endl;
        g.Resize();
        g.init();
    }
    else if (mode == 2) {
        random_device rd;//用于生成随机数
        mt19937 gen(rd());//均匀分布，数据随机性较高
        uniform_int_distribution<>distrib(1, 100);
        g.V = 200;
        g.E =40000;
        cout << "点数：" << g.V << " 边数：" << g.E << endl;
        g.Resize();
        g.init_random();
    }
    cout << "开始寻找..." << endl;

    // 找到所有的桥
    int ans;
    clock_t start_time, end_time;//记录时间
    start_time = clock();
    ans=base();
    end_time = clock();
    cout << "基准法用时：" << fixed << setprecision(5) << (double)end_time - start_time << "ms" << endl;

    start_time = clock();
    ans = Uf();
    end_time = clock();
    cout << "并查集法用时：" << fixed << setprecision(5) << (double)end_time - start_time << "ms" << endl;
    
    cout << "桥的数量：" << ans << endl;
    return 0;
}
