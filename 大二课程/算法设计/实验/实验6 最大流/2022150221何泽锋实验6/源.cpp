#include<cstdio>
#include<cstring>
#include<vector>
#include<queue>
#include<string>
#include<iostream>
#include<algorithm>
#include<Windows.h>
using namespace std;

const int INF = 1e9;
const int maxn = 2000;

struct P {
    int to, cap, rev,flow_EK;
    P(int t, int c, int r) : to(t), cap(c), rev(r){}
};
vector<P> G[maxn];
string name[maxn];//队伍名称
int n, m;//队伍数量、边数
int s, t;//源点、汇点
int w[maxn],l[maxn],re[maxn];//胜利场数、失败场数、剩余场数
int now[maxn][maxn];//两个队伍需要比赛的场数、
int lv[maxn];//图中节点层次
int it[maxn];//当前弧优化记录数组
bool visited[maxn] = { false }; // 用于记录当前已经访问过的边的索引
int cap_EK[maxn][maxn];
int flow_EK[maxn];
int pre[maxn];                 //标记在这条路径上当前节点的前驱,同时标记该节点是否在队列中

void add(int from, int to, int cap) {
    G[from].push_back(P(to, cap, G[to].size()));
    G[to].push_back(P(from, 0, G[from].size() - 1));
}

inline bool bfs() {
    memset(lv, -1, sizeof(lv));
    lv[s] = 0;//初始化源点的层次为0
    queue<int> q; q.push(s);
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int i = 0; i < G[u].size(); i++) {
            P e = G[u][i];
            if (lv[e.to] != -1 || !e.cap) continue;//如果边e的终点已经在层次图中，或者边的容量为0，则跳过这条边。
            lv[e.to] = lv[u] + 1;//否则将边放入队列，并将层次+1
            q.push(e.to);
            if (lv[t] != -1)return true;//找到汇点直接跳出。
        }
    }
    return lv[t] != -1;//存在路径到汇点那么汇点层次一定不为-1
}

inline int dfs_dinic(int u, int f) {
    if (u == t) return f;//到达汇点则返回当前的流量
    for (int &i = it[u]/*0*/; i < G[u].size(); i++) {
        P e = G[u][i];//取边
        if (lv[e.to] <= lv[u] || !e.cap) continue; //如果边e的终点已经在层次图中，或者边的容量为0，则跳过这条边。
        int c = dfs_dinic(e.to, min(f, e.cap));//从边e的终点开始，尝试增加流量。
        if (!c) continue; //如果没有增加流量，则跳过这条边。
        G[u][i].cap -= c; //减少边e的容量
        G[e.to][e.rev].cap += c;//增加边e的反向边的容量
        return c;//返回增加的流量
    }
    //it[u] = G[u].size(); // 重置当前弧为最后一个边
    return 0;
}

int dfs_FF(int u, int f) {
    if (u == t) return f; // 到达汇点则返回当前的流量
    visited[u] = true;
    for (int i = 0; i < G[u].size(); i++) {
        P& e = G[u][i]; // 取边
        if (!e.cap || visited[e.to]) continue; // 如果边e的终点已经在层次图中，或者边的容量为0，则跳过这条边。
        int c = dfs_FF(e.to, min(f, e.cap)); // 从边e的终点开始，尝试增加流量。
        if (!c) continue; // 如果没有增加流量，则跳过这条边。
        G[u][i].cap -= c; // 减少边e的容量
        G[e.to][e.rev].cap += c; // 增加边e的反向边的容量
        return c; // 返回增加的流量
    }
    return 0; // 如果没有找到可以增加流量的边，则返回0
}


inline int dinic() {
    int f = 0, fl;//分别用于存储当前的最大流和当前迭代中增加的流量。
    while (bfs()) {
        memset(it, 0, sizeof(it));
        while ((fl = dfs_dinic(s, INF))) f += fl;
    }
    return f;
}


inline int FF() {
    int f = 0, fl;//分别用于存储当前的最大流和当前迭代中增加的流量。
    memset(visited, 0, sizeof(visited));
    while ((fl = dfs_FF(s, INF))){
        f += fl;
        memset(visited, 0, sizeof(visited));
    }
    return f;
}
queue<int> eq;
int BFS(){
    while (!eq.empty())eq.pop();//队列清空
    for (int i = 0; i <= t; i++) pre[i] = -1;
    pre[s] = 0;
    flow_EK[s] = INF;
    eq.push(s);
    while (!eq.empty())
    {
        int index = eq.front();
        eq.pop();
        if (index == t)break; //找到了增广路径
        for (int i = 0; i <= t; i++)
        {
            if (i != s && cap_EK[index][i] > 0 && pre[i] == -1) {
                pre[i] = index; //记录前驱
                flow_EK[i] = min(cap_EK[index][i], flow_EK[index]);   
                eq.push(i);
                if (i == t)return flow_EK[t];
            }
        }
    }
    if (pre[t] == -1)      //残留图中不再存在增广路径
        return -1;
    else return flow_EK[t];
}

inline int EK(){
    int fl = 0;
    int f = 0;
    while ((fl = BFS()) != -1) {
        int k = t;          //利用前驱寻找路径
        while (k != s){
            int last = pre[k];
            cap_EK[last][k] -= fl; //改变正向边的容量
            cap_EK[k][last] += fl; //改变反向边的容量
            k = last;
        }
        f += fl;
    }
    return f;
}



inline bool win_dinic(int id, int tal) {
    int st = 1, sum = 0;
    for (int i = 0; i < maxn; i++)
        G[i].clear();//将图清空
    for (int i = 1; i <= n; i++) {//创图
        if (i == id) continue;
        for (int j = i + 1; j <= n; j++) {
            if (!now[i][j] || j == id) continue;//这两队没比赛或这场比赛涉及了要判断胜利的队伍（默认要判断的队伍能胜全胜，因此不需要将有关的边导入图）
            sum += now[i][j];//除去要判断的队伍以外的所有场数
            add(s, st, now[i][j]);
            add(st, i + m, now[i][j]);
            add(st, j + m, now[i][j]);
            st++;

        }
        if (w[i] > tal) return false;//平凡淘汰
        add(i + m, t, tal - w[i]);
    }
   int maxf = dinic();//最终流量
    //int maxf = FF();
    //cout << name[id] << " " << maxf <<" "<<sum << endl;
    if (maxf == sum) return true;
    return false;
}

inline bool win_FF(int id, int tal) {
    int st = 1, sum = 0;
    for (int i = 0; i < maxn; i++)
        G[i].clear();//将图清空
    for (int i = 1; i <= n; i++) {//创图
        if (i == id) continue;
        for (int j = i + 1; j <= n; j++) {
            if (!now[i][j] || j == id) continue;//这两队没比赛或这场比赛涉及了要判断胜利的队伍（默认要判断的队伍能胜全胜，因此不需要将有关的边导入图）
            sum += now[i][j];//除去要判断的队伍以外的所有场数
            add(s, st, now[i][j]);
            add(st, i + m, now[i][j]);
            add(st, j + m, now[i][j]);
            st++;
        }
        if (w[i] > tal) return false;//平凡淘汰
        add(i + m, t, tal - w[i]);
    }
    //int maxf = dinic();//最终流量
    int maxf = FF();
    //cout << name[id] << " " << maxf <<" "<<sum << endl;
    if (maxf == sum) return true;
    return false;
}

inline bool win_EK(int id, int tal) {
    int st = 1, sum = 0;
    for (int i = 1; i <= n; i++) {//创图
        if (i == id) continue;
        for (int j = i + 1; j <= n; j++) {
            if (!now[i][j] || j == id) continue;//这两队没比赛或这场比赛涉及了要判断胜利的队伍（默认要判断的队伍能胜全胜，因此不需要将有关的边导入图）
            sum += now[i][j];//除去要判断的队伍以外的所有场数
            cap_EK[s][st] = now[i][j];
            cap_EK[st][i + m] = now[i][j];
            cap_EK[st][j + m] = now[i][j];
            st++;
        }
        if (w[i] > tal) return false;//平凡淘汰
        cap_EK[i + m][t] = tal - w[i];
    }

    int maxf = EK();
    //cout << name[id] << " " << maxf <<" "<<sum << endl;
    if (maxf == sum) return true;
    return false;
}

int ans= 0;
long long  dis[maxn][maxn], vis[maxn], minn[maxn];
vector<int> e[maxn];
bool bfs1() {
    memset(vis, 0, sizeof(vis));
    queue<int> q;
    vis[s] = 1;
    q.push(s);
    minn[s] = 0x3ffffff;
    while (!q.empty()) {
        int x = q.front();
        q.pop();
        for (int i = 0; i < e[x].size(); i++) {
            int nx = e[x][i];
            if (dis[x][nx] > 0) {
                if (vis[nx]) continue;
                minn[nx] = min(minn[x], dis[x][nx]);	//找出最小容量 
                pre[nx] = x;	//记录前驱 
                q.push(nx);
                vis[nx] = 1;
                if (nx == t) return 1;
            }
        }
    }
    return 0;
}
void update() {	//更新剩余容量 
    int x = t;
    while (x != s) {
        int px = pre[x];
        dis[x][px] += minn[t];
        dis[px][x] -= minn[t];
        x = px;
    }
    ans += minn[t];
}
inline bool win_EK1(int id, int tal) {
    ans = 0;
    for (int i = 0; i < maxn; i++) {
        e[i].clear();
    }
    int st = 1, sum = 0;
    for (int i = 1; i <= n; i++) {//创图
        if (i == id) continue;
        for (int j = i + 1; j <= n; j++) {
            if (!now[i][j] || j == id) continue;//这两队没比赛或这场比赛涉及了要判断胜利的队伍（默认要判断的队伍能胜全胜，因此不需要将有关的边导入图）
            sum += now[i][j];//除去要判断的队伍以外的所有场数
            e[s].push_back(st);
            dis[s][st] = now[i][j];	
            e[st].push_back(s);	//反向边

            e[st].push_back(i+m);
            dis[st][i+m] = now[i][j];	
            e[i+m].push_back(st);	//反向边

            e[st].push_back(j+ m);
            dis[st][j + m] = now[i][j];	 
            e[j + m].push_back(st);	//反向边
            st++;
        }
        if (w[i] > tal) return false;//平凡淘汰
        e[i+m].push_back(t);
        dis[i+m][t] = tal - w[i];	
        e[t].push_back(i+m);	//反向边
    }
    while (bfs1()) update();
    //cout << name[id] << " " << maxf <<" "<<sum << endl;
    if (ans == sum) return true;
    return false;
}


int main() {
    clock_t start, end;
    freopen("teams54.txt", "r",stdin);
    cin >> n;
    int Max = 0;
    m = 0;
    for (int i = 1; i <= n; i++) {//队伍信息
        cin >> name[i] >> w[i] >> l[i] >> re[i];
        Max = max(Max, w[i]);
        for (int j = 1; j <= n; j++) {
            cin >> now[i][j];
            if (now[i][j] != 0)m++;
        }
    }
    m /= 2;//比赛节点的个数
    s = 0; t = n + m + 1;//源点和汇点下标
    start = clock();
    for (int i = 1; i <= n; i++) {
        int sum = w[i]+re[i];//最多获胜场数
        //if (win(i, sum)) {//可胜利队伍
        //    cout << name[i] << endl;
        //}
       
        if (!win_dinic(i, sum) && w[i] + re[i] >= Max) {//非平凡淘汰的队伍
            cout << name[i] << endl;
        }
    }
    end = clock();
    cout << "dinic运行时间：" << end - start <<" ms" << endl;

    for (int i = 1; i <= n; i++) {
        int sum = w[i] + re[i];//最多获胜场数
        //if (win(i, sum)) {//可胜利队伍
        //    cout << name[i] << endl;
        //}

        if (!win_FF(i, sum) && w[i] + re[i] >= Max) {//非平凡淘汰的队伍
            cout << name[i] << endl;
        }
    }
    end = clock();
    cout << "FF运行时间：" << end - start << " ms" << endl;


    int total = 0;
    for (int i = 1; i <= n; i++) {
        int sum = w[i] + re[i];//最多获胜场数
        //if (win(i, sum)) {//可胜利队伍
        //    cout << name[i] << endl;
        //}
       // memset(cap_EK, 0, sizeof(cap_EK));
        //memset(flow_EK, 0, sizeof(flow_EK));
        start = clock();
        if (!win_EK1(i, sum) && w[i] + re[i] >= Max) {//非平凡淘汰的队伍
            cout << name[i] << endl;
        }
        end = clock();
        total += end - start;
    }

    cout << "EK运行时间：" << total << " ms" << endl;
}