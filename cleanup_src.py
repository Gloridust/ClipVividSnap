import os

def clear_directory(directory):
    # 获取目录中的所有文件和子目录
    files = os.listdir(directory)
    for file in files:
        # 构建文件路径
        file_path = os.path.join(directory, file)
        # 判断文件类型，如果是文件则删除
        if os.path.isfile(file_path):
            os.remove(file_path)
        # 如果是子目录，则递归调用clear_directory函数
        elif os.path.isdir(file_path):
            clear_directory(file_path)

# 清除指定目录中的所有文件
clear_directory("src/video/")
clear_directory("src/voice/")
