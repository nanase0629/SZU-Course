#include<iostream>
#include<algorithm>
#include<random>
#include<stdlib.h>
#include<Windows.h>
using namespace std;

int BreakFloor;

int Force(int eggs, int floors) {
    if (floors == 0) return 0;// 如果没有楼层，不需要扔鸡蛋
    if (eggs == 1) return floors; // 如果只有一个鸡蛋，需要扔floors次
    
    int minDrops = INT_MAX;// 初始化最小次数为最大整数值
    for (int i = 1; i <= floors; i++) {
        // 扔鸡蛋，有两种情况：
        // 1. 鸡蛋碎了，需要在下面i-1层楼继续尝试，剩余鸡蛋数量减1
        // 2. 鸡蛋没碎，需要在上面floors-i层楼继续尝试
        int drops = 1 + max(Force(eggs - 1, i - 1), Force(eggs, floors - i));
        // 更新最小次数
        minDrops = min(minDrops, drops);
    }
    return minDrops;
}
int Dp(int eggs, int floors) {
    vector<vector<int>> dp(eggs + 1, vector<int>(floors + 1));

    for (int f = 1; f <= floors; f++) {
        dp[1][f] = f; // 只有一个鸡蛋时，需要扔floors次
    }
    for (int i = 0; i < eggs + 1; i++) {
        dp[i][0] = 0; // 楼层数为0时，掉落次数为0
        if (i >= 1) {
            dp[i][1] = 1; // 鸡蛋数量大于0时，楼层为1时掉落次数为1
        }
    }

    // 动态规划计算最少的试验次数
    for (int e = 2; e <= eggs; e++) {
        for (int f = 2; f <= floors; f++) {
            dp[e][f] = INT_MAX; // 初始化状态为最大值
            for (int k = 1; k <= f; k++) {
                // 计算两种情况的试验次数，取较小值
                int res = 1 + max(dp[e - 1][k - 1], dp[e][f - k]);
                dp[e][f] = min(res, dp[e][f]); // 更新状态
            }
        }
    }
    for (int i = 0; i < eggs + 1; i++) {
        for (int j = 0; j < floors + 1; j++) {
            cout << dp[i][j] << " ";
        }cout << endl;
    }
    //返回动态规划数组中的最终结果
    return dp[eggs][floors];
}
int Dp_space(int eggs, int floors) {
    vector<int> dp(floors + 1);
    vector<int>dpPrev(floors + 1);

    for (int f = 1; f <= floors; f++) {
        dp[f] = f; // 只有一个鸡蛋时，需要扔floors次
    }

    for (int e = 2; e <= eggs; e++) {
        // 用dpPrev保存上一行的状态
        dpPrev = dp;
        dp[1] = 1; // 楼层为1时掉落次数为1
        for (int f = 2; f <= floors; f++) {
            dp[f] = INT_MAX;
            for (int k = 1; k <= f; k++) {
                int res = 1 + max(dpPrev[k - 1], dp[f - k]);
                dp[f] = min(res, dp[f]);
            }
        }
    }
    // 返回动态规划数组中的最终结果
    return dp[floors];
}

int Dp_better1(int eggs, int floors) {
    vector<vector<int>> dp(eggs + 1, vector<int>(floors + 1));
    for (int i = 1; i <= floors; i++) {//只有一个鸡蛋时，需要扔floors次
        dp[1][i] = i;
    }
    for (int i = 1; i <= eggs; i++) {//只有一层楼，当有一个或多个鸡蛋时只需扔一次
        dp[i][1] = 1;
    }
    for (int i = 2; i <= floors; i++) {
        for (int j = 2; j <= eggs; j++) {
            int low = 1, high = i;
            while (low+1<high) {//超过两层差
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
int Dp_better2(vector<vector<int>>& dp, int eggs, int floors) {//逆向dp
 
    int ans = 0;//记录操作次数
    while (dp[eggs][ans] < floors) {//使用eggs个鸡蛋，操作ans次，可以确定的楼层小于当前最高楼层才继续找
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

int Dp_better2_space(int eggs, int floors) {//逆向dp优化空间
    vector<int> dp(eggs + 1);//dp下表是鸡蛋数，存的是通过该鸡蛋数能确定的层数
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
int Dp_better3(int eggs,int floors) {//决策单调性优化
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
    clock_t start_time, end_time;//分别用于记录排序开始时间和排序结束时间
    int mode;
    cout << "输入1为手动输入 输入2为随机生成" << endl;
    cin >> mode;
    vector<vector<int>> dp(3000+1, vector<int>(30000 + 1));

    if (mode == 1) {
        cout << "请输入鸡蛋数 楼层数：" << endl;
        cin >> e >> f;
        int Min=0;

        start_time = clock();
        //Min = Force(e, f);
        end_time = clock();
        cout << "暴力法用时：" << end_time - start_time << "ms" << endl;
        cout << "最小操作次数：" << Min << endl;

        start_time = clock();
        Min = Dp(e, f);
        end_time = clock();
        cout << "动态规划用时：" << end_time - start_time << "ms" << endl;
        cout << "最小操作次数：" << Min << endl;

        start_time = clock();
        Min = Dp_space(e, f);
        end_time = clock();
        cout << "优化空间的动态规划用时：" << end_time - start_time << "ms" << endl;
        cout << "最小操作次数：" << Min << endl;

        start_time = clock();
        Min = Dp_better1(e, f);
        end_time = clock();
        cout << "二分优化动态规划用时：" << end_time - start_time << "ms" << endl;
        cout << "最小操作次数：" << Min << endl;

        start_time = clock();
        Min = Dp_better2(dp,e, f);
        end_time = clock();
        cout << "数学优化动态规划用时：" << end_time - start_time << "ms" << endl;
        cout << "最小操作次数：" << Min << endl;

 
    }
    else if(mode==2) {      
        int total_time = 0;
        for (int i = 1; i <= 50; i++) {//循环20次，将得到的时间取平均值
            random_device rd;//用于生成随机数
            mt19937 gen(rd());//均匀分布，数据随机性较高
            uniform_int_distribution<>distrib(40000, 40000 );
            e = distrib(gen);
            f = distrib(gen);
            //cout << "当前鸡蛋数：" << e << endl;
            //cout << "当前楼层数：" << f << endl;

            start_time = clock();
            int Min = Dp_better3(e, f);
            end_time = clock();
            total_time += end_time - start_time;

            cout << "用时：" << end_time - start_time << "ms" << endl;
           //cout << "最小操作次数：" << Min << endl;
           // cout << "---------------" << endl;
        }
        cout << "平均用时："<<total_time/50<<"ms" << endl;
    }
}