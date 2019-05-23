'''
    chat服务端
    env: python3.6
    socket fork 练习
'''
from socket import *
import os,sys

#服务器地址
ADDR = '0.0.0.0',9999

#存储用户信息
user = {}

#进入聊天室
def do_login(s,name,addr):
    if name in user or '管理员' in name:
        s.sendto('\n该用户已经存在'.encode(),addr)
        return
    s.sendto(b'OK',addr)
    #通知其他人
    msg = '\n欢迎尊贵的皇帝%s进入聊天室'%name
    for i in user:
        s.sendto(msg.encode(),user[i])
    #将用户加入
    user[name] = addr
#聊天
def do_chat(s,name,text):
    '''
    聊天
    :param s:
    :param name:
    :param text:
    :return:
    '''
    msg = '%s : %s\n'%(name,text)
    for i in user:
        if i != name:
            s.sendto(msg.encode(),user[i])
#用户退出
def do_quit(s,name):
    msg = '\n%s退出了聊天室'%name
    for i in user:
        if i != name:
            s.sendto(msg.encode(),user[i])
        else:
            s.sendto(b'exit',user[i])
    #将用户删除
    del user[name]


def do_request(s):
    '''
    消息处理
    :param s: 接收的套接字
    :return:
    '''
    while True:
        data,addr = s.recvfrom(1024)
        msg = data.decode().split(' ')
        #区分请求类型
        if msg[0] == 'L':
            do_login(s,msg[1],addr)
        elif msg[0] == 'C':
            text = ' '.join(msg[2:])
            do_chat(s,msg[1],text)
        elif msg[0] == 'Q':
            if msg[1] not in user:
                s.sendto(b'EXIT',addr)
                continue
            do_quit(s,msg[1])
#创建网络连接
def main():
    #创建udp套接字
    s = socket(AF_INET,SOCK_DGRAM)
    s.bind(ADDR)
    pid = os.fork()
    if pid < 0:
        return
    #发送管理员消息
    elif pid == 0:
        while True:
            msg = input('超级管理员:')
            msg = 'C \n管理员消息 ' + msg
            s.sendto(msg.encode(),ADDR) #将管理员消息发送给自己,然后服务器自己在父进程中通过处理消息将消息发送到聊天室
    else:
        #请求处理
        do_request(s)#处理客户端请求


if __name__ == '__main__':
    main()