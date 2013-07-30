from ProxyServer import ProxyServer

if __name__ == '__main__':
    server = ProxyServer('0.0.0.0', 9084)
    try:
        server.run()
    except KeyboardInterrupt:
        print "Ctrl C - Stopping server"
        exit(1)
