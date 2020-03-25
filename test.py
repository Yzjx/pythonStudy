import epoll_fish


def main():
	tcp_server = epoll_fish.Tcp_server()
	tcp_server.run()



if __name__ == '__main__':
	main()
	
