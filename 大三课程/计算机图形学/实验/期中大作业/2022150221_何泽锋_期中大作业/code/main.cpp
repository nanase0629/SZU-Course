/*
 *        Computer Graphics Course - Shenzhen University
 *    Mid-term Assignment - Tetris implementation sample code
 * ============================================================
 *
 * - 本代码仅仅是参考代码，具体要求请参考作业说明，按照顺序逐步完成。
 * - 关于配置OpenGL开发环境、编译运行，请参考第一周实验课程相关文档。
 *
 * - 已实现功能如下：
 * - 1) 绘制棋盘格和‘L’型方块
 * - 2) 键盘左/右/下键控制方块的移动，上键旋转方块
 * - 3) 绘制‘J’、‘Z’等形状的方块
 * - 4) 方块之间、方块与边界之间的碰撞检测
 * - 5) 棋盘格中每一行填充满之后自动消除
 * - 6) 随机生成方块并赋上不同的颜色
 * - 7) 方块的自动向下移动
 * - 8) 记分
 * - 9) 根据分数加快下落速度
 * - 10) 输出帮助信息
 * - 11) 两种游戏模式，分别是生存模式和倒计时模式
 * - 12）空格使方块立即下落
 * - 13）R重新开始游戏
 */


#include "Angel.h"
#include <iostream>
#include <cstdlib>
#include <iostream>
#include <string>
#include <random>
#include <chrono>
#include <thread>
#include<windows.h>
using namespace std;

std::random_device rd;  // 用于获取随机数种子
std::mt19937 gen(rd()); // 使用种子初始化Mersenne Twister生成器

int starttime;			// 控制方块向下移动时间
int rotation = 0;		// 控制当前窗口中的方块旋转
glm::vec2 tile[4];			// 表示当前窗口中的方块
bool gameover = false;	// 游戏结束控制变量
bool gamewin = false;	// 倒计时模式胜利标志
int xsize = 400;		// 窗口大小（尽量不要变动窗口大小！）
int ysize = 720;

int score = 0;          // 生成模式分数
int nowscore = 0;       // 生存模式当前分数
bool wait2restart = false; // 游戏结束时控制只输出一次语句的变量
int countdownTime = 120;   // 生产模式时长
auto startTime = std::chrono::high_resolution_clock::now(); // 记录游戏开始时间
auto printTime = startTime;// 控制生存模式每一秒打印一次剩余时间
int mode;               // 模式选择变量
int nowcolor;			// 当前生成方块的颜色
int nowblock;			// 当前生成的方块下标

// 单个网格大小
int tile_width = 33;
bool spacedrop = false;
// 网格布大小
const int board_width = 10;
const int board_height = 20;

// 网格三角面片的顶点数量
const int points_num = board_height * board_width * 6;

// 我们用画直线的方法绘制网格
// 包含竖线 board_width+1 条
// 包含横线 board_height+1 条
// 一条线2个顶点坐标
// 网格线的数量
const int board_line_num = (board_width + 1) + (board_height + 1);

int blocktype = 9;
// 一个二维数组表示所有可能出现的方块和方向。
glm::vec2 allRotationsLshape[28][4] =
{ {glm::vec2(0, 0), glm::vec2(-1,0), glm::vec2(1, 0), glm::vec2(-1,-1)},	//   "L"
 {glm::vec2(0, 1), glm::vec2(0, 0), glm::vec2(0,-1), glm::vec2(1, -1)},
 {glm::vec2(1, 1), glm::vec2(-1,0), glm::vec2(0, 0), glm::vec2(1,  0)},
 {glm::vec2(-1,1), glm::vec2(0, 1), glm::vec2(0, 0), glm::vec2(0, -1)},

 {glm::vec2(0, 0), glm::vec2(-1,0), glm::vec2(0, -1), glm::vec2(-1,-1)},  //   "O"
 {glm::vec2(0, 0), glm::vec2(-1,0), glm::vec2(0, -1), glm::vec2(-1,-1)},
 {glm::vec2(0, 0), glm::vec2(-1,0), glm::vec2(0, -1), glm::vec2(-1,-1)},
 {glm::vec2(0, 0), glm::vec2(-1,0), glm::vec2(0, -1), glm::vec2(-1,-1)},

 {glm::vec2(0, 0), glm::vec2(-1,0), glm::vec2(-2, 0), glm::vec2(1,0)},    //   "I"
 {glm::vec2(0, 0), glm::vec2(0,-1), glm::vec2(0, -2), glm::vec2(0,1)},
 {glm::vec2(0, 0), glm::vec2(-1,0), glm::vec2(-2, 0), glm::vec2(1,0)},
 {glm::vec2(0, 0), glm::vec2(0,-1), glm::vec2(0, -2), glm::vec2(0,1)},

 {glm::vec2(0, 0), glm::vec2(-1,-1), glm::vec2(1, 0), glm::vec2(0,-1)},   //   "S"
 {glm::vec2(0, 0), glm::vec2(0,1), glm::vec2(1, 0), glm::vec2(1,-1)},
 {glm::vec2(0, 0), glm::vec2(-1,-1), glm::vec2(1, 0), glm::vec2(0,-1)},
 {glm::vec2(0, 0), glm::vec2(0,1), glm::vec2(1, 0), glm::vec2(1,-1)},

 {glm::vec2(0, 0), glm::vec2(-1,0), glm::vec2(0, -1), glm::vec2(1,-1)},   //   "Z"
 {glm::vec2(0, 0), glm::vec2(0,-1), glm::vec2(1, 0), glm::vec2(1,1)},
 {glm::vec2(0, 0), glm::vec2(-1,0), glm::vec2(0, -1), glm::vec2(1,-1)},
 {glm::vec2(0, 0), glm::vec2(0,-1), glm::vec2(1, 0), glm::vec2(1,1)},

 {glm::vec2(0, 0), glm::vec2(-1,0), glm::vec2(1, 0), glm::vec2(1,-1)},   //   "J"
 {glm::vec2(0, 0), glm::vec2(0,-1), glm::vec2(0, 1), glm::vec2(1,1)},
 {glm::vec2(0, 0), glm::vec2(-1,0), glm::vec2(-1, 1), glm::vec2(1,0)},
 {glm::vec2(0, 0), glm::vec2(-1,-1), glm::vec2(0, -1), glm::vec2(0,1)},

 {glm::vec2(0, 0), glm::vec2(-1,0), glm::vec2(1, 0), glm::vec2(0,-1)},   //   "T"
 {glm::vec2(0, 0), glm::vec2(0,-1), glm::vec2(0, 1), glm::vec2(1,0)},
 {glm::vec2(0, 0), glm::vec2(-1,0), glm::vec2(1, 0), glm::vec2(0,1)},
 {glm::vec2(0, 0), glm::vec2(-1,0), glm::vec2(0, -1), glm::vec2(0,1)}
};


// 绘制窗口的颜色变量
glm::vec4 orange = glm::vec4(1.0, 0.5, 0.0, 1.0);
glm::vec4 red = glm::vec4(1.0, 0.0, 0.0, 1.0);
glm::vec4 green = glm::vec4(0.0, 1.0, 0.0, 1.0);
glm::vec4 blue = glm::vec4(0.0, 0.0, 1.0, 1.0);
glm::vec4 white = glm::vec4(1.0, 1.0, 1.0, 1.0);
glm::vec4 black = glm::vec4(0.0, 0.0, 0.0, 1.0);
glm::vec4 Colors[4] = { orange, red, blue, green };


// 当前方块的位置（以棋盘格的左下角为原点的坐标系）
glm::vec2 tilepos = glm::vec2(5, 19);

// 布尔数组表示棋盘格的某位置是否被方块填充，即board[x][y] = true表示(x,y)处格子被填充。
// （以棋盘格的左下角为原点的坐标系）
bool board[board_width][board_height];

// 当棋盘格某些位置被方块填充之后，记录这些位置上被填充的颜色
glm::vec4 board_colours[points_num];

GLuint locxsize;
GLuint locysize;

GLuint vao[3];
GLuint vbo[6];

void framebuffer_size_callback(GLFWwindow* window, int width, int height)
{
	glViewport(0, 0, width, height);
}

// 修改棋盘格在pos位置的颜色为colour，并且更新对应的VBO
void changecellcolour(glm::vec2 pos, glm::vec4 colour)
{
	// 每个格子是个正方形，包含两个三角形，总共6个定点，并在特定的位置赋上适当的颜色
	for (int i = 0; i < 6; i++)
		board_colours[(int)(6 * (board_width * pos.y + pos.x) + i)] = colour;

	glm::vec4 newcolours[6] = { colour, colour, colour, colour, colour, colour };

	glBindBuffer(GL_ARRAY_BUFFER, vbo[3]);

	// 计算偏移量，在适当的位置赋上颜色
	int offset = 6 * sizeof(glm::vec4) * (int)(board_width * pos.y + pos.x);
	glBufferSubData(GL_ARRAY_BUFFER, offset, sizeof(newcolours), newcolours);
	glBindBuffer(GL_ARRAY_BUFFER, 0);
}

// 当前方块移动或者旋转时，更新VBO
void updatetile()
{
	glBindBuffer(GL_ARRAY_BUFFER, vbo[4]);

	// 每个方块包含四个格子
	for (int i = 0; i < 4; i++)
	{
		// 计算格子的坐标值
		GLfloat x = tilepos.x + tile[i].x;
		GLfloat y = tilepos.y + tile[i].y;

		glm::vec4 p1 = glm::vec4(tile_width + (x * tile_width), tile_width + (y * tile_width), .4, 1);
		glm::vec4 p2 = glm::vec4(tile_width + (x * tile_width), tile_width * 2 + (y * tile_width), .4, 1);
		glm::vec4 p3 = glm::vec4(tile_width * 2 + (x * tile_width), tile_width + (y * tile_width), .4, 1);
		glm::vec4 p4 = glm::vec4(tile_width * 2 + (x * tile_width), tile_width * 2 + (y * tile_width), .4, 1);

		// 每个格子包含两个三角形，所以有6个顶点坐标
		glm::vec4 newpoints[6] = { p1, p2, p3, p2, p3, p4 };
		glBufferSubData(GL_ARRAY_BUFFER, i * 6 * sizeof(glm::vec4), 6 * sizeof(glm::vec4), newpoints);
	}
	glBindVertexArray(0);

}
// 设置当前方块为下一个即将出现的方块。在游戏开始的时候调用来创建一个初始的方块，
// 在游戏结束的时候判断，没有足够的空间来生成新的方块。

void newtile()
{
	// 将新方块放于棋盘格的最上行中间位置
	tilepos = glm::vec2(5, 19);
	std::uniform_int_distribution<> disBlockType(0, 6); // 生成 [0, 6] 范围内的方块随机数（共6种方块）
	std::uniform_int_distribution<> disRotation(0, 3);  // 生成 [0, 3] 范围内的角度随机数（共4个方向）
	std::uniform_int_distribution<> disColour(0, 3);    // 生成 [0, 3] 范围内的颜色随机数（共4种颜色）

	// 使用生成器生成随机数
	blocktype = disBlockType(gen);
	rotation = disRotation(gen);

	for (int i = 0; i < 4; i++)
	{
		nowblock = blocktype * 4;
		//cout << "初始： " << nowblock + rotation << endl;
		tile[i] = allRotationsLshape[nowblock + rotation][i];
	}

	updatetile();

	// 给新方块赋上颜色
	glm::vec4 newcolours[24];
	nowcolor = disColour(gen);//随机生成当前方块颜色
	for (int i = 0; i < 24; i++) {
		newcolours[i] = Colors[nowcolor];
	}

	glBindBuffer(GL_ARRAY_BUFFER, vbo[5]);
	glBufferSubData(GL_ARRAY_BUFFER, 0, sizeof(newcolours), newcolours);
	glBindBuffer(GL_ARRAY_BUFFER, 0);

	glBindVertexArray(0);
}

// 游戏和OpenGL初始化
void init()
{
	// 初始化棋盘格，这里用画直线的方法绘制网格
	// 包含竖线 board_width+1 条
	// 包含横线 board_height+1 条
	// 一条线2个顶点坐标，并且每个顶点一个颜色值

	glm::vec4 gridpoints[board_line_num * 2];
	glm::vec4 gridcolours[board_line_num * 2];

	// 绘制网格线
	// 纵向线
	for (int i = 0; i < (board_width + 1); i++)
	{
		gridpoints[2 * i] = glm::vec4((tile_width + (tile_width * i)), tile_width, 0, 1);
		gridpoints[2 * i + 1] = glm::vec4((tile_width + (tile_width * i)), (board_height + 1) * tile_width, 0, 1);
	}

	// 水平线
	for (int i = 0; i < (board_height + 1); i++)
	{
		gridpoints[2 * (board_width + 1) + 2 * i] = glm::vec4(tile_width, (tile_width + (tile_width * i)), 0, 1);
		gridpoints[2 * (board_width + 1) + 2 * i + 1] = glm::vec4((board_width + 1) * tile_width, (tile_width + (tile_width * i)), 0, 1);
	}

	// 将所有线赋成白色
	for (int i = 0; i < (board_line_num * 2); i++)
		gridcolours[i] = white;

	// 初始化棋盘格，并将没有被填充的格子设置成黑色
	glm::vec4 boardpoints[points_num];
	for (int i = 0; i < points_num; i++)
		board_colours[i] = black;

	// 对每个格子，初始化6个顶点，表示两个三角形，绘制一个正方形格子
	for (int i = 0; i < board_height; i++)
		for (int j = 0; j < board_width; j++)
		{
			glm::vec4 p1 = glm::vec4(tile_width + (j * tile_width), tile_width + (i * tile_width), .5, 1);
			glm::vec4 p2 = glm::vec4(tile_width + (j * tile_width), tile_width * 2 + (i * tile_width), .5, 1);
			glm::vec4 p3 = glm::vec4(tile_width * 2 + (j * tile_width), tile_width + (i * tile_width), .5, 1);
			glm::vec4 p4 = glm::vec4(tile_width * 2 + (j * tile_width), tile_width * 2 + (i * tile_width), .5, 1);
			boardpoints[6 * (board_width * i + j) + 0] = p1;
			boardpoints[6 * (board_width * i + j) + 1] = p2;
			boardpoints[6 * (board_width * i + j) + 2] = p3;
			boardpoints[6 * (board_width * i + j) + 3] = p2;
			boardpoints[6 * (board_width * i + j) + 4] = p3;
			boardpoints[6 * (board_width * i + j) + 5] = p4;
		}

	// 将棋盘格所有位置的填充与否都设置为false（没有被填充）
	for (int i = 0; i < board_width; i++)
		for (int j = 0; j < board_height; j++)
			board[i][j] = false;

	// 载入着色器
	std::string vshader, fshader;
	vshader = "shaders/vshader.glsl";
	fshader = "shaders/fshader.glsl";
	GLuint program = InitShader(vshader.c_str(), fshader.c_str());
	glUseProgram(program);

	locxsize = glGetUniformLocation(program, "xsize");
	locysize = glGetUniformLocation(program, "ysize");

	GLuint vPosition = glGetAttribLocation(program, "vPosition");
	GLuint vColor = glGetAttribLocation(program, "vColor");


	glGenVertexArrays(3, &vao[0]);
	glBindVertexArray(vao[0]);		// 棋盘格顶点

	glGenBuffers(2, vbo);

	// 棋盘格顶点位置
	glBindBuffer(GL_ARRAY_BUFFER, vbo[0]);
	glBufferData(GL_ARRAY_BUFFER, (board_line_num * 2) * sizeof(glm::vec4), gridpoints, GL_STATIC_DRAW);
	glVertexAttribPointer(vPosition, 4, GL_FLOAT, GL_FALSE, 0, 0);
	glEnableVertexAttribArray(vPosition);

	// 棋盘格顶点颜色
	glBindBuffer(GL_ARRAY_BUFFER, vbo[1]);
	glBufferData(GL_ARRAY_BUFFER, (board_line_num * 2) * sizeof(glm::vec4), gridcolours, GL_STATIC_DRAW);
	glVertexAttribPointer(vColor, 4, GL_FLOAT, GL_FALSE, 0, 0);
	glEnableVertexAttribArray(vColor);


	glBindVertexArray(vao[1]);		// 棋盘格每个格子

	glGenBuffers(2, &vbo[2]);

	// 棋盘格每个格子顶点位置
	glBindBuffer(GL_ARRAY_BUFFER, vbo[2]);
	glBufferData(GL_ARRAY_BUFFER, points_num * sizeof(glm::vec4), boardpoints, GL_STATIC_DRAW);
	glVertexAttribPointer(vPosition, 4, GL_FLOAT, GL_FALSE, 0, 0);
	glEnableVertexAttribArray(vPosition);

	// 棋盘格每个格子顶点颜色
	glBindBuffer(GL_ARRAY_BUFFER, vbo[3]);
	glBufferData(GL_ARRAY_BUFFER, points_num * sizeof(glm::vec4), board_colours, GL_DYNAMIC_DRAW);
	glVertexAttribPointer(vColor, 4, GL_FLOAT, GL_FALSE, 0, 0);
	glEnableVertexAttribArray(vColor);


	glBindVertexArray(vao[2]);		// 当前方块

	glGenBuffers(2, &vbo[4]);

	// 当前方块顶点位置
	glBindBuffer(GL_ARRAY_BUFFER, vbo[4]);
	glBufferData(GL_ARRAY_BUFFER, 24 * sizeof(glm::vec4), NULL, GL_DYNAMIC_DRAW);
	glVertexAttribPointer(vPosition, 4, GL_FLOAT, GL_FALSE, 0, 0);
	glEnableVertexAttribArray(vPosition);

	// 当前方块顶点颜色
	glBindBuffer(GL_ARRAY_BUFFER, vbo[5]);
	glBufferData(GL_ARRAY_BUFFER, 24 * sizeof(glm::vec4), NULL, GL_DYNAMIC_DRAW);
	glVertexAttribPointer(vColor, 4, GL_FLOAT, GL_FALSE, 0, 0);
	glEnableVertexAttribArray(vColor);


	glBindVertexArray(0);

	glClearColor(0, 0, 0, 0);

	// 游戏初始化
	newtile();
	// starttime = glutGet(GLUT_ELAPSED_TIME);
}

// 检查在cellpos位置的格子是否被填充或者是否在棋盘格的边界范围内
bool checkvalid(glm::vec2 cellpos)
{
	if ((cellpos.x >= 0) && (cellpos.x < board_width) && (cellpos.y >= 0) && (cellpos.y < board_height) && !board[(int)cellpos.x][(int)cellpos.y])
		return true;
	else
		return false;
}

// 在棋盘上有足够空间的情况下旋转当前方块
void rotate()
{
	// 计算得到下一个旋转方向
	int nextrotation = (rotation + 1) % 4;
	// 检查当前旋转之后的位置的有效性
	if (checkvalid((allRotationsLshape[nextrotation][0]) + tilepos)
		&& checkvalid((allRotationsLshape[nextrotation][1]) + tilepos)
		&& checkvalid((allRotationsLshape[nextrotation][2]) + tilepos)
		&& checkvalid((allRotationsLshape[nextrotation][3]) + tilepos))
	{
		// 更新旋转，将当前方块设置为旋转之后的方块
		rotation = nextrotation;
		for (int i = 0; i < 4; i++) {
			tile[i] = allRotationsLshape[nowblock + rotation][i];
			//cout << "旋转： " << nowblock  + rotation << endl;
		}
		updatetile();
	}
}


// 检查棋盘格在row行有没有被填充满
void checkfullrow(int row)
{
	//如果该行有没满直接结束
	for (int i = 0; i < board_width; i++) {
		if (!board[i][row])return;
	}
	if (mode == 1) {
		score += 1;
		cout << "当前分数：" << score << endl;
	}
	//消去该行，上方部分整体下移
	for (int i = row + 1; i < board_height; i++) {
		for (int j = 0; j < board_width; j++) {
			board[j][i - 1] = board[j][i];
			changecellcolour(glm::vec2(j, i - 1), board_colours[6 * (j + i * board_width)]);
		}
	}
	//最上方一行需要初始化
	for (int i = 0; i < board_width; i++) {
		board[i][board_height - 1] = false;
		changecellcolour(glm::vec2(i, board_height - 1), black);
	}
}

// 放置当前方块，并且更新棋盘格对应位置顶点的颜色VBO
bool gameOver = false;//游戏结束标志符
void settile()
{
	// 每个格子
	for (int i = 0; i < 4; i++)
	{
		// 获取格子在棋盘格上的坐标
		int x = (tile[i] + tilepos).x;
		int y = (tile[i] + tilepos).y;
		if (y >= 20) {
			gameOver = true; // 设置游戏结束标志
			cout << "GAME OVER" << endl;
			return; // 结束函数执行
		}
		// 将格子对应在棋盘格上的位置设置为填充
		board[x][y] = true;
		// 并将相应位置的颜色修改
		changecellcolour(glm::vec2(x, y), Colors[nowcolor]);
	}
	for (int i = 0; i < 4; i++) {
		int y = (tile[i] + tilepos).y;
		checkfullrow(y);
	}
	spacedrop = false;
}

// 给定位置(x,y)，移动方块。有效的移动值为(-1,0)，(1,0)，(0,-1)，分别对应于向
// 左，向下和向右移动。如果移动成功，返回值为true，反之为false
bool movetile(glm::vec2 direction)
{
	// 计算移动之后的方块的位置坐标
	glm::vec2 newtilepos[4];
	for (int i = 0; i < 4; i++)
		newtilepos[i] = tile[i] + tilepos + direction;

	// 检查移动之后的有效性
	if (checkvalid(newtilepos[0])
		&& checkvalid(newtilepos[1])
		&& checkvalid(newtilepos[2])
		&& checkvalid(newtilepos[3]))
	{
		// 有效：移动该方块
		tilepos.x = tilepos.x + direction.x;
		tilepos.y = tilepos.y + direction.y;

		updatetile();

		return true;
	}

	return false;
}

void help() {
	cout << "--------------------------------" << endl;
	cout << "键盘上键 旋转方向" << endl;
	cout << "键盘下降 立即向下移动一格" << endl;
	cout << "<- 向左移动" << endl;
	cout << "-> 向右移动" << endl;
	cout << "空格 立即下落" << endl;
	cout << "R 重新开始游戏" << endl;
	cout << "Q 退出游戏" << endl;
	cout << "--------------------------------" << endl;
}

// 重新启动游戏
void restart()
{
	score = 0;
	nowscore = 0;
	gameOver = false;
	gamewin = false;
	wait2restart = false; // 重置提示信息打印标志
	cout << endl;
	cout << "--游戏重新开始--" << endl;
	for (int i = 3; i > 0; i--) {
		cout << i << "... " << endl;
		this_thread::sleep_for(std::chrono::seconds(1)); // 等待1秒
	}
	startTime = std::chrono::high_resolution_clock::now();
	printTime = startTime;
	if (mode == 1)cout << "当前分数：" << score << endl;
	// 重置棋盘格
	for (int i = 0; i < board_width; i++)
		for (int j = 0; j < board_height; j++)
		{
			board[i][j] = false;
			changecellcolour(glm::vec2(i, j), black);
		}

	// 重置方块
	tilepos = glm::vec2(5, 19);
	std::uniform_int_distribution<> disBlockType(0, 6); // 生成 [0, 6] 范围内的随机数
	std::uniform_int_distribution<> disRotation(0, 3);  // 生成 [0, 3] 范围内的随机数
	std::uniform_int_distribution<> disColour(0, 3);  // 生成 [0, 3] 范围内的随机数

	// 使用生成器生成随机数
	blocktype = disBlockType(gen);
	rotation = disRotation(gen);

	for (int i = 0; i < 4; i++)
	{
		nowblock = blocktype * 4;
		//cout << "初始： " << nowblock + rotation << endl;
		tile[i] = allRotationsLshape[nowblock + rotation][i];
	}

	updatetile();

	// 给新方块赋上颜色
	glm::vec4 newcolours[24];
	nowcolor = disColour(gen);
	for (int i = 0; i < 24; i++)
		newcolours[i] = Colors[nowcolor];

	glBindBuffer(GL_ARRAY_BUFFER, vbo[5]);
	glBufferSubData(GL_ARRAY_BUFFER, 0, sizeof(newcolours), newcolours);
	glBindBuffer(GL_ARRAY_BUFFER, 0);

	glBindVertexArray(0);
}

// 游戏渲染部分
void display()
{
	glClear(GL_COLOR_BUFFER_BIT);

	glUniform1i(locxsize, xsize);
	glUniform1i(locysize, ysize);

	glBindVertexArray(vao[1]);
	glDrawArrays(GL_TRIANGLES, 0, points_num); // 绘制棋盘格 (width * height * 2 个三角形)
	glBindVertexArray(vao[2]);
	glDrawArrays(GL_TRIANGLES, 0, 24);	 // 绘制当前方块 (8 个三角形)
	glBindVertexArray(vao[0]);
	glDrawArrays(GL_LINES, 0, board_line_num * 2);		 // 绘制棋盘格的线

}

// 在窗口被拉伸的时候，控制棋盘格的大小，使之保持固定的比例。
void reshape(GLsizei w, GLsizei h)
{
	xsize = w;
	ysize = h;
	glViewport(0, 0, w, h);
}

chrono::time_point<chrono::steady_clock> lastAutoDownTime;
void Autodown(int time) {
	// 获取当前时间
	auto now = chrono::steady_clock::now();
	// 计算自上次自动下落以来的时间差
	auto duration = chrono::duration_cast<chrono::milliseconds>(now - lastAutoDownTime).count();

	// 如果时间间隔已经超过AUTO_DOWN_INTERVAL，则尝试向下移动方块
	int tmp_time = (!spacedrop) ? time : 50;
	if (duration >= tmp_time) {
		// 更新上次自动下落的时间
		lastAutoDownTime = now;

		// 如果方块可以向下移动，则移动它
		if (!movetile(glm::vec2(0, -1)))
		{
			settile();
			newtile();
		}
	}
}


// 键盘响应事件中的特殊按键响应
void key_callback(GLFWwindow* window, int key, int scancode, int action, int mode)
{
	if (!gameover)
	{
		switch (key)
		{
			// 控制方块的移动方向，更改形态
		case GLFW_KEY_UP:	// 向上按键旋转方块
			if (action == GLFW_PRESS || action == GLFW_REPEAT)
			{
				rotate();
				break;
			}
			else
			{
				break;
			}
		case GLFW_KEY_DOWN: // 向下按键移动方块
			if (action == GLFW_PRESS || action == GLFW_REPEAT) {
				if (!movetile(glm::vec2(0, -1)))
				{
					settile();
					newtile();
					break;
				}
				else
				{
					break;
				}
			}
		case GLFW_KEY_LEFT:  // 向左按键移动方块
			if (action == GLFW_PRESS || action == GLFW_REPEAT) {
				movetile(glm::vec2(-1, 0));
				break;
			}
			else
			{
				break;
			}
		case GLFW_KEY_RIGHT: // 向右按键移动方块
			if (action == GLFW_PRESS || action == GLFW_REPEAT) {
				movetile(glm::vec2(1, 0));
				break;
			}
			else
			{
				break;
			}
		case GLFW_KEY_SPACE:
			if (action == GLFW_PRESS || action == GLFW_REPEAT) {
				spacedrop = true;
				break;
			}
			// 游戏设置。
		case GLFW_KEY_ESCAPE:
			if (action == GLFW_PRESS) {
				exit(EXIT_SUCCESS);
				break;
			}
			else
			{
				break;
			}
		case GLFW_KEY_Q:
			if (action == GLFW_PRESS) {
				exit(EXIT_SUCCESS);
				break;
			}
			else
			{
				break;
			}

		case GLFW_KEY_R:
			if (action == GLFW_PRESS) {
				restart();
				break;
			}
			else
			{
				break;
			}
		}
	}
}


int main(int argc, char** argv)
{
	cout << "请选择游戏模式（请输入数字）" << endl;
	cout << "1.生存模式" << endl;
	cout << "2.倒计时模式" << endl;

	cin >> mode;
	while (mode != 1 && mode != 2) {
		cout << "请重新选择模式" << endl;
		cin >> mode;
	}
	cout << endl;

	cout << "当前模式--";
	if (mode == 1)cout << "生存模式" << endl;
	else cout << "倒计时模式" << endl;
	for (int i = 3; i > 0; i--) {
		cout << i << "... " << endl;
		this_thread::sleep_for(std::chrono::seconds(1)); // 等待1秒
	}

	cout << "--游戏开始--" << endl;
	help();

	glfwInit();
	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

	#ifdef __APPLE__
		glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
	#endif

	// 创建窗口。
	GLFWwindow* window = glfwCreateWindow(500, 900, u8"2022150221_何泽锋_期中大作业", NULL, NULL);
	if (window == NULL)
	{
		std::cout << "Failed to create GLFW window!" << std::endl;
		glfwTerminate();
		return -1;
	}
	glfwMakeContextCurrent(window);
	glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);
	glfwSetKeyCallback(window, key_callback);

	if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress))
	{
		std::cout << "Failed to initialize GLAD" << std::endl;
		return -1;
	}


	init();


	if (mode == 1) {
		cout << "当前分数：" << score << endl;
		while (!glfwWindowShouldClose(window))
		{
			if (!gameOver) {
				display();
				glfwSwapBuffers(window);
				glfwPollEvents();
				if (score >= nowscore + 10) {
					nowscore = score;
					cout << "--速度加快--" << endl;
				}
				Autodown(max(100, 500 - nowscore * 10));//动态调整游戏难度，随分数增加而加快
			}
			else {
				if (!wait2restart) {
					cout << "游戏结束，请按R重新开始游戏" << endl;
					wait2restart = true;
				}

				glfwSwapBuffers(window); // 确保在游戏结束时也交换缓冲区
				glfwPollEvents(); // 确保在游戏结束时也处理事件
			}
		}
	}
	else if (mode == 2) {
		startTime = std::chrono::high_resolution_clock::now();
		auto printTime = startTime;
		auto oneSecond = std::chrono::seconds(1); // 定义一个时长为1秒的时长对象

		while (!glfwWindowShouldClose(window))
		{
			if (!gameOver && !gamewin) {
				auto currentTime = std::chrono::high_resolution_clock::now(); // 获取当前时间
				auto duration = std::chrono::duration_cast<std::chrono::seconds>(currentTime - startTime).count(); // 计算游戏已进行的时间
				int remainingTime = countdownTime - duration; // 计算剩余时间
				if (remainingTime > 0) {
					// 输出剩余时间，每秒更新一次
					auto tmpTime = std::chrono::high_resolution_clock::now();
					if (printTime + oneSecond < tmpTime) {
						printTime = tmpTime;
						cout << "剩余时间: " << remainingTime << " 秒" << endl;
					}

					// 根据剩余时间调整自动下落速度，时间越少，速度越快
					Autodown(max(100, 500 - ((int)duration) * 4));
				}
				else {
					gamewin = true; // 如果时间耗尽，设置游戏结束标志
					cout << "Victory!" << endl;
				}

				display();
				glfwSwapBuffers(window);
				glfwPollEvents();
			}
			else {
				if (!wait2restart) {
					cout << "游戏结束，请按R重新开始游戏" << endl;
					wait2restart = true;
				}

				glfwSwapBuffers(window); // 确保在游戏结束时也交换缓冲区
				glfwPollEvents(); // 确保在游戏结束时也处理事件
			}
		}
	}

	glfwTerminate();
	return 0;
}
