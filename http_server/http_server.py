import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from cpustat import GetCpuLoad

# HOST_NAME = '192.168.1.10'  # !!!REMEMBER TO CHANGE THIS!!!
HOST_NAME = '127.0.0.1'  # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 8000


class MyHandler(BaseHTTPRequestHandler):
    def getprocesses(self):
        return ''
    def getversion(self):
        with open('/proc/version') as version:
            return version.readlines()[0].rstrip('\n')

    def getmeminfo(self):
        with open('/proc/meminfo') as meminfo:
            data = {}
            for line in meminfo.readlines():
                d = line.rstrip('\n').split(':')
                data.update({d[0]: int(d[1].rstrip(' kB').strip()) / 1024})
            return data

    def getuptime(self):
        with open('/proc/uptime', 'r') as uptime:
            up = [line.rstrip('\n').split(' ') for line in uptime.readlines()][0][0]
            return up

    def getcpuinfo(self):
        with open('/proc/cpuinfo', 'r') as info:
            data = [line.rstrip('\n').split(':') for line in info if line.startswith('model name')][0][1]
            return data

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        system_time = os.popen('date').read()
        uptime = self.getuptime()
        cpu_load = GetCpuLoad()
        cpu_usage = cpu_load.getcpuload()['cpu']
        cpu_info = self.getcpuinfo()
        meminfo = self.getmeminfo()
        totalmem = meminfo['MemTotal']
        usedmem = totalmem - meminfo['MemFree']
        version = self.getversion()
        processes = self.getprocesses()

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('<!DOCTYPE html><html><head><title>OS Info</title></head><body>'.encode('utf-8'))
        self.wfile.write('<table>'.encode('utf-8'))
        self.wfile.write('<tr><th colspan="2">Info</th></tr>'.encode('utf-8'))
        self.wfile.write(('<tr><td>Data/Hora</td><td>{}</td></tr>'.format(system_time)).encode('utf-8'))
        self.wfile.write(('<tr><td>Uptime</td><td>{}s</td></tr>'.format(uptime)).encode('utf-8'))
        self.wfile.write(('<tr><td>CPU</td><td>{}</td></tr>'.format(cpu_info)).encode('utf-8'))
        self.wfile.write(('<tr><td>Uso da CPU</td><td>{:.2f}%</td></tr>'.format(cpu_usage)).encode('utf-8'))
        self.wfile.write(
            ('<tr><td style="white-space:nowrap">RAM Total / Usada</td><td>{:.2f} MiB / {:.2f} MiB</td></tr>'.format(totalmem, usedmem)).encode(
                'utf-8'))
        self.wfile.write(('<tr><td>OS</td><td>{}</td></tr>'.format(version)).encode('utf-8'))
        self.wfile.write('</table>'.encode('utf-8'))
        self.wfile.write('<div style="margin:16px"></div>'.encode('utf-8'))
        self.wfile.write('<table>'.encode('utf-8'))
        self.wfile.write(
            '<thead><tr><th colspan="2">Processos</th></tr><tr><th>PID</th><th>Nome</th></tr></thead>'.encode('utf-8'))
        for i in range(1, 3):
            self.wfile.write(('<tr><td>{}</td><td>{}</td></tr>'.format(i, i * 2)).encode('utf-8'))
        self.wfile.write('</table>'.encode('utf-8'))
        self.wfile.write(
            '<style>html{color:#fff;font-family:"Roboto Mono",monospace;height:100%;width:100%}table{background-color:#78a6c8;border:8px solid rgba(0,0,0,0%);border-collapse:collapse;border-radius:8px}td,th{padding-bottom:4px;padding-top:4px}tr>*+*{padding-left:2em}hr{margin:8px 0}</style>'.encode(
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
