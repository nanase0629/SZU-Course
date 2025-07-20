import os

# 获取用户主目录
home_dir = os.path.expanduser("~")
condarc_path = os.path.join(home_dir, ".condarc")

# 设定路径（设置 envs 安装在当前目录的 ./envs）
condarc_content = "envs_dirs:\n  - ./envs\n"

# 写入文件
with open(condarc_path, "w") as f:
    f.write(condarc_content)

print(f".condarc 已生成到: {condarc_path}")
