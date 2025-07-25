﻿#include "TriMesh.h"
#include<iostream>
using namespace std;

// 一些基础颜色
const glm::vec3 basic_colors[8] = {
	glm::vec3(1.0, 0.843, 0.0),	// Bright Gold
	glm::vec3(0.0, 1.0, 0.5),		// Bright Turquoise
	glm::vec3(1.0, 0.0, 1.0),		// Bright Magenta
	glm::vec3(1.0, 0.271, 0.0),	// Bright Orange
	glm::vec3(0.0, 0.5, 1.0),		// Bright Blue
	glm::vec3(1.0, 0.549, 0.0),	// Bright Yellow
	glm::vec3(0.0, 1.0, 1.0),		// Bright Cyan
	glm::vec3(1.0, 0.0, 0.5),		// Bright Pink
};

// 立方体的各个点
const glm::vec3 cube_vertices[8] = {
	glm::vec3(-0.5, -0.5, -0.5),
	glm::vec3(0.5, -0.5, -0.5),
	glm::vec3(-0.5,  0.5, -0.5),
	glm::vec3(0.5,  0.5, -0.5),
	glm::vec3(-0.5, -0.5,  0.5),
	glm::vec3(0.5, -0.5,  0.5),
	glm::vec3(-0.5,  0.5,  0.5),
	glm::vec3(0.5,  0.5,  0.5)
};


TriMesh::TriMesh()
{
}

TriMesh::~TriMesh()
{
}

std::vector<glm::vec3> TriMesh::getVertexPositions()
{
	return vertex_positions;
}

std::vector<glm::vec3> TriMesh::getVertexColors()
{
	return vertex_colors;
}

std::vector<vec3i> TriMesh::getFaces()
{
	return faces;
}


std::vector<glm::vec3> TriMesh::getPoints()
{
	return points;
}

std::vector<glm::vec3> TriMesh::getColors()
{
	return colors;
}

void TriMesh::cleanData() {
	vertex_positions.clear();
	vertex_colors.clear();	
	
	faces.clear();

	points.clear();
	colors.clear();
}

void TriMesh::storeFacesPoints() {

	// 根据每个三角面片的顶点下标存储要传入GPU的数据
    for (auto &face : faces) {
        points.push_back(vertex_positions[face.x]);
        points.push_back(vertex_positions[face.y]);
        points.push_back(vertex_positions[face.z]);

        colors.push_back(vertex_colors[face.x]);
        colors.push_back(vertex_colors[face.y]);
        colors.push_back(vertex_colors[face.z]);

    }

}

// 立方体生成12个三角形的顶点索引
void TriMesh::generateCube() {
	// 创建顶点前要先把那些vector清空
	cleanData();

	// @TODO: Task1-修改此函数，存储立方体的各个面信息
    // vertex_positions和vertex_colors先保存每个顶点的数据
	for (int i = 0; i < 8; i++) {
		vertex_positions.push_back(cube_vertices[i]);
		vertex_colors.push_back(basic_colors[i]);
	}

	// faces再记录每个面片上顶点的下标
	faces.push_back(vec3i(0, 1, 2));
	faces.push_back(vec3i(2, 1, 3));
	faces.push_back(vec3i(4, 5, 6));
	faces.push_back(vec3i(6, 5, 7));
	faces.push_back(vec3i(0, 4, 1));
	faces.push_back(vec3i(1, 4, 5));
	faces.push_back(vec3i(2, 3, 6));
	faces.push_back(vec3i(6, 3, 7));
	faces.push_back(vec3i(0, 2, 4));
	faces.push_back(vec3i(4, 2, 6));
	faces.push_back(vec3i(1, 5, 3));
	faces.push_back(vec3i(3, 5, 7));
   
	storeFacesPoints();
}

glm::vec3 getColorForRegion(int regionIndex, int numRegions) {
	// 这里我们简单地使用HSV颜色空间来生成均匀的颜色
	float hue = (regionIndex % numRegions) / (float)numRegions;
	return glm::vec3(glm::cos(hue * 2 * glm::pi<float>()),
		glm::sin(hue * 2 * glm::pi<float>()),
		0.5f); // 生成HSV颜色，然后转换为RGB
}


void TriMesh::readOff(const std::string& filename)
{
    // fin打开文件读取文件信息
    if (filename.empty())
    {
        return;
    }
    std::ifstream fin;
    fin.open(filename);
    if (!fin)
    {
        printf("File on error\n");
        return;
    }
    else
    {
        printf("File open success\n");
		cleanData();
		int nVertices, nFaces, nEdges;

        // 读取OFF字符串
        std::string str;
        fin >> str;
        // 读取文件中顶点数、面片数、边数
        fin >> nVertices >> nFaces >> nEdges;
        // 根据顶点数，循环读取每个顶点坐标
		cout << nVertices << endl;
        for (int i = 0; i < nVertices; i++)
        {
			glm::vec3 tmp_node;
            fin >> tmp_node.x >> tmp_node.y >> tmp_node.z;
            vertex_positions.push_back(tmp_node);
			vertex_colors.push_back(tmp_node+glm::vec3(0.5,0.5,0.5));

        }
        // 根据面片数，循环读取每个面片信息，并用构建的vec3i结构体保存
        for (int i = 0; i < nFaces; i++)
        {
            int num, a, b, c;
            // num记录此面片由几个顶点构成，a、b、c为构成该面片顶点序号
            fin >> num >> a >> b >> c;
            faces.push_back(vec3i(a, b, c));
        }
    }
    fin.close();
    storeFacesPoints();
};