import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from cpustat import GetCpuLoad

# HOST_NAME = '192.168.1.10'  # !!!REMEMBER TO CHANGE THIS!!!
HOST_NAME = '127.0.0.1'  # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 8000


class MyHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        cpu_load = GetCpuLoad()
        cpu_usage = cpu_load.getcpuload()['cpu']
        cpu_info = cpu_load.getcpuinfo()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('<!DOCTYPE html><html><head><title>OS Info</title></head><body>'.encode('utf-8'))
        self.wfile.write('<table>'.encode('utf-8'))
        self.wfile.write('<tr><th colspan="2">Info</th></tr>'.encode('utf-8'))
        self.wfile.write(('<tr><td>Data/Hora</td><td>{}</td></tr>'.format(1)).encode('utf-8'))
        self.wfile.write(('<tr><td>Uptime</td><td>{}</td></tr>'.format(1)).encode('utf-8'))
        self.wfile.write(('<tr><td>CPU</td><td>{}</td></tr>'.format(cpu_info)).encode('utf-8'))
        self.wfile.write(('<tr><td>Uso da CPU</td><td>{:.2f}%</td></tr>'.format(cpu_usage)).encode('utf-8'))
        self.wfile.write(('<tr><td>RAM Total/Usada</td><td>{}</td></tr>'.format(1)).encode('utf-8'))
        self.wfile.write(('<tr><td>OS</td><td>{}</td></tr>'.format(1)).encode('utf-8'))
        self.wfile.write('</table>'.encode('utf-8'))
        self.wfile.write('<div style="margin:16px"></div>'.encode('utf-8'))
        self.wfile.write('<table>'.encode('utf-8'))
        self.wfile.write(
            '<thead><tr><th colspan="2">Processos</th></tr><tr><th>PID</th><th>Nome</th></tr></thead>'.encode('utf-8'))
        for i in range(1, 3):
            self.wfile.write(('<tr><td>{}</td><td>{}</td></tr>'.format(i, i * 2)).encode('utf-8'))
        self.wfile.write('</table>'.encode('utf-8'))
        self.wfile.write(
            '<style>html{color:#fff;font-family:"Roboto Mono",monospace;height:100%;width:100%}table{background-color:#78a6c8;border:8px solid rgba(0,0,0,0%);border-collapse:collapse;border-radius:8px}tr>*+*{padding-left:2em}hr{margin:8px 0}</style>'.encode(
                'utf-8'))
        self.wfile.write('</body></html>'.encode('utf-8'))


if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print(time.asctime(), 'Server Starts - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server Stops - %s:%s' % (HOST_NAME, PORT_NUMBER))
