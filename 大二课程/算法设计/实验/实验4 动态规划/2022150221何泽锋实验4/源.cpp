#include<iostream>
#include<algorithm>
#include<random>
#include<stdlib.h>
#include<Windows.h>
using namespace std;

int BreakFloor;

int Force(int eggs, int floors) {
    if (floors == 0) return 0;// ���û��¥�㣬����Ҫ�Ӽ���
    if (eggs == 1) return floors; // ���ֻ��һ����������Ҫ��floors��
    
    int minDrops = INT_MAX;// ��ʼ����С����Ϊ�������ֵ
    for (int i = 1; i <= floors; i++) {
        // �Ӽ����������������
        // 1. �������ˣ���Ҫ������i-1��¥�������ԣ�ʣ�༦��������1
        // 2. ����û�飬��Ҫ������floors-i��¥��������
        int drops = 1 + max(Force(eggs - 1, i - 1), Force(eggs, floors - i));
        // ������С����
        minDrops = min(minDrops, drops);
    }
    return minDrops;
}
int Dp(int eggs, int floors) {
    vector<vector<int>> dp(eggs + 1, vector<int>(floors + 1));

    for (int f = 1; f <= floors; f++) {
        dp[1][f] = f; // ֻ��һ������ʱ����Ҫ��floors��
    }
    for (int i = 0; i < eggs + 1; i++) {
        dp[i][0] = 0; // ¥����Ϊ0ʱ���������Ϊ0
        if (i >= 1) {
            dp[i][1] = 1; // ������������0ʱ��¥��Ϊ1ʱ�������Ϊ1
        }
    }

    // ��̬�滮�������ٵ��������
    for (int e = 2; e <= eggs; e++) {
        for (int f = 2; f <= floors; f++) {
            dp[e][f] = INT_MAX; // ��ʼ��״̬Ϊ���ֵ
            for (int k = 1; k <= f; k++) {
                // ����������������������ȡ��Сֵ
                int res = 1 + max(dp[e - 1][k - 1], dp[e][f - k]);
                dp[e][f] = min(res, dp[e][f]); // ����״̬
            }
        }
    }
    for (int i = 0; i < eggs + 1; i++) {
        for (int j = 0; j < floors + 1; j++) {
            cout << dp[i][j] << " ";
        }cout << endl;
    }
    //���ض�̬�滮�����е����ս��
    return dp[eggs][floors];
}
int Dp_space(int eggs, int floors) {
    vector<int> dp(floors + 1);
    vector<int>dpPrev(floors + 1);

    for (int f = 1; f <= floors; f++) {
        dp[f] = f; // ֻ��һ������ʱ����Ҫ��floors��
    }

    for (int e = 2; e <= eggs; e++) {
        // ��dpPrev������һ�е�״̬
        dpPrev = dp;
        dp[1] = 1; // ¥��Ϊ1ʱ�������Ϊ1
        for (int f = 2; f <= floors; f++) {
            dp[f] = INT_MAX;
            for (int k = 1; k <= f; k++) {
                int res = 1 + max(dpPrev[k - 1], dp[f - k]);
                dp[f] = min(res, dp[f]);
            }
        }
    }
    // ���ض�̬�滮�����е����ս��
    return dp[floors];
}

int Dp_better1(int eggs, int floors) {
    vector<vector<int>> dp(eggs + 1, vector<int>(floors + 1));
    for (int i = 1; i <= floors; i++) {//ֻ��һ������ʱ����Ҫ��floors��
        dp[1][i] = i;
    }
    for (int i = 1; i <= eggs; i++) {//ֻ��һ��¥������һ����������ʱֻ����һ��
        dp[i][1] = 1;
    }
    for (int i = 2; i <= floors; i++) {
        for (int j = 2; j <= eggs; j++) {
            int low = 1, high = i;
            while (low+1<high) {//���������
                int mid = low + (high - low) / 2;
                if (dp[j - 1][mid - 1] <= dp[j][i-mid]) {
                    low = mid;
                }
                if (dp[j - 1][mid - 1] >= dp[j][i-mid]) {
                    high = mid;
                }
            }
            int count1 = max(dp[j - 1][low - 1], dp[j][i-low]);
            int count2 = max(dp[j - 1][high - 1], dp[j][i-high]);
            dp[j][i] = min(count1, count2) + 1;
        }
    }
    return dp[eggs][floors];
}
int Dp_better2(vector<vector<int>>& dp, int eggs, int floors) {//����dp
 
    int ans = 0;//��¼��������
    while (dp[eggs][ans] < floors) {//ʹ��eggs������������ans�Σ�����ȷ����¥��С�ڵ�ǰ���¥��ż�����
        ans++;
       
        for (int j = 1; j <= eggs; j++) {
            dp[j][ans] = dp[j - 1][ans - 1] + dp[j][ans -1] + 1;
        }
    }
    //for (int i = 0; i < eggs + 1; i++) {
    //    for (int j = 0; j < ans + 1; j++) {
    //        cout << dp[i][j] << " ";
    //    }cout << endl;
    //}
    return ans;
}

int Dp_better2_space(int eggs, int floors) {//����dp�Ż��ռ�
    vector<int> dp(eggs + 1);//dp�±��Ǽ������������ͨ���ü�������ȷ���Ĳ���
    int ans = 0;
    while(dp[eggs] < floors) {
        for (int i = eggs; i > 0; i--) {
            dp[i] = dp[i] + dp[i - 1] + 1;
        }
        ans++;
    }
    return ans;
}
vector<int>dp3(50000);
int Dp_better3(int eggs,int floors) {//���ߵ������Ż�
    for (int i = 0; i <= floors; ++i) {
        dp3[i] = i;
    }

    for (int j = 2; j <= eggs; ++j) {
        int dp2[50000];
        int x = 1;
        dp2[0] = 0;
        for (int m = 1; m <= floors; ++m) {
            while (x < m && max(dp3[x - 1], dp2[m - x]) >= max(dp3[x], dp2[m - x - 1])) {
                x++;
            }
            dp2[m] = 1 + max(dp3[x - 1], dp2[m - x]);
        }
        for (int m = 1; m <= floors; ++m) {
            dp3[m] = dp2[m];
        }
    }
    return dp3[floors];
}

signed main() {
    int f, e;
    clock_t start_time, end_time;//�ֱ����ڼ�¼����ʼʱ����������ʱ��
    int mode;
    cout << "����1Ϊ�ֶ����� ����2Ϊ�������" << endl;
    cin >> mode;
    vector<vector<int>> dp(3000+1, vector<int>(30000 + 1));

    if (mode == 1) {
        cout << "�����뼦���� ¥������" << endl;
        cin >> e >> f;
        int Min=0;

        start_time = clock();
        //Min = Force(e, f);
        end_time = clock();
        cout << "��������ʱ��" << end_time - start_time << "ms" << endl;
        cout << "��С����������" << Min << endl;

        start_time = clock();
        Min = Dp(e, f);
        end_time = clock();
        cout << "��̬�滮��ʱ��" << end_time - start_time << "ms" << endl;
        cout << "��С����������" << Min << endl;

        start_time = clock();
        Min = Dp_space(e, f);
        end_time = clock();
        cout << "�Ż��ռ�Ķ�̬�滮��ʱ��" << end_time - start_time << "ms" << endl;
        cout << "��С����������" << Min << endl;

        start_time = clock();
        Min = Dp_better1(e, f);
        end_time = clock();
        cout << "�����Ż���̬�滮��ʱ��" << end_time - start_time << "ms" << endl;
        cout << "��С����������" << Min << endl;

        start_time = clock();
        Min = Dp_better2(dp,e, f);
        end_time = clock();
        cout << "��ѧ�Ż���̬�滮��ʱ��" << end_time - start_time << "ms" << endl;
        cout << "��С����������" << Min << endl;

 
    }
    else if(mode==2) {      
        int total_time = 0;
        for (int i = 1; i <= 50; i++) {//ѭ��20�Σ����õ���ʱ��ȡƽ��ֵ
            random_device rd;//�������������
            mt19937 gen(rd());//���ȷֲ�����������Խϸ�
            uniform_int_distribution<>distrib(40000, 40000 );
            e = distrib(gen);
            f = distrib(gen);
            //cout << "��ǰ��������" << e << endl;
            //cout << "��ǰ¥������" << f << endl;

            start_time = clock();
            int Min = Dp_better3(e, f);
            end_time = clock();
            total_time += end_time - start_time;

            cout << "��ʱ��" << end_time - start_time << "ms" << endl;
           //cout << "��С����������" << Min << endl;
           // cout << "---------------" << endl;
        }
        cout << "ƽ����ʱ��"<<total_time/50<<"ms" << endl;
    }
}