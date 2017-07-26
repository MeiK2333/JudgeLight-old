#coding=utf-8
import os
import json
import time
import redis
import shutil
import logging
import threading
from Queue import Queue

import config

judge_que = Queue(config.queue_size) #初始化队列

def worker():
    '''工作线程，循环扫描队列，获取任务并执行'''
    while True:
        if judge_que.empty() is True:
            logging.info("%s idle" % threading.current_thread().name)
        task = q.get() #获取任务，若队列为空则阻塞
        Id = task['id']
        pid = task['pid']
        language = task['language']
        all_judge = task['all_judge']
        special_judge = task['special_judge']
        


def update_result(id, result, prompt=""):
    '''更新评测状态'''
    Redis = redis.StrictRedis(config.redis_host, config.redis_port, config.redis_db)
    #读取原有信息
    redis_result = Redis.hget(config.redis_hash_name, id)
    redis_result_dic = json.loads(redis_result)
    redis_result_dic['result'] = result
    redis_result_dic['prompt'] = prompt
    #更新状态
    Redis.hset(config.redis_hash_name, id, json.dumps(redis_result_dic))

def check_thread():
    '''检测评测程序是否存在,小于config规定数目则启动新的'''
    while True:
        try:
            if threading.active_count() < config.count_thread + 3:
                logging.info("start new thread")
                t = threading.Thread(target=worker)
                t.deamon = True
                t.start()
            time.sleep(1)
        except:
            pass

def start_protect():
    '''开启评测线程'''
    t = threading.Thread(target=check_thread, name="check_thread")
    #t.daemon = True
    t.start()

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
    return True

def put_task_into_queue():
    '''将任务添加至队列'''
    while True:
        Redis = None
        while True:
            try:
                #尝试连接redis
                Redis = redis.StrictRedis(config.redis_host, config.redis_port, config.redis_db)
                print "connect to redis"
                break
            except:
                logging.error("Cannot connect to redis, try again")
                time.sleep(1)
        try:
            while True:
                redis_task = Redis.blpop(config.redis_list_name, 120)
                #从redis中获得数据
                redis_task_dic = json.loads(redis_task[1])
                #判断语言是否支持
                if not redis_task_dic['language'] in config.language_list:
                    print 'language not define'
                    update_result(redis_task_dic['id'], "system error")
                    continue
                update_result(redis_task_dic['id'], "write on file")
                print 'write to file'
                #尝试将代码写入文件
                if write_code(redis_task_dic['id'], redis_task_dic['pid'], redis_task_dic['language'], redis_task_dic['code']):
                    update_result(redis_task_dic['id'], "in queue")
                else:
                    update_result(redis_task_dic['id'], "system error")
                    continue
                #写入Queue中
                judge_que.put(redis_task_dic)
        except Exception, e:
            Redis = None

def start_get_task():
    '''开启获取任务的线程'''
    t = threading.Thread(target=put_task_into_queue, name="get_task")
    #t.daemon = True
    t.start()

def main():
    '''主函数'''
    logging.basicConfig(level=logging.INFO,
                        format = '%(asctime)s --- %(message)s',)
    start_protect()
    start_get_task()


if __name__ == '__main__':
    main()
