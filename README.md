# JudgeLight
某中二的鶸评测姬

# 介绍
JudgeLight是一个较为独立的OJ评测机，中文名为**某中二的鶸评测姬**，她封装了Lo-runner的接口并利用redis队列实现了多进程的评测，比起多线程评测的性能更加高，评测更加快。

向外提供了POST提交和GET查询两个接口，普通用户不需要了解内部实现，可以让想写OJ的同学只需要关心网站逻辑，且网站与评测姬低耦合，开发与维护会变得更加的简单

# 平台
鶸评测姬使用Linux平台的系统函数进行资源限制与测量，因此限制只能在Linux下使用，且由于系统调用不同，因此，推荐使用64位系统，若有其他需求，请自行修改编译另一个项目[Lo-runner](https://github.com/MeiK-h/Lo-runner/)并替换掉原有的评测核心

# 依赖
Redis

PHP

Python2.7


# 使用
启动Redis服务

进入WEB目录内，使用PHP自带发布服务```php -S 0.0.0.0:8888```

进入Judge目录内，修改config.py配置，之后```bash start.sh```以启动服务

若需要限制运行权限，请自行修改相关位置代码(解除注释)，并配置Linux用户权限

# 评测说明
all_judge代表了是否要评测所有的数据，若为False的话，则会在出现任意错误的时候停止评测，否则会评测每组数据

special_judge表示本题是否为Special Judge的题目，若选择此项，则对应的数据文件夹中应该有spj程序(spj程序规范请看我的这篇[博客](http://blog.csdn.net/meik_sdut/article/details/73228166))

项目中给出了两个题目的数据，其中1000题目对应[SDUTOJ1000](http://acm.sdut.edu.cn/onlinejudge2/index.php/Home/Index/problemdetail/pid/1000.html)，1001是一个special judge的题目，没有输入数据，要求输出一个128-256之间的任意数字

需要注意的是，即使题目没有标准输入输出，也应该有空的输入输出文件，否则会返回no data的错误