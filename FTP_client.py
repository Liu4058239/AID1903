'''
    ftp文件服务器客户端
'''
from socket import *
import sys
from time import sleep

#具体功能
class FtpClient:
    def __init__(self,sockfd):
        self.sockfd = sockfd

    #查看文件列表
    def do_list(self):
        self.sockfd.send(b'L') #发送请求
        #等待回复
        data = self.sockfd.recv(128).decode()
        # OK表示请求成功
        if data == 'OK':
            #接收文件列表
            data = self.sockfd.recv(4096)
            print(data.decode())
        else:
            print(data)

    #客户端退出
    def do_quit(self):
        self.sockfd.send(b'Q')
        self.sockfd.close()
        sys.exit('谢谢使用')

    #下载文件
    def do_get(self,filename):
        #发送请求
        self.sockfd.send(('G '+ filename).encode()) #G这里有个空格
        #等待回复
        data = self.sockfd.recv(128).decode()
        if data == 'OK':
            fd = open(filename,'wb')
            #接收内容写入文件
            while True:
                data = self.sockfd.recv(1024)
                if data == b'##':
                    break
                fd.write(data)
            fd.close()
        else:
            print(data)

    #上传文件
    def do_put(self,filename):
        try:
            fd = open(filename,'rb')
        except Exception:
            print('该文件不存在')
            return
        #发送请求
        filename = filename.split('/')[-1] #对路径进行切割，得到真正的文件名称
        self.sockfd.send(('P ' + filename).encode()) #Ｐ这里有个空格
        #等待回复
        data = self.sockfd.recv(1024).decode()
        if data == 'OK':
            while True:
                # 读取文件内容
                data = fd.read(1024)
                if not data:
                    sleep(0.1)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(data)
            fd.close() #易错事项
        else:
            print(data)


#发送具体请求
def request(sockfd):
    ftp = FtpClient(sockfd)
    while True:
        print('\n-------命令选项--------')
        print('----------list---------')
        print('--------get file-------')
        print('---------put file------')
        print('-----------quit--------')

        cmd = input('请输入指令：')
        if cmd.strip() == 'list': #strip()切除字符串两端的空格
            # sockfd.send(cmd.encode())
            ftp.do_list()
        elif cmd[:3] == 'get':
            filename = cmd.strip().split(' ')[-1]
            ftp.do_get(filename)
        elif cmd[:3] == 'put':
            filename = cmd.strip().split(' ')[-1]
            ftp.do_put(filename)
        elif cmd.strip() == 'quit':
            ftp.do_quit()

#网络连接
def main():
    #服务器地址
    sever_addr = ('176.140.6.143',10000)
    sockfd = socket()
    try:
        sockfd.connect(sever_addr)
    except Exception as e:
        print('连接服务器失败！')
        return
    else:
        print("""-----------------
                  Data File Image
                 ----------------- 
        """)
        cls = input('请输入文件种类：')
        if cls not in ['Data','File','Image']:
            print('Sorry input Error!!')
            return
        else:
            sockfd.send(cls.encode())
            request(sockfd) #发送具体请求

if __name__ == '__main__':
    main()
