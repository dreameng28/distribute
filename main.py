#coding=utf-8
__author__ = 'dreameng'

import Queue, requests, re
from multiprocessing.managers import BaseManager

# 发送任务的队列:
task_queue = Queue.Queue()
# 接收结果的队列:
result_queue = Queue.Queue()

# 从BaseManager继承的QueueManager:
class QueueManager(BaseManager):
    pass

# 把两个Queue都注册到网络上, callable参数关联了Queue对象:
QueueManager.register('get_task_queue', callable=lambda: task_queue)
QueueManager.register('get_result_queue', callable=lambda: result_queue)

# 绑定端口5000, 设置验证码'abc':
manager = QueueManager(address=('', 8000), authkey='abc')

# 启动Queue:
manager.start()


# 获得通过网络访问的Queue对象:
taskQueen = manager.get_task_queue()
resultQueen = manager.get_result_queue()

# # 放几个任务进去:
# for i in range(10):
#     print('Put num %d...' % i)
#     taskQueen.put(i)
# # 从result队列读取结果:
# print('Try get results...')
# for i in range(10):
#     r = resultQueen.get(timeout=50)
#     print('Result: %s' % r)


beginUrl = "http://www.aitaotu.com/tag/juru.html"
baseUrl = "http://www.aitaotu.com"

# print content
content = requests.get(beginUrl).content
groupPattern = '下一页</a><a href="' + beginUrl[22: -5] + '/' + '(.*?).html">末页</a>'
groupPageNum = re.findall(groupPattern, content, re.S)
groupPageNum = int(groupPageNum[0])
print groupPageNum


# 获取全部套图首页的url
for i in range(1, groupPageNum+1):
    if i == 1:
        html = requests.get(beginUrl)
    else:
        otherUrl = beginUrl[: -5] + '/' + str(i) + '.html'
        print otherUrl
        html = requests.get(otherUrl)
    content = html.content
    link = re.findall('<p class="ph3"><a href="(.*?)" target="_blank" title=', content, re.S)
    for each in link:
        taskQueen.put(baseUrl + each)

print taskQueen.qsize()

for i in range(taskQueen.qsize()):
    if i == 0:
        print 'waiting worker...'
    r = resultQueen.get(timeout=120)
    print('Result: %s' % r)
    print taskQueen.qsize()



# 关闭:
manager.shutdown()
