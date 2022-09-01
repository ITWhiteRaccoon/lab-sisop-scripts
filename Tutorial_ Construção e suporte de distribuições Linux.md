# Tutorial: Construção e suporte de distribuições Linux

`Eduardo Cardoso de Andrade e Julia Alberti Maia`

### Resumo do tutorial: 
O suporte para linguagem Python pode ser adicionado através do menuconfig do Buildroot (submenu Interpreter languages and scripting). Contudo, o Python exige uma toolchain que suporte WCHAR (um tipo de variável usado para codificação de strings UTF-16). Esse suporte também pode ser adicionado através do menuconfig. Será necessário a recompilação total da distribuição (make clean, seguido de make). Caso seja utilizado C/C++, o próprio compilador cruzado criado pelo Buildroot poderá ser utilizado para compilar a aplicação.

## Passo a passo

### 1º passo: Ativar o python para nosso servidor WEB
- Na pasta `linuxdistro/buildroot`, rode o comando `make menuconfig`

- Ative o suporte a WCHAR
```
Toolchain  --->
  	 [*] Enable WCHAR support
```
- Ative o suporte a python
```
Target packages  --->
	Interpreter languages and scripting  ---> 
  		 [*]python3
```
OBS: Para ativar, use a tecla espaço.

- Salve as mudanças e saia.

OBS: Se alterarmos a toolchain, temos que rodar `make clean` de novo.

### 2º passo: Criar o servidor Web para a máquina target
- Dentro da pasta `custom-scripts`, crie uma pasta para armazenar os arquivos do servidor, como `http-server`
- Dentro desta pasta, crie os arquivos **http_server.py** e **cpustat.py**, com os seguintes conteúdos:

http_server.py
```py
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from cpustat import GetCpuLoad

HOST_NAME = '192.168.1.10'  # !!!REMEMBER TO CHANGE THIS!!!
# HOST_NAME = '127.0.0.1'  # !!!REMEMBER TO CHANGE THIS!!!
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
        self.wfile.write(('<tr><td style="white-space:nowrap">RAM Total / Usada</td><td>{:.2f} MiB / {:.2f} MiB</td></tr>'.format(totalmem, usedmem)).encode('utf-8'))
        self.wfile.write(('<tr><td>OS</td><td>{}</td></tr>'.format(version)).encode('utf-8'))
        self.wfile.write('</table>'.encode('utf-8'))
        self.wfile.write('<div style="margin:16px"></div>'.encode('utf-8'))
        self.wfile.write('<table>'.encode('utf-8'))
        self.wfile.write('<thead><tr><th colspan="2">Processos</th></tr><tr><th>PID</th><th>Nome</th></tr></thead>'.encode('utf-8'))
        for i in range(1, 3):
            self.wfile.write(('<tr><td>{}</td><td>{}</td></tr>'.format(i, i * 2)).encode('utf-8'))
        self.wfile.write('</table>'.encode('utf-8'))
        self.wfile.write('<style>html{color:#fff;font-family:"Roboto Mono",monospace;height:100%;width:100%}table{background-color:#78a6c8;border:8px solid rgba(0,0,0,0%);border-collapse:collapse;border-radius:8px}td,th{padding-bottom:4px;padding-top:4px}tr>*+*{padding-left:2em}hr{margin:8px 0}</style>'.encode('utf-8'))
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
```

cpustat.py
```py
#!/usr/bin/python 
# -*- coding: utf-8 -*-

from time import sleep
import sys

class GetCpuLoad(object):
    def __init__(self, percentage=True, sleeptime=1):
        self.percentage = percentage
        self.cpustat = '/proc/stat'
        self.sep = ' '
        self.sleeptime = sleeptime

    def getcputime(self):
        cpu_infos = {}  # collect here the information
        with open(self.cpustat, 'r') as f_stat:
            lines = [line.split(self.sep) for content in f_stat.readlines() for line in content.split('\n') if
                     line.startswith('cpu')]

            # compute for every cpu
            for cpu_line in lines:
                if '' in cpu_line: cpu_line.remove('')  # remove empty elements
                cpu_line = [cpu_line[0]] + [float(i) for i in cpu_line[1:]]  # type casting
                cpu_id, user, nice, system, idle, iowait, irq, softrig, steal, guest, guest_nice = cpu_line

                Idle = idle + iowait
                NonIdle = user + nice + system + irq + softrig + steal

                Total = Idle + NonIdle
                # update dictionionary
                cpu_infos.update({cpu_id: {'total': Total, 'idle': Idle}})
            return cpu_infos

    def getcpuload(self):
        start = self.getcputime()
        # wait a second
        sleep(self.sleeptime)
        stop = self.getcputime()

        cpu_load = {}

        for cpu in start:
            Total = stop[cpu]['total']
            PrevTotal = start[cpu]['total']

            Idle = stop[cpu]['idle']
            PrevIdle = start[cpu]['idle']
            CPU_Percentage = ((Total - PrevTotal) - (Idle - PrevIdle)) / (Total - PrevTotal) * 100
            cpu_load.update({cpu: CPU_Percentage})
        return cpu_load

if __name__ == '__main__':
    x = GetCpuLoad()
    while True:
        try:
            data = x.getcpuload()
            print(data)
        except KeyboardInterrupt:

            sys.exit("Finished")
```

- Altere o pre-build.sh para copiar os dois arquivos criados para a máquina target adicionando:
```sh
cp $BASE_DIR/../custom-scripts/http_server/http_server.py $BASE_DIR/target/usr/bin
cp $BASE_DIR/../custom-scripts/http_server/cpustat.py $BASE_DIR/target/usr/bin
```
- Compile novamente com `make clean` e depois `make`

OBS: É possível testar o servidor na máquina host enquanto o make compila na máquina target.

### Teste do servidor web
Para testar o funcionamento do servidor na máquina host, basta trocar a linha `HOST_NAME = '192.168.1.10'` por `HOST_NAME = '127.0.0.1'` e rodar o arquivo. Com o servidor rodando, basta ir para `127.0.0.1:8000` no navegador para visualizar o resultado.

### Rodando o servidor na máquina target
Após compilar, iniciamos a máquina através do `qemu-system-i386`. Uma vez dentro da máquina basta rodar o arquivo `http_server.py` que foi copiado para a pasta `/usr/bin`. Caso os tutoriais de configuração da rede tenham sido completados corretamente, o servidor deve estar acessível pela máquina host no endereço `192.168.1.10:8000`.
