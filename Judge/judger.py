#coding=utf-8
import os
import stat
import json
import time
import redis
import lorun
import shutil
import logging
import threading
from multiprocessing import Process, Queue, Pool

import config

RESULT_STR = [
    'Accepted',
    'Presentation Error',
    'Time Limit Exceeded',
    'Memory Limit Exceeded',
    'Wrong Answer',
    'Runtime Error',
    'Output Limit Exceeded',
    'Compile Error',
    'System Error'
]

def worker(task):
    '''评测进程'''
    Id = str(task['id'])
    pid = str(task['pid'])
    language = task['language'].lower()
    time_limit = int(task['time_limit'])
    memory_limit = int(task['memory_limit'])
    all_judge = task['all_judge']
    special_judge = task['special_judge']
    #编译代码
    if not compile_code(Id, language):
        return
    #获取数据组数
    data_count = get_data_count(pid)
    if data_count == 0:
        update_result(Id, 'system error', 'no data')
        return
    #开始评测
    judge(Id, pid, data_count, time_limit, memory_limit, language, all_judge, special_judge)
    #清理现场
    shutil.rmtree(os.path.join(config.work_dir, Id))

def judge(Id, pid, data_count, time_limit, memory_limit, language, all_judge, special_judge):
    '''评测代码'''
    rsts = []
    rst_flag = 0
    for i in range(data_count):
        rst = judge_one(Id, pid, str(i + 1), time_limit, memory_limit, language, special_judge)
        if rst_flag == 0 and rst['result'] != 0:
            rst_flag = rst['result']
        rst['result_str'] = RESULT_STR[rst['result']]
        rsts.append(rst)
        print rst
        if (all_judge is False) and (rst['result'] != 0):
            break
    update_result(Id, RESULT_STR[rst_flag], rsts)
    return rsts

def judge_one(Id, pid, data_num, time_limit, memory_limit, language, special_judge):
    '''评测一组数据'''
    in_path = os.path.join(config.data_dir, pid, "data%s.in" % data_num)
    out_path = os.path.join(config.data_dir, pid, "data%s.out" % data_num)
    tmp_path = os.path.join(config.work_dir, Id, "temp.out")
    try:
        fin = open(in_path)
        ftmp = open(tmp_path, 'w')
    except:
        fin.close()
        ftmp.close()
        return False
    os.chdir(os.path.join(config.work_dir, str(Id)))
    runcfg = {
        'args': config.run_cmd[language],
        'fd_in': fin.fileno(),
        'fd_out': ftmp.fileno(),
        'timelimit': time_limit, #in MS
        'memorylimit': memory_limit, #in KB
        #'runner': config.RUNNER, #限制运行用户
    }
    rst = lorun.run(runcfg)
    fin.close()
    ftmp.close()

    if rst['result'] == 0: #程序正常运行结束
        if special_judge: #判断是否为special judge
            spj_path = os.path.join(config.data_dir, pid, config.SPJ_NAME)
            spjcfg = {
                'args': [spj_path, in_path, out_path, tmp_path],
                'timelimit': config.SPJ_TIME,
                'memorylimit': config.SPJ_MEMORY,
                #'runner': config.RUNNER,
            }
            outbuffer = lorun.special(spjcfg)
            if outbuffer:
                print outbuffer
                update_result(Id, 'wrong answer', outbuffer)
                return {'result': 4}
            return rst
        else: #否则为普通评测方式
            ftmp = open(tmp_path)
            fout = open(out_path)
            crst = lorun.check(fout.fileno(), ftmp.fileno())
            fout.close()
            ftmp.close()
            #os.remove(tmp_path)
            if crst != 0:
                return {'result': crst}

    return rst

def compile_code(Id, language):
    '''将代码编译成可执行程序'''
    update_result(Id, 'compiling') #修改评测状态
    logging.info('compile %s' % Id)
    os.chdir(os.path.join(config.work_dir, Id)) #修改工作目录
    comcfg = {
        'args': config.compile_cmd[language],
        'timelimit': config.COMPILE_TIME,
        'memorylimit': config.COMPILE_MEMORY,
        #'runner': config.RUNNER,
    }
    errbuffer = lorun.compile(comcfg)
    if errbuffer:
        update_result(Id, 'compile error', errbuffer)
        print 'compile error'
        print errbuffer
        return False
    return True

def get_data_count(pid):
    '''获取指定题目的数据组数'''
    full_path = os.path.join(config.data_dir, pid)
    files = None
    try:
        files = os.listdir(full_path)
    except OSError, e:
        logging.error(e)
        return 0
    cnt = 0
    for item in files:
        if item.endswith(".in") and item.startswith("data"):
            cnt += 1
    return cnt

def update_result(Id, result, prompt=""):
    '''更新评测状态'''
    Redis = redis.StrictRedis(config.redis_host, config.redis_port, config.redis_db)
    #读取原有信息
    redis_result = Redis.hget(config.redis_hash_name, Id)
    redis_result_dic = json.loads(redis_result)
    redis_result_dic['result'] = result
    redis_result_dic['prompt'] = prompt
    #更新状态
    Redis.hset(config.redis_hash_name, Id, json.dumps(redis_result_dic))

def write_code(id, pid, language, code):
    '''将代码写入对应的文件'''
    try:
        work_path = os.path.join(config.work_dir, str(id))
        os.mkdir(work_path)
    except OSError, e:
        logging.error(e)
        return False
    real_path = os.path.join(work_path, config.file_name[language])
    f = open(real_path, 'w')
    try:
        f.write(code.encode('utf-8', 'ignore'))
    except Exception, e:
        logging.error("%s not write code to file\n%s" % (id, e))
        f.close()
        return False
    f.close()
    #os.chmod(work_path, stat.S_IRWXO)
    #os.chmod(real_path, stat.S_IRWXO)
    return True

def put_task_into_queue(judge_queue):
    '''死循环将任务添加至队列'''
    while True:
        Redis = None
        while True:
            #尝试连接Redis
            try:
                Redis = redis.StrictRedis(config.redis_host, config.redis_port, config.redis_db)
                print 'connect to redis'
                break
            except:
                logging.error('Cannot connect to redis, try again')
                time.sleep(1)
        try:
            while True:
                #从redis中获得数据
                redis_task = Redis.blpop(config.redis_list_name, 120)
                redis_task_dic = json.loads(redis_task[1])
                #判断语言是否受支持
                if not redis_task_dic['language'].lower() in config.language_list:
                    print 'language not define'
                    update_result(redis_task_dic['id'], 'system error', 'language not define')
                    continue
                update_result(redis_task_dic['id'], 'write on file')
                print 'write to file'
                #尝试将代码写入文件
                if write_code(redis_task_dic['id'], redis_task_dic['pid'], redis_task_dic['language'], redis_task_dic['code']):
                    update_result(redis_task_dic['id'], 'in queue')
                else:
                    logging.error("write %s error" % redis_task_dic['id'])
                    update_result(redis_task_dic['id'], 'system error', 'write error')
                    continue
                #加入判题队列
                judge_queue.put(redis_task_dic)
        except:
            Redis = None
                    

def start_get_task(judge_queue):
    '''开启获取任务线程'''
    t_get_task = threading.Thread(target=put_task_into_queue, name='get_task', args=(judge_queue, ))
    t_get_task.start()

def start_protect(judge_queue):
    '''开启评测进程'''
    pool = Pool()
    while True:
        task = judge_queue.get() #会阻塞直到获取到数据
        pool.apply_async(worker, args=(task, )) #添加至进程池，最多同时运行系统核数个，多余的会在前面的运行完后自动开始
    pool.join()

def main():
    '''主函数，启动队列线程与判题进程'''
    logging.basicConfig(level = logging.INFO,
                        format = '%(asctime)s --- %(message)s', )
    judge_queue = Queue(config.queue_size) #判题队列
    start_get_task(judge_queue)
    start_protect(judge_queue)

if __name__ == "__main__":
    main()
