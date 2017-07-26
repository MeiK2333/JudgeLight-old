#coding=utf-8

#任务队列长度
queue_size = 0
#评测线程数
count_thread = 1

#redis配置
#redis主机
redis_host = "127.0.0.1"
#redis端口
redis_port = 6379
#redis数据库号
redis_db = 0
#redis作为任务队列的list键名
redis_list_name = "judge_list"
#用于储存结果的Hash表名
redis_hash_name = "judge_result"


#评测目录
work_dir = "/home/meik/judge/work"
#数据目录
data_dir = "/home/meik/data"

#允许的语言列表
language_list = [
    "gcc",
    "g++",
    "g++11",
    "java",
    "python2",
    "python3",
]

#写入文件选项
file_name = {
    "gcc": "main.c",
    "g++": "main.cpp",
    "g++11": "main.cpp",
    "java": "Main.java",
    "python2": "main.py",
    "python3": "main.py",
}

#编译选项
compile_cmd = {
    "gcc": ["gcc", "main.c", "-o", "main", "-Wall", "-lm", "-O2", "-std=c99"],
    "g++": ["g++", "main.cpp", "-o", "main", "-Wall", "-lm", "-O2"],
    "g++11": ["g++", "main.cpp", "-o", "main", "-Wall", "-lm", "-O2", "-std=c++11"],
    "java": ["javac", "Main.java"],
    "python2": ["ls"],
    "python3": ["ls"],
}
#编译时限(MS)
COMPILE_TIME = 1000
#编译内存限制(KB)
COMPILE_MEMORY = 20000

#运行选项
run_cmd = {
    "gcc": ["./main"],
    "g++": ["./main"],
    "g++11": ["./main"],
    "java": ["java", "-cp", "./", "Main"],
    "python2": ["python2", "main.py"],
    "python3": ["python3", "main.py"],
}