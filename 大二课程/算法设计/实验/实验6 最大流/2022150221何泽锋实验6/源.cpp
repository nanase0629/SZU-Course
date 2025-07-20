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
string name[maxn];//��������
int n, m;//��������������
int s, t;//Դ�㡢���
int w[maxn],l[maxn],re[maxn];//ʤ��������ʧ�ܳ�����ʣ�ೡ��
int now[maxn][maxn];//����������Ҫ�����ĳ�����
int lv[maxn];//ͼ�нڵ���
int it[maxn];//��ǰ���Ż���¼����
bool visited[maxn] = { false }; // ���ڼ�¼��ǰ�Ѿ����ʹ��ıߵ�����
int cap_EK[maxn][maxn];
int flow_EK[maxn];
int pre[maxn];                 //���������·���ϵ�ǰ�ڵ��ǰ��,ͬʱ��Ǹýڵ��Ƿ��ڶ�����

void add(int from, int to, int cap) {
    G[from].push_back(P(to, cap, G[to].size()));
    G[to].push_back(P(from, 0, G[from].size() - 1));
}

inline bool bfs() {
    memset(lv, -1, sizeof(lv));
    lv[s] = 0;//��ʼ��Դ��Ĳ��Ϊ0
    queue<int> q; q.push(s);
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int i = 0; i < G[u].size(); i++) {
            P e = G[u][i];
            if (lv[e.to] != -1 || !e.cap) continue;//�����e���յ��Ѿ��ڲ��ͼ�У����߱ߵ�����Ϊ0�������������ߡ�
            lv[e.to] = lv[u] + 1;//���򽫱߷�����У��������+1
            q.push(e.to);
            if (lv[t] != -1)return true;//�ҵ����ֱ��������
        }
    }
    return lv[t] != -1;//����·���������ô�����һ����Ϊ-1
}

inline int dfs_dinic(int u, int f) {
    if (u == t) return f;//�������򷵻ص�ǰ������
    for (int &i = it[u]/*0*/; i < G[u].size(); i++) {
        P e = G[u][i];//ȡ��
        if (lv[e.to] <= lv[u] || !e.cap) continue; //�����e���յ��Ѿ��ڲ��ͼ�У����߱ߵ�����Ϊ0�������������ߡ�
        int c = dfs_dinic(e.to, min(f, e.cap));//�ӱ�e���յ㿪ʼ����������������
        if (!c) continue; //���û�����������������������ߡ�
        G[u][i].cap -= c; //���ٱ�e������
        G[e.to][e.rev].cap += c;//���ӱ�e�ķ���ߵ�����
        return c;//�������ӵ�����
    }
    //it[u] = G[u].size(); // ���õ�ǰ��Ϊ���һ����
    return 0;
}

int dfs_FF(int u, int f) {
    if (u == t) return f; // �������򷵻ص�ǰ������
    visited[u] = true;
    for (int i = 0; i < G[u].size(); i++) {
        P& e = G[u][i]; // ȡ��
        if (!e.cap || visited[e.to]) continue; // �����e���յ��Ѿ��ڲ��ͼ�У����߱ߵ�����Ϊ0�������������ߡ�
        int c = dfs_FF(e.to, min(f, e.cap)); // �ӱ�e���յ㿪ʼ����������������
        if (!c) continue; // ���û�����������������������ߡ�
        G[u][i].cap -= c; // ���ٱ�e������
        G[e.to][e.rev].cap += c; // ���ӱ�e�ķ���ߵ�����
        return c; // �������ӵ�����
    }
    return 0; // ���û���ҵ��������������ıߣ��򷵻�0
}


inline int dinic() {
    int f = 0, fl;//�ֱ����ڴ洢��ǰ��������͵�ǰ���������ӵ�������
    while (bfs()) {
        memset(it, 0, sizeof(it));
        while ((fl = dfs_dinic(s, INF))) f += fl;
    }
    return f;
}


inline int FF() {
    int f = 0, fl;//�ֱ����ڴ洢��ǰ��������͵�ǰ���������ӵ�������
    memset(visited, 0, sizeof(visited));
    while ((fl = dfs_FF(s, INF))){
        f += fl;
        memset(visited, 0, sizeof(visited));
    }
    return f;
}
queue<int> eq;
int BFS(){
    while (!eq.empty())eq.pop();//�������
    for (int i = 0; i <= t; i++) pre[i] = -1;
    pre[s] = 0;
    flow_EK[s] = INF;
    eq.push(s);
    while (!eq.empty())
    {
        int index = eq.front();
        eq.pop();
        if (index == t)break; //�ҵ�������·��
        for (int i = 0; i <= t; i++)
        {
            if (i != s && cap_EK[index][i] > 0 && pre[i] == -1) {
                pre[i] = index; //��¼ǰ��
                flow_EK[i] = min(cap_EK[index][i], flow_EK[index]);   
                eq.push(i);
                if (i == t)return flow_EK[t];
            }
        }
    }
    if (pre[t] == -1)      //����ͼ�в��ٴ�������·��
        return -1;
    else return flow_EK[t];
}

inline int EK(){
    int fl = 0;
    int f = 0;
    while ((fl = BFS()) != -1) {
        int k = t;          //����ǰ��Ѱ��·��
        while (k != s){
            int last = pre[k];
            cap_EK[last][k] -= fl; //�ı�����ߵ�����
            cap_EK[k][last] += fl; //�ı䷴��ߵ�����
            k = last;
        }
        f += fl;
    }
    return f;
}



inline bool win_dinic(int id, int tal) {
    int st = 1, sum = 0;
    for (int i = 0; i < maxn; i++)
        G[i].clear();//��ͼ���
    for (int i = 1; i <= n; i++) {//��ͼ
        if (i == id) continue;
        for (int j = i + 1; j <= n; j++) {
            if (!now[i][j] || j == id) continue;//������û�������ⳡ�����漰��Ҫ�ж�ʤ���Ķ��飨Ĭ��Ҫ�жϵĶ�����ʤȫʤ����˲���Ҫ���йصıߵ���ͼ��
            sum += now[i][j];//��ȥҪ�жϵĶ�����������г���
            add(s, st, now[i][j]);
            add(st, i + m, now[i][j]);
            add(st, j + m, now[i][j]);
            st++;

        }
        if (w[i] > tal) return false;//ƽ����̭
        add(i + m, t, tal - w[i]);
    }
   int maxf = dinic();//��������
    //int maxf = FF();
    //cout << name[id] << " " << maxf <<" "<<sum << endl;
    if (maxf == sum) return true;
    return false;
}

inline bool win_FF(int id, int tal) {
    int st = 1, sum = 0;
    for (int i = 0; i < maxn; i++)
        G[i].clear();//��ͼ���
    for (int i = 1; i <= n; i++) {//��ͼ
        if (i == id) continue;
        for (int j = i + 1; j <= n; j++) {
            if (!now[i][j] || j == id) continue;//������û�������ⳡ�����漰��Ҫ�ж�ʤ���Ķ��飨Ĭ��Ҫ�жϵĶ�����ʤȫʤ����˲���Ҫ���йصıߵ���ͼ��
            sum += now[i][j];//��ȥҪ�жϵĶ�����������г���
            add(s, st, now[i][j]);
            add(st, i + m, now[i][j]);
            add(st, j + m, now[i][j]);
            st++;
        }
        if (w[i] > tal) return false;//ƽ����̭
        add(i + m, t, tal - w[i]);
    }
    //int maxf = dinic();//��������
    int maxf = FF();
    //cout << name[id] << " " << maxf <<" "<<sum << endl;
    if (maxf == sum) return true;
    return false;
}

inline bool win_EK(int id, int tal) {
    int st = 1, sum = 0;
    for (int i = 1; i <= n; i++) {//��ͼ
        if (i == id) continue;
        for (int j = i + 1; j <= n; j++) {
            if (!now[i][j] || j == id) continue;//������û�������ⳡ�����漰��Ҫ�ж�ʤ���Ķ��飨Ĭ��Ҫ�жϵĶ�����ʤȫʤ����˲���Ҫ���йصıߵ���ͼ��
            sum += now[i][j];//��ȥҪ�жϵĶ�����������г���
            cap_EK[s][st] = now[i][j];
            cap_EK[st][i + m] = now[i][j];
            cap_EK[st][j + m] = now[i][j];
            st++;
        }
        if (w[i] > tal) return false;//ƽ����̭
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
                minn[nx] = min(minn[x], dis[x][nx]);	//�ҳ���С���� 
                pre[nx] = x;	//��¼ǰ�� 
                q.push(nx);
                vis[nx] = 1;
                if (nx == t) return 1;
            }
        }
    }
    return 0;
}
void update() {	//����ʣ������ 
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
    for (int i = 1; i <= n; i++) {//��ͼ
        if (i == id) continue;
        for (int j = i + 1; j <= n; j++) {
            if (!now[i][j] || j == id) continue;//������û�������ⳡ�����漰��Ҫ�ж�ʤ���Ķ��飨Ĭ��Ҫ�жϵĶ�����ʤȫʤ����˲���Ҫ���йصıߵ���ͼ��
            sum += now[i][j];//��ȥҪ�жϵĶ�����������г���
            e[s].push_back(st);
            dis[s][st] = now[i][j];	
            e[st].push_back(s);	//�����

            e[st].push_back(i+m);
            dis[st][i+m] = now[i][j];	
            e[i+m].push_back(st);	//�����

            e[st].push_back(j+ m);
            dis[st][j + m] = now[i][j];	 
            e[j + m].push_back(st);	//�����
            st++;
        }
        if (w[i] > tal) return false;//ƽ����̭
        e[i+m].push_back(t);
        dis[i+m][t] = tal - w[i];	
        e[t].push_back(i+m);	//�����
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
    for (int i = 1; i <= n; i++) {//������Ϣ
        cin >> name[i] >> w[i] >> l[i] >> re[i];
        Max = max(Max, w[i]);
        for (int j = 1; j <= n; j++) {
            cin >> now[i][j];
            if (now[i][j] != 0)m++;
        }
    }
    m /= 2;//�����ڵ�ĸ���
    s = 0; t = n + m + 1;//Դ��ͻ���±�
    start = clock();
    for (int i = 1; i <= n; i++) {
        int sum = w[i]+re[i];//����ʤ����
        //if (win(i, sum)) {//��ʤ������
        //    cout << name[i] << endl;
        //}
       
        if (!win_dinic(i, sum) && w[i] + re[i] >= Max) {//��ƽ����̭�Ķ���
            cout << name[i] << endl;
        }
    }
    end = clock();
    cout << "dinic����ʱ�䣺" << end - start <<" ms" << endl;

    for (int i = 1; i <= n; i++) {
        int sum = w[i] + re[i];//����ʤ����
        //if (win(i, sum)) {//��ʤ������
        //    cout << name[i] << endl;
        //}

        if (!win_FF(i, sum) && w[i] + re[i] >= Max) {//��ƽ����̭�Ķ���
            cout << name[i] << endl;
        }
    }
    end = clock();
    cout << "FF����ʱ�䣺" << end - start << " ms" << endl;


    int total = 0;
    for (int i = 1; i <= n; i++) {
        int sum = w[i] + re[i];//����ʤ����
        //if (win(i, sum)) {//��ʤ������
        //    cout << name[i] << endl;
        //}
       // memset(cap_EK, 0, sizeof(cap_EK));
        //memset(flow_EK, 0, sizeof(flow_EK));
        start = clock();
        if (!win_EK1(i, sum) && w[i] + re[i] >= Max) {//��ƽ����̭�Ķ���
            cout << name[i] << endl;
        }
        end = clock();
        total += end - start;
    }

    cout << "EK����ʱ�䣺" << total << " ms" << endl;
}