#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http.server
import socketserver
import webbrowser
import os
import sys
import socket
import argparse
from urllib.parse import quote

DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(DIR)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def guess_type(self, path):
        if path.endswith('.db') or path.endswith('.enc'):
            return 'application/octet-stream'
        return super().guess_type(path)

    def log_message(self, fmt, *args):
        print(f'  {self.client_address[0]} - {fmt % args}')

    def end_headers(self):
        if self.path.endswith('.html'):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()


def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(('', port))
            return True
        except OSError:
            return False


def main():
    parser = argparse.ArgumentParser(description='本地静态文件服务器')
    parser.add_argument('--port', type=int, default=8080, help='监听端口（默认: 8080）')
    args = parser.parse_args()

    PORT = args.port

    if not check_port(PORT):
        print(f'  ❌ 端口 {PORT} 已被占用，请更换端口（使用 --port 参数）')
        sys.exit(1)

    INDEX = 'index.html'

    print()
    print('=' * 50)
    print('  本地服务器已启动')
    print('=' * 50)
    print(f'  地址: http://localhost:{PORT}')
    print(f'  按 Ctrl+C 停止服务器')
    print('=' * 50)
    print()

    webbrowser.open(f'http://localhost:{PORT}/{quote(INDEX)}')

    class ThreadedServer(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    with ThreadedServer(('', PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\n服务器已停止')


if __name__ == '__main__':
    main()
