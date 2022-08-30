import time
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST_NAME = '127.0.0.1'  # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 8000


class MyHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        """Respond to a GET request."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("<html><head><title>Title goes here.</title></head>".encode("utf-8"))
        self.wfile.write("<body><p>This is a test.</p>".encode("utf-8"))
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
        self.wfile.write(("<p>You accessed path: %s</p>" % self.path).encode("utf-8"))
        self.wfile.write("<p>Julinha gata</p>".encode("utf-8"))
        self.wfile.write("</body></html>".encode("utf-8"))


if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))
