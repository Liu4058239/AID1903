'''
    群聊天室
    1设计思路
        *转发
        模型: 客户端-->服务端--转发给其他客户端
        *网络模型: UDP通信
        *保存用户信息 [(name,addr),()] {name:addr,}
        *收发关系处理: 采用多进程分别进行收发操作
    2结构设计
        *采用什么样的封装结构: 函数
        *编写一个功能,测试一个功能
        *注意注释和结构的设计
    3分析功能模块,指定具体编写流程
        *搭建网络连接
        *进入聊天室
            客户端: *输入姓名
                   *将姓名发送给服务器
                   *接收返回的结果
                   *如果不允许则重复输入姓名
            服务器: *接收姓名
                   *判断姓名是否存在
                   *将结果给客户端
                   *如果允许进入聊天室增加用户信息
                   *通知其他用户
        *聊天
            客户端: *创建新的进程
                   *一个进程循环发送消息
                   *一个进程循环接收消息
            服务端: *接收请求,判断请求类型
                   *将消息转发给其他用户
        *退出聊天室
            客户端: *输入quit或者ctrl+c退出
                   *将请求发送给服务端
                   *结束进程
                   *接收端收到exit退出进程
            服务端: *接收消息
                   *将退出消息告知其他人
                   *给该用户发送'exit'
                   *删除用户
        *管理员消息
    4 协议
        *如果允许进入聊天室,服务端发送'OK'给客户端
        *如果不允许进入聊天室,则服务端发送不允许的原因
        *请求类别:
            L-----进入聊天室
            C-----聊天
            Q-----退出聊天室
        *用户存储结构:{name:addr...}
        *客户端如果输入quit或者ctrl+c ,点击esc退出聊天室
'''
from socket import *
import os,sys

#服务器地址
ADDR = '176.140.6.143',9999
#发送消息
def send_msg(s,name):
    '''
    发送消息
    :param s:
    :param name:
    :return:
    '''
    while True:
        try:
            text = input('发言:')
        except KeyboardInterrupt: #如果按ctrl+c 则退出进程
            text = 'quit'
        #退出聊天室
        if text == 'quit':
            msg = 'Q' + name
            s.sendto(msg.encode(),ADDR)
            sys.exit('\n退出聊天室')
        msg = 'C %s %s'%(name,text)
        s.sendto(msg.encode(),ADDR)
#接收消息
def recv_msg(s):
    '''
    接收消息
    :param s:
    :return:
    '''
    while True:
        data,addr = s.recvfrom(2048)
        #服务端发送exit表示让客户端的接收消息的进程退出
        if data.decode() == 'EXIT':
            sys.exit()
        print(data.decode() + '\n发:',end ='')
#创建网络连接
def main():
    #创建套接字
    s = socket(AF_INET,SOCK_DGRAM)
    while True:
        name = input('请输入你的姓名:')
        msg = 'L ' + name
        s.sendto(msg.encode(),ADDR)
        #等待回应
        data,addr = s.recvfrom(1024)
        if data.decode()  == 'OK':
            print('您已进入至尊聊天室')
            break
        else:
            print(data.decode())
    #创建新的进程
    pid = os.fork()
    if pid < 0:
        sys.exit('Error')
    elif pid == 0:
        send_msg(s,name)
    else:
        recv_msg(s)
if __name__ == '__main__':
    main()