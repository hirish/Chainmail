from ProxyServer import ProxyServer

if __name__ == '__main__':
		server = ProxyServer('0.0.0.0', 8080)
		try:
			server.run()
		except KeyboardInterrupt:
			print "Ctrl C - Stopping server"
			exit(1)
