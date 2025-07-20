#include<iostream>
#include<algorithm>
#include <fstream>
#include <vector>
#include <bitset>
using namespace std;


//置换矩阵-2022150221
int Origin[8][8] = { 58,50,42,34,26,18,10,2,
                     60,52,44,36,28,20,12,4,
                     62,54,46,38,30,22,14,6,
                     64,56,48,40,32,24,16,8,
                     57,49,41,33,25,17,9,1,
                     59,51,43,35,27,19,11,3,
                     61,53,45,37,29,21,13,5,
                     63,55,47,39,31,23,15,7 };

//逆置换矩阵-2022150221
int Inverse[8][8] = { 40,8,48,16,56,24,64,32,
                      39,7,47,15,55,23,63,31,
                      38,6,46,14,54,22,62,30,
                      37,5,45,13,53,21,61,29,
                      36,4,44,12,52,20,60,28,
                      35,3,43,11,51,19,59,27,
                      34,2,42,10,50,18,58,26,
                      33,1,41,9,49,17,57,25 };

//拓展E-2022150221
int Expend[8][6] = { 32,1,2,3,4,5,
                     4,5,6,7,8,9,
                     8,9,10,11,12,13,
                     12,13,14,15,16,17,
                     16,17,18,19,20,21,
                     20,21,22,23,24,25,
                     24,25,26,27,28,29,
                     28,29,30,31,32,1 };

//s box-2022150221
int s_box[8][4][16] = { {{14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7},{0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8},{4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0},{15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13}},
                        {{15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10},{3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5},{ 0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15},{ 13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9}},
                        {{10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8},{13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1},{13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7},{1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12}},
                        {{7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15},{13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9},{10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4},{3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14}},
                        {{2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9},{14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6},{4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14},{11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3}},
                        {{12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11},{10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8},{9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6},{4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13}},
                        {{4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1},{13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6},{1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2},{6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12}},
                        {{13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7},{1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2},{7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8},{2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11}} };
//p box-2022150221
int p_box[4][8] = { 16,7,20,21,29,12,28,17,
                    1,15,23,26,5,18,31,10,
                    2,8,24,14,32,27,3,9,
                    19,13,30,6,22,11,4,25 };

//循环左移-2022150221
int Move[16] = { 1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1 };

//置换PC1-2022150221
int PC1[8][7] = { 57,49,41,33,25,17,9,
                  1,58,50,42,34,26,18,
                  10,2,59,51,43,35,27,
                  19,11,3,60,52,44,36,
                  3,55,47,39,31,23,15,
                  7,62,54,46,38,30,22,
                  14,6,61,53,45,37,29,
                  21,13,5,28,20,12,4 };


//置换PC2-2022150221
int PC2[8][6] = { 14,17,11,24,1,5,
                  3,28,15,6,21,10,
                  23,19,12,4,26,8,
                  16,7,27,20,13,2,
                  41,52,31,37,47,55,
                  30,40,51,45,33,48,
                  44,49,39,56,34,53,
                  46,42,50,36,29,32 };

//存16轮子密钥-2022150221
string Secret_Keys1[20];
string Secret_Keys2[20];
string Secret_Keys3[20];


//64->56-2022150221
string secret_key_64to56(string s){
    string ss = "";
    for (int i = 0; i < 8; i++){
        for (int j = 0; j < 7; j++){
            ss += s[PC1[i][j] - 1];
        }
    }
    return ss;
}
//分块左移-2022150221
string secret_ket_move(string s,int move){
    string s1 = s.substr(0, 28);
    string s2 = s.substr(28, 28);
    string ss = s1.substr(move, 28 - move) + s1.substr(0, move) + s2.substr(move, 28 - move) + s2.substr(0, move);
    return ss;
}
//56->48-2022150221
string secret_key_56to48(string s)
{
    string ss = "";
    for (int i = 0; i < 8; i++){
        for (int j = 0; j < 6; j++){
            ss += s[PC2[i][j] - 1];
        }
    }
    return ss;
}


//生成子密钥-2022150221
void Generate_Key(string s, int move){
    //置换1，将64bit转为56bit
    s = secret_key_64to56(s);
    //cout << s << endl;
    //16轮左移和置换
    for (int i = 1; i <= 16; i++){
        s = secret_ket_move(s,Move[i-1]);
        if (move == 1)Secret_Keys1[i] = secret_key_56to48(s);
        else if (move == 2)Secret_Keys2[i] = secret_key_56to48(s);
        else if (move == 3)Secret_Keys3[i] = secret_key_56to48(s);
    }
}

//明文初始置换-2022150221
string Origin_text(string s){
    string ss = "";
    for (int i = 0; i < 8; i++){
        for (int j = 0; j < 8; j++){
            ss += s[Origin[i][j] - 1];
        }
    }
    return ss;
}
//异或操作-2022150221
string XOR(string s1, string s2){
    string ss = "";
    for (int i = 0; i < s1.length() && i < s2.length(); i++){
        ss += ((s1[i] - '0') ^ (s2[i] - '0')) + '0';
    }
    return ss;
}
//右半拓展-2022150221
string Expend_R(string s){
    string ss = "";
    for (int i = 0; i < 8; i++){
        for (int j = 0; j < 6; j++){
            ss += s[Expend[i][j] - 1];
        }
    }
    return ss;
}
//置换S-2022150221
string S_box(string s){
    string ss = "";
    int row, col;//行、列
    int id = 0;//s box索引
    for (int i = 0; i <= 42; i += 6, id++){
        row = (s[i] - '0') * 2 + (s[i + 5] - '0');//B1B6
        col = (s[i + 1] - '0') * 8 + (s[i + 2] - '0') * 4 + (s[i + 3] - '0') * 2 + (s[i + 4] - '0');//B2B3B4B5
        int x = s_box[id][row][col];
        string tmp;
        int y = 8;//四位二进制的最高位值
        for (int j = 1; j <= 4; j++){
            //判是否需要补0（输出要满足4位二进制数）
            if (x < y){
                tmp += "0";
                y /= 2;
            }
            else{
                tmp += "1";
                x = x % y;
                y /= 2;
            }
        }
        ss += tmp;
    }
    return ss;
}
//压缩P-2022150221
string P_box(string s){
    string ss = "";
    for (int i = 0; i < 4; i++){
        for (int j = 0; j < 8; j++){
            ss += (s[p_box[i][j] - 1]);
        }
    }
    return ss;
}

//F-2022150221
string F(string str1, string K){
    string expendR = Expend_R(str1);
    string ss = XOR(expendR, K);
    ss = S_box(ss);
    ss = P_box(ss);
    return ss;
}

//逆初始置换-2022150221
string Final_text(string s)
{
    string ss = "";
    for (int i = 0; i < 8; i++){
        for (int j = 0; j < 8; j++){
            ss += s[Inverse[i][j] - 1];
        }
    }
    return ss;
}
//加密-2022150221
string Encryption_text(string str1, int move){
    //明文初始置换 64->64
    str1 = Origin_text(str1);
    //数据分组
    string left = str1.substr(0, 32);
    string right = str1.substr(32, 32);

    string newleft;

    //16轮迭代
    for (int i = 1; i <= 16; i++){
        newleft = right;
        if (move == 1)right = XOR(left, F(right, Secret_Keys1[i]));
        else if (move == 2)right = XOR(left, F(right, Secret_Keys2[i]));
        else if (move == 3)right = XOR(left, F(right, Secret_Keys3[i]));
        left = newleft;
    }

    //合并数据，此处将最后的左右串进行了位置对换
    string ss = right + left;

    //结尾置换
    ss = Final_text(ss);
    return ss;
}
//解密-2022150221
string Decryption_text(string str1, int move){
    str1 = Origin_text(str1);
    string left = str1.substr(0, 32);
    string right = str1.substr(32, 32);
    string newleft;
    for (int i = 16; i >= 1; i--) {
        newleft = right;
        if (move == 1)right = XOR(left, F(right, Secret_Keys1[i]));
        else if (move == 2)right = XOR(left, F(right, Secret_Keys2[i]));
        else if (move == 3)right = XOR(left, F(right, Secret_Keys3[i]));
        left = newleft;
    }
    string ss = right + left;
    ss = Final_text(ss); 
    return ss;
}

// 3DES加密函数-2022150221
string TripleDES_Encryption(string s) {
    // 第一次加密
    s = Encryption_text(s,1);

    // 第一次解密
    s = Decryption_text(s,2);

    // 第二次加密
    s = Encryption_text(s,3);

    return s;
}

// 3DES解密函数-2022150221
string TripleDES_Decryption(string s) {

    // 使用第三个密钥解密
    s = Decryption_text(s,3); 

    // 使用第二个密钥加密
    s = Encryption_text(s,2);

    // 使用第一个密钥解密
    s = Decryption_text(s,1);
    return s;
}

//转二进制字符-2022150221
string stringToBinary(string s){
    string s1;
    string ss = "";
    for (int i = 0; i < s.length(); i++){
        int x;
        if (s[i] >= '0' && s[i] <= '9') {
            x = s[i] - '0';
        }
        else x = s[i] - 'A' + 10;
        s1 = "";
        int y = 8;
        for (int j = 1; j <= 4; j++){
            if (x < y){
                y /= 2;
                s1 += "0";
            }
            else{
                s1 += "1";
                x = x % y;
                y = y / 2;
            }
        }
        ss += s1;
    }
    return ss;
}

//转原字符-2022150221
string binaryToString(string str){
    string ss = "";
    char temp;
    for (int i = 0; i <= str.length() - 4; i = i + 4){
        int x = (str[i] - '0') * 8 + (str[i + 1] - '0') * 4 + (str[i + 2] - '0') * 2 + str[i + 3] - '0';
        if (x >= 10) {
            temp = x - 10 + 'A';
        }
        else temp = x + '0';
        ss += temp;
    }
    return ss;
}

int add_len = 0;
// 使用3DES加密文件-2022150221
void EncryptFile(const string& inputFilename,const string& outputFilename) {
    ifstream inputFile(inputFilename, ios::binary);//以二进制的形式读入文件
    ofstream outputFile(outputFilename, ios::binary);//以二进制形式输出

    //判断是否能打开
    if (!inputFile.is_open() || !outputFile.is_open()) {
        cerr << "Error opening file." << endl;
        return;
    }

    //将读入数据转为char
    vector<char> buffer((istreambuf_iterator<char>(inputFile)), (istreambuf_iterator<char>()));
    inputFile.close();

    string binaryData;
    for (char c : buffer) {
        for (int i = 7; i >= 0; i--) {
            char bit = ((c >> i) & 1) + '0';
            binaryData += bit;
        }
    }
    //cout << binaryData << endl;
    while (binaryData.length() % 64 != 0) {
        binaryData += '0'; // 添加填充位，这里使用'0'填充
        add_len++;
    }
    vector<string> encryptedBlocks;
    for (size_t i = 0; i <= binaryData.length()-64; i += 64) {
        //每次取64个'01'串进行加密
        string block = binaryData.substr(i, 64);
        string encryptedBlock = TripleDES_Encryption(block);
        for (size_t j = 0; j < encryptedBlock.length(); j += 8) {
            //将加密结果转为bit，每次取8位与输入时一致
            std::bitset<8> byte(encryptedBlock.substr(j, 8));
            //将取出的值转回char
            char encryptedChar = static_cast<char>(byte.to_ulong());
            outputFile << encryptedChar;
        }
    }
    outputFile.close();
}
//使用3DES解密-2022150221
void DecryptFile(const string& inputFilename,const string& outputFilename) {
    ifstream inputFile(inputFilename, ios::binary);//以二进制的形式读入文件
    ofstream outputFile(outputFilename, ios::binary);//以二进制形式输出

    //判断是否能打开
    if (!inputFile.is_open() || !outputFile.is_open()) {
        cerr << "Error opening file." << endl;
        return;
    }

    //将读入数据转为char
    vector<char> buffer((istreambuf_iterator<char>(inputFile)), (istreambuf_iterator<char>()));
    inputFile.close();

    string binaryData;
    for (char c : buffer) {
        for (int i = 7; i >= 0; i--) {
            char bit = ((c >> i) & 1) + '0';
            binaryData += bit;
        }
    }

    vector<string> decryptedBlocks;
    for (size_t i = 0; i <= binaryData.length() - 64; i += 64) {
        // 每次取64个'01'串进行加密
        string block = binaryData.substr(i, 64);
        string decryptedBlock = TripleDES_Decryption(block);
        //如果是最后一个串需要去掉补的'0'
        if (i + 64 == binaryData.length()) {
            decryptedBlock = decryptedBlock.substr(0, decryptedBlock.length() - add_len);
        }
        for (size_t j = 0; j < decryptedBlock.length(); j += 8) {
            // 将加密结果转为bit，每次取8位与输入时一致
            std::bitset<8> byte(decryptedBlock.substr(j, 8));
            //将取出的值转回char
            char decryptedBlock = static_cast<char>(byte.to_ulong());
            outputFile << decryptedBlock;
        }
    }
    outputFile.close();
}


int main() {
    // 明文
    //string text = "0123456789ABCDEF"; // 明文，16个16进制字符（64位）
    //cout << "明文输入：" << text << endl;

    //2022150221
    string key1 = "133457799BBCDFF1"; // 第一个密钥
    string key2 = "8765432187654321"; // 第二个密钥
    string key3 = "1234876543212348"; // 第三个密钥

    //string text_in = stringToBinary(text);
    string key1_in = stringToBinary(key1);
    string key2_in = stringToBinary(key2);
    string key3_in = stringToBinary(key3);

    Generate_Key(key1_in, 1);
    Generate_Key(key2_in, 2);
    Generate_Key(key3_in, 3);

    EncryptFile("2022150221何泽锋.mp3", "2022150221何泽锋加密mp3文件.txt");
    cout << "加密完成" << endl;
    DecryptFile("2022150221何泽锋加密mp3文件.txt", "2022150221何泽锋解密文件.mp3");
    cout << "解密完成" << endl;

    /*
    // 加密
    string C = TripleDES_Encryption(text_in);
    cout << "加密结果: " << binaryToString(C) << endl;

    // 解密
    string M = TripleDES_Decryption(C);
    M = binaryToString(M);
    cout << "解密结果: " << M << endl;
    */

}




