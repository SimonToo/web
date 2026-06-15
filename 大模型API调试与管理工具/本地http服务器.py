#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http.server
import socketserver
import webbrowser
import os
import sqlite3
from urllib.parse import quote

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(DIR)

API_DB = os.path.join(DIR, 'api.db')
MODEL_DB = os.path.join(DIR, 'model.db')


def ensure_db(path, schema):
    """若 db 文件不存在则创建并建表"""
    if os.path.exists(path):
        return
    conn = sqlite3.connect(path)
    conn.execute(schema)
    conn.commit()
    conn.close()
    print(f'  ✓ 已创建: {os.path.basename(path)}')


CREATE_API = '''CREATE TABLE IF NOT EXISTS api_configs (
    id INTEGER PRIMARY KEY,
    platform TEXT NOT NULL,
    url TEXT NOT NULL,
    key TEXT NOT NULL,
    remark TEXT DEFAULT '',
    useProxy INTEGER DEFAULT 0
)'''

CREATE_MODEL = '''CREATE TABLE IF NOT EXISTS favorite_models (
    id INTEGER PRIMARY KEY,
    apiId INTEGER NOT NULL,
    modelName TEXT NOT NULL,
    remark TEXT DEFAULT ''
)'''

ensure_db(API_DB, CREATE_API)
ensure_db(MODEL_DB, CREATE_MODEL)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def guess_type(self, path):
        if path.endswith('.db') or path.endswith('.enc'):
            return 'application/octet-stream'
        return super().guess_type(path)

    def log_message(self, fmt, *args):
        print(f'  {args[0]} {args[1]} {args[2]}')


INDEX = '大模型 API 调试与管理工具.html'

print()
print('=' * 60)
print('  大模型 API 调试与管理工具')
print('  本地服务器已启动')
print('=' * 60)
print(f'  地址: http://localhost:{PORT}')
print(f'  按 Ctrl+C 停止服务器')
print('=' * 60)
print()

webbrowser.open(f'http://localhost:{PORT}/{quote(INDEX)}')

with socketserver.TCPServer(('', PORT), Handler) as httpd:
    httpd.allow_reuse_address = True
    httpd.server_activate()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n服务器已停止')
