from socket_selectors import SelectorServer


s = SelectorServer('localhost', 5000)
s.serve_forever()