import socket
import select
import re

class Tcp_server(object):
	def __init__(selt):
		selt.epl = select.epoll()

		selt.tcp_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		# 绑定ip地址，端口
		selt.tcp_server.bind(("",7990))
		# tcp_server 设置为监听模式
		selt.tcp_server.listen(128)
		# 设置为非堵塞
		selt.tcp_server.setblocking(False)
		# 将服务器套接字交给系统监听 fd
		# fileno()获取套接字的fd地址,EPOLLIN对套接字进行事件监听
		selt.epl.register(selt.tcp_server.fileno(),select.EPOLLIN)
		# 创建一个列表用来存放（套接字和事件的返回） poll()返回一个元祖
		selt.fd_event_list = list()
		# 创建一个字典用来存放
		selt.fd_socket_dict = dict()

	def __del__(selt):
		selt.tcp_server.close()


	def http_server(selt,new_client_socket,recv_data):
		# http的头部，200是客户端返回的信息有效，服务器向客户端发送正确的信息
		respones_head = "HTTP/1.1 200 OK\r\n"
		# 错误信息
		respones_eorr = "HTTP/1.1 400 NOT FOUND\r\n"
		respones_eorr += "\r\n"
		respones_eorr += "<h1>404 NOT FOUND</h1>"

		# 将客户端的http信息按行拆分
		html_items = recv_data.splitlines()
		# 放入异常处理中,防止因为html_items[0]和ret.group(1)为空而出错
		try:
			# 通过正则表达式获取客户端请求的页面
			ret = re.match(r"[^/]+([^ ]*)",html_items[0])
			# 判断正则表达式是否捕获到了客户端的请求
			if ret.group(1):
				# 将ret.group(1)的指向赋予file_name
				file_name = ret.group(1)
				# 判断 file_name 的 内容是不是" 如果是则将主页路径赋给file_name
				if file_name == "/":
					file_name = "/index.html"
			# 打开客户端请求的页面
			html_context = open("html"+file_name,"rb")
		except Exception as rs:
			print(rs)
			# 出现异常则返回失败页面
			new_client_socket.send(respones_eorr.encode("utf-8"))
		else:
			# http的身体
			respones_body = html_context.read()
			# 关闭文件指向
			html_context.close()
			# 返回的数据长度，让客户端可以判断这个数据是否接受完毕
			respones_head += "Content-Length:%d\r\n" % len(respones_body)
			respones_head += "\r\n"
			# 将头部和身体组合
			respones = respones_head.encode("utf-8")+respones_body
			# 将获取的文件内容返回给客户端
			new_client_socket.send(respones)
		finally:
			pass
			



	def run(selt):
		"""
		服务器不断循环等待客户端连接
		"""
		while True:
			# 通过系统和应用程序共同的内存空间进行监听
			# 用列表接受系统监听到的消息，默认堵塞,当有数据的时候才会通过
			# 只会返回收到数据的套接字
			selt.fd_event_list = selt.epl.poll()

			# 当上一步通过后，进行循环，将列表里的接受到的元祖全部遍历
			# 因为返回的是一个元祖(fd,socket)
			for fd,event in selt.fd_event_list:
				# 判断接受数据的是服务器套接字，还是客户端的套接字
				if fd == selt.tcp_server.fileno():
					new_client_socket,new_client_addr = selt.tcp_server.accept()
					# 设置客户端套接字为非堵塞
					new_client_socket.setblocking(False)
					# 将客户端套接字交于系统进行监听
					selt.epl.register(new_client_socket.fileno(),select.EPOLLIN)
					# 将客户端套接字和fd地址放进字典中
					# fd:"socket"
					selt.fd_socket_dict[new_client_socket.fileno()] = new_client_socket
				# 如果不是服务器套接字，那么判断监听到的是什么事件
				elif event == select.EPOLLIN:
					# 判断客户端服务器是否有数据发送过来
					recv_data = selt.fd_socket_dict[fd].recv(1024).decode("utf-8")
					# 如果recv_data 有数据，那么执行http_server方法
					if recv_data:
						selt.http_server(selt.fd_socket_dict[fd],recv_data)
					else:
						# 如果没有信息则客户端进行了四次挥手,服务器则将客户端套接字关闭
						# 关闭客户端套接字
						selt.fd_socket_dict[fd].close()
						# 将客户端的套接字和fd地址取消监听
						selt.epl.unregister(fd)
						# 从字典中除去
						del selt.fd_socket_dict[fd]


def main():
	pass

if __name__ == '__main__':
	main()
	
