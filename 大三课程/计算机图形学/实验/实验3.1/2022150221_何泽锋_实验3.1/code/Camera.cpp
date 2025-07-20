#include "Camera.h"

Camera::Camera() { updateCamera(); };
Camera::~Camera() {};


glm::mat4 Camera::lookAt(const glm::vec4& eye, const glm::vec4& at, const glm::vec4& up)
{	
	// @TODO: Task1:请按照实验课内容补全相机观察矩阵的计算
	glm::mat4 c = glm::mat4(0.0f);
	glm::vec3 n = glm::normalize(eye - at);
	glm::vec3 u = glm::normalize(glm::cross((glm::vec3)up, (glm::vec3)n));
	glm::vec3 v = glm::normalize(glm::cross(n, u));

	//glm::mat4 viewMarix({ u.x,u.y,u.z,0 }, { v.x,v.y,v.z,0 }, { n.x,n.y,n.z,0 }, { 0,0,0,1 });
	//glm::mat4 T({ 1,0,0,-eye.x }, { 0,1,0,-eye.y }, { 0,0,1,-eye.z }, { 0,0,0,1 });
	
	glm::mat4 cc({ u.x,v.x,n.x,0 }, 
				 { u.y,v.y,n.y,0 }, 
				 { u.z,v.z,n.z,0 }, 
				 { -eye.x * u.x - eye.y * u.y - eye.z * u.z,-eye.x * v.x - eye.y * v.y - eye.z * v.z,-eye.x * n.x - eye.y * n.y - eye.z * n.z,1.0 });
	return cc;
}


glm::mat4 Camera::ortho(const GLfloat left, const GLfloat right,
	const GLfloat bottom, const GLfloat top,
	const GLfloat zNear, const GLfloat zFar)
{
	// @TODO: Task2:请按照实验课内容补全正交投影矩阵的计算
	glm::mat4 c = glm::mat4(0.0f);
	c[0][0] = 2.0 / (right - left);
	c[1][1] = 2.0 / (top - bottom);
	c[2][2] = 2.0 / (zNear - zFar);
	c[3][3] = 1.0;
	c[0][3] = -(right + left) / (right - left);
	c[1][3] = -(top + bottom) / (top - bottom);
	c[2][3] = -(zFar + zNear) / (zFar - zNear);
	return glm::transpose(c);
}


glm::mat4 Camera::perspective(const GLfloat fov, const GLfloat aspect,
	const GLfloat zNear, const GLfloat zFar)
{
	// @TODO: Task3:请按照实验课内容补全透视投影矩阵的计算
	glm::mat4 c = glm::mat4(0.0f);
	GLfloat top = zNear * tan(glm::radians(fov )/ 2.0);
	GLfloat right = top * aspect;
	c[0][0] = zNear / right;
	c[1][1] = zNear / top;
	c[2][2] = -(zFar + zNear) / (zFar - zNear);
	c[2][3] = -2.0 * zFar * zNear / (zFar - zNear);
	c[3][2] = -1.0;
	return glm::transpose(c);
}


glm::mat4 Camera::frustum(const GLfloat left, const GLfloat right,
	const GLfloat bottom, const GLfloat top,
	const GLfloat zNear, const GLfloat zFar)
{
	// 任意视锥体矩阵
	glm::mat4 c = glm::mat4(1.0f);
	c[0][0] = 2.0 * zNear / (right - left);
	c[0][2] = (right + left) / (right - left);
	c[1][1] = 2.0 * zNear / (top - bottom);
	c[1][2] = (top + bottom) / (top - bottom);
	c[2][2] = -(zFar + zNear) / (zFar - zNear);
	c[2][3] = -2.0 * zFar * zNear / (zFar - zNear);
	c[3][2] = -1.0;
	c[3][3] = 0.0;
	c = glm::transpose(c);
	return c;
}


void Camera::updateCamera()
{
	// @TODO: Task1 设置相机位置和方向
	float eyex = 0;			// 根据rotateAngle和upAngle设置x
	float eyey = 0;			// 根据upAngle设置y
	float eyez = radius;	// 根据rotateAngle和upAngle设置z
	
	eye = glm::vec4(eyex, eyey, eyez, 1.0);
	up = glm::vec4(0.0, 1.0, 0.0, 0.0);
	at = glm::vec4(0.0, 0.0, 0.0, 1.0);
	
	float radianRotateAngle = glm::radians(rotateAngle);
	float radianUpAngle = glm::radians(upAngle);

	// 计算eye的x, y, z分量
	eye.x = radius * glm::sin(radianRotateAngle) * glm::cos(radianUpAngle);
	eye.y = radius * glm::sin(radianUpAngle);
	eye.z = radius * glm::cos(radianRotateAngle) * glm::cos(radianUpAngle);
	eye.w = 1.0f; // 齐次坐标的w分量

	// 当upAngle大于90度时，相机翻转到up向量的下方
	if (upAngle > 90.0f) {
		up.y = -1.0f;
	}

}


void Camera::keyboard(int key, int action, int mode)
{

	// 键盘事件处理
	if (key == GLFW_KEY_X && action == GLFW_PRESS && mode == 0x0000)
	{
		rotateAngle += 5.0;
	}
	else if(key == GLFW_KEY_X && action == GLFW_PRESS && mode == GLFW_MOD_SHIFT)
	{
		rotateAngle -= 5.0;
	}
	else if(key == GLFW_KEY_Y && action == GLFW_PRESS && mode == 0x0000)
	{
		upAngle += 5.0;
		if (upAngle > 180)
			upAngle = 180;
	}
	else if(key == GLFW_KEY_Y && action == GLFW_PRESS && mode == GLFW_MOD_SHIFT)
	{
		upAngle -= 5.0;
		if (upAngle < -180)
			upAngle = -180;
	}
	else if(key == GLFW_KEY_R && action == GLFW_PRESS && mode == 0x0000)
	{
		radius += 0.1;
	}
	else if(key == GLFW_KEY_R && action == GLFW_PRESS && mode == GLFW_MOD_SHIFT)
	{
		radius -= 0.1;
	}
	else if(key == GLFW_KEY_F && action == GLFW_PRESS && mode == 0x0000)
	{
		fov += 5.0;
	}
	else if(key == GLFW_KEY_F && action == GLFW_PRESS && mode == GLFW_MOD_SHIFT)
	{
		fov -= 5.0;
	}
	else if(key == GLFW_KEY_A && action == GLFW_PRESS && mode == 0x0000)
	{
		aspect += 0.1;
	}
	else if(key == GLFW_KEY_A && action == GLFW_PRESS && mode == GLFW_MOD_SHIFT)
	{
		aspect -= 0.1;
	}
	else if(key == GLFW_KEY_S && action == GLFW_PRESS && mode == 0x0000)
	{
		scale += 0.1;
	}
	else if(key == GLFW_KEY_S && action == GLFW_PRESS && mode == GLFW_MOD_SHIFT)
	{
		scale -= 0.1;
	}
	else if(key == GLFW_KEY_SPACE && action == GLFW_PRESS && mode == 0x0000)
	{
		radius = 4.0;
		rotateAngle = 0.0;
		upAngle = 0.0;
		fov = 45.0;
		aspect = 1.0;
		scale = 1.5;
	}

}
