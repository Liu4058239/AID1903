'''
 ftp服务器
【1】 分为服务端和客户端,要求可以有多个客户端同时操作。
【2】 客户端可以查看服务器文件库中有什么文件。
【3】 客户端可以从文件库中下载文件到本地。
【4】 客户端可以上传一个本地文件到文件库。
【5】 使用print在客户端打印命令输入提示,引导操作

１
    ＊
    ＊数据传输　TCP传输
２结构设计
    ＊客户端发起请求，打印请求提示界面
    ＊文件传输功能封装为类
３功能
    ＊网络搭建
    ＊查看文件库信息
    ＊下载文件
    ＊上传文件
    ＊客户端退出
４协议
    L ---表示查看文件列表
'''
from socket import *
from threading import Thread
import sys,os
from time import sleep

#全局变量
HOST = '0.0.0.0'
PORT = 10000
ADDR = (HOST,PORT)
FTP = "/home/tarena/FTP/"#文件库的路径

#将客户端请求功能封装成类
class FtpSever:
    def __init__(self,connfd,FTP_path):
        self.connfd = connfd
        self.path = FTP_path

    def do_list(self):
        #获取文件列表
        files = os.listdir(self.path)
        if not files:
            self.connfd.send('该文件类别为空'.encode())
            return
        else:
            self.connfd.send(b'OK')
            sleep(0.1)
        fs = ''
        for file in files:
            if file[0] != '.' and os.path.isfile(self.path + file):
                fs += file + '\n'
        self.connfd.send(fs.encode())

    def do_get(self,filename):
        try:
            fd = open(self.path + filename,'rb')
        except Exception:
            self.connfd.send('文件不存在'.encode())
            return
        else:
            self.connfd.send(b'OK')
            sleep(0.1)
        #发送文件内容
        while True:
            data = fd.read(1024)
            if not data: #文件结束，发送一个##,让服务器结束
                sleep(0.1)
                self.connfd.send(b'##')
                break
            self.connfd.send(data)

    def do_put(self,filename):
        if os.path.exists(self.path + filename):
            self.connfd.send('该文件已经存在！'.encode())
            return
        self.connfd.send(b'OK') #如果文件不存在，则发送ｏｋ，表示可以接收文件
        fd = open(self.path + filename,'wb')
        #接收内容
        while True:
            data = self.connfd.recv(1024)
            if data == b'##':
                break
            fd.write(data)
        fd.close()

#客户端请求处理函数
def handle(connfd):
    #选择文件夹
    cls = connfd.recv(1024).decode()
    FTP_path = FTP + cls +'/'
    ftp = FtpSever(connfd,FTP_path)
    while True:
        #接收客户端请求
        data = connfd.recv(1024).decode()
        # print(FTP_path,':',all_rows)
        #如果客户端端口返回ｄａｔａ为空
        if not data or data[0] == 'Q':
            return  #函数结束，线程就结束了
        elif data[0] == "L":
            ftp.do_list()
        elif data[0] == 'G':
            filename = data.split(' ')[-1]
            ftp.do_get(filename)
        elif data[0] == 'P':
            filename = data.split(' ')[-1]
            ftp.do_put(filename)

#网络搭建
def main():
    #创建套接字
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(5)
    print('listen the port 10000...')

    while True:
        try:
            connfd,addr = s.accept()
        except KeyboardInterrupt:
            sys.exit('服务器退出')
        except Exception as e:
            print(e)
            continue
        print('连接的客户端是：',addr)
        #创建新的线程来处理客户端请求
        client = Thread(target = handle,args = (connfd,))
        client.setDaemon(True)
        client.start()

if __name__ == '__main__':
    main()
