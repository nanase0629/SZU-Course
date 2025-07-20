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
    vector<vector<int>> map; // 邻接矩阵，表示图中的边
    bool visited[1000000] = { false }; // 标记节点是否被访问过
    vector<pair<int, int>> edges; // 存储所有边的列表
    vector<pair<int, int>> notTreeEdges; // 存储非树边的列表
    bool notLoopEdges[10000000] = { false }; // 标记边是否在环上
    int depth[10000000] = {0}; // 存储节点的深度
    int father[1000000]; // 存储节点的父节点，用于并查集
    int fa[1000000] ;
    int vertexNumber; // 节点的数量

    // 构造函数，初始化图的数据结构
    Map(int edgeNumber, int vertexNumber) : vertexNumber(vertexNumber) {
        //cout << vertexNumber << endl;
        map.resize(vertexNumber); // 初始化邻接矩阵

        for (int i = 0; i < vertexNumber; i++) {
            fa[i] = i;
            father[i] = i; // 初始化每个节点的父节点为自己
        }
    }

     //构建并查集树
     inline void buildTree(int& current ,int currentFather) {
        if (currentFather == -1)depth[current] = 1;
        else depth[current] = depth[currentFather]+1; // 设置当前节点的深度
        father[current] = currentFather; // 设置当前节点的父节点
        visited[current] = true; // 标记当前节点为已访问
        for (auto& son : map[current]) {
            if (!visited[son]) {
                ans++;
                notLoopEdges[son] = true; // 标记子节点为非环边
                buildTree(son, current); // 递归构建子树
            }
        }
     }


    // 创建并查集树
    void createTree() {
        for (int i = 0; i < vertexNumber; i++) {
            if (!visited[i]) {
                buildTree(i,-1); // 从未访问的节点开始构建
            }
        }
    }

    // 添加边到图中
    void addEdge(int head, int tail, bool init = false) {
        map[head].push_back(tail);
        map[tail].push_back(head);
        if (init) edges.emplace_back(head, tail);
    }

    // 查找非树边
    void findNotTreeEdge() {
        for (auto& edge : edges) {
            if (father[edge.first] != edge.second && father[edge.second] != edge.first) {
                notTreeEdges.emplace_back(edge.first, edge.second); // 添加非树边到列表
            }
        }
    }

    // 压缩路径
    inline int find(int x) {
        if (x == fa[x]||x==-1)return x;
        return fa[x] = find(fa[x]);
    }

    // 查找环边
    void LCA(int x,int y) {
        int u = x;
        int v = y;
        //cout << x << " " << y << endl;
        u = find(u);
        v = find(v);
        while (u!=v) {
            if (depth[u] > depth[v]) {//按照深度分类
                notLoopEdges[u] = false; // 标记边为环边
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

    // 查找桥
    void findBridge() {
        clock_t start, end;
        start = clock();
        createTree(); // 创建并查集树
        end = clock();
        cout << (end - start) << endl;
        start = clock();
        findNotTreeEdge(); // 查找非树边
        end = clock();
        cout << (end - start) << endl;
        start = clock();
        for (int i = 0; i < notTreeEdges.size(); i++) {
            pair<int, int>edge = notTreeEdges[i];
            LCA(edge.first,edge.second); // 查找环边
        }
        end = clock();
        cout << (end - start) << endl;
    }

    // 显示桥
    void showBridge() {
        int n = 0;
        for (int i = 0; i < vertexNumber; i++) {
            if (notLoopEdges[i]) {
                //n++; // 计数桥的数量
                cout << i << '-' << father[i] << endl; // 输出桥的信息
            }
        }
        cout << "桥的数量为：" << n << endl; // 输出桥的总数
    }
};

int main() {
    cout << "输入1为测试图 输入2为随机图" << endl;
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

        cout << "开始计算..." << endl;

        clock_t start_time, end_time;
        start_time = clock();
        map.findBridge();
        end_time = clock();
        map.showBridge();  
        cout << "优化寻找时间：" << end_time - start_time << "ms" << endl;
    }
    else {
        random_device rd;//用于生成随机数
        mt19937 gen(rd());//均匀分布，数据随机性较高
        uniform_int_distribution<>distrib(1, 100000);
        
        int vertexNumber= 5000;//点
        int edgeNumber= vertexNumber*vertexNumber;//边
        cout << vertexNumber << " " << edgeNumber << endl;

        Map map(edgeNumber, vertexNumber);
        int head,tail;
        for (int i = 0; i < edgeNumber; i++) {
            mt19937 gen2(rd());//均匀分布，数据随机性较高
            uniform_int_distribution<>distrib2(0, vertexNumber-1);
            head = distrib2(gen2);
            tail = distrib2(gen2);
            map.addEdge(head, tail, true);
        }

        cout << "开始计算..." << endl;

        clock_t start_time, end_time;
        start_time = clock();
        map.findBridge();
        end_time = clock();

        //map.showBridge();  
        cout << "优化寻找时间：" << end_time - start_time << "ms" << endl;

    }


}
