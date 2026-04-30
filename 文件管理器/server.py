# -*- coding: utf-8 -*-
import sqlite3
import hashlib
import base64
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api.db')

def get_password_key(password):
    key = 0
    for c in password:
        key = key * 31 + ord(c)
    return key % 1000000

def simple_encrypt(text, password):
    if not text:
        return ''
    seed = get_password_key(password)
    result = []
    for i, c in enumerate(text):
        code = ord(c)
        shifted = (code + seed + i) % 126
        result.append(chr(shifted))
    return base64.b64encode(''.join(result).encode()).decode()

def simple_decrypt(encrypted, password):
    if not encrypted:
        return ''
    try:
        seed = get_password_key(password)
        decoded = base64.b64decode(encrypted.encode()).decode()
        result = []
        for i, c in enumerate(decoded):
            code = ord(c)
            shifted = (code - seed - i) % 126
            result.append(chr(shifted))
        return ''.join(result)
    except Exception:
        return ''

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            owner TEXT,
            repo TEXT,
            token_encrypted TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

class APIHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _get_json(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            return json.loads(self.rfile.read(content_length).decode('utf-8'))
        return {}

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api.db' or path == '/api.db' or path == 'api.db':
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.end_headers()
            with open(DB_PATH, 'rb') as f:
                self.wfile.write(f.read())
            return

        if path == '/api/login':
            self._send_json({'success': False, 'error': '请使用POST方法'}, 405)
            return

        if path == '/api/users':
            conn = get_db()
            cursor = conn.execute('SELECT id, username, owner, repo, created_at FROM users')
            users = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self._send_json({'success': True, 'users': users})
            return

        if path.startswith('/api/users/'):
            try:
                user_id = int(path.split('/')[-1])
                conn = get_db()
                cursor = conn.execute('SELECT id, username, owner, repo, created_at FROM users WHERE id = ?', (user_id,))
                user = cursor.fetchone()
                conn.close()
                if user:
                    self._send_json({'success': True, 'user': dict(user)})
                else:
                    self._send_json({'success': False, 'error': '用户不存在'}, 404)
            except ValueError:
                self._send_json({'success': False, 'error': '无效的用户ID'}, 400)
            return

        if path == '/api/files':
            self.serve_static_file('/文件管理器.html')
            return

        self.serve_static_file(path)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        data = self._get_json()

        if path == '/api/login':
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()

            if not username or not password:
                self._send_json({'success': False, 'error': '请输入用户名和密码'}, 400)
                return

            conn = get_db()
            cursor = conn.execute('SELECT id, username, password_hash, salt, owner, repo, token_encrypted FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            conn.close()

            if not user:
                self._send_json({'success': False, 'error': '用户不存在'}, 401)
                return

            password_hash = hashlib.sha256((password + user['salt']).encode()).hexdigest()
            if password_hash != user['password_hash']:
                self._send_json({'success': False, 'error': '密码错误'}, 401)
                return

            token = simple_decrypt(user['token_encrypted'], password) if user['token_encrypted'] else ''

            self._send_json({
                'success': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'owner': user['owner'],
                    'repo': user['repo'],
                    'token': token
                }
            })
            return

        if path == '/api/users':
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            owner = data.get('owner', '').strip()
            repo = data.get('repo', '').strip()
            token = data.get('token', '').strip()

            if not username or not password:
                self._send_json({'success': False, 'error': '用户名和密码不能为空'}, 400)
                return

            import random
            import string
            salt = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            token_encrypted = simple_encrypt(token, password) if token else ''

            conn = get_db()
            try:
                cursor = conn.execute(
                    'INSERT INTO users (username, password_hash, salt, owner, repo, token_encrypted) VALUES (?, ?, ?, ?, ?, ?)',
                    (username, password_hash, salt, owner, repo, token_encrypted)
                )
                conn.commit()
                user_id = cursor.lastrowid
                conn.close()
                self._send_json({'success': True, 'message': '用户创建成功', 'user_id': user_id})
            except sqlite3.IntegrityError:
                conn.close()
                self._send_json({'success': False, 'error': '用户名已存在'}, 400)
            return

        self._send_json({'success': False, 'error': '无效的API路径'}, 404)

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path
        data = self._get_json()

        if path.startswith('/api/users/') and path.endswith('/token'):
            try:
                user_id = int(path.split('/')[-2])
                new_token = data.get('token', '').strip()
                new_owner = data.get('owner', '').strip()
                new_repo = data.get('repo', '').strip()
                user_password = data.get('password', '').strip()

                if not new_token:
                    self._send_json({'success': False, 'error': 'Token不能为空'}, 400)
                    return

                if not user_password:
                    self._send_json({'success': False, 'error': '请输入用户密码用于加密Token'}, 400)
                    return

                conn = get_db()
                cursor = conn.execute('SELECT password_hash, salt FROM users WHERE id = ?', (user_id,))
                user = cursor.fetchone()
                if not user:
                    conn.close()
                    self._send_json({'success': False, 'error': '用户不存在'}, 404)
                    return

                # 验证密码
                password_hash = hashlib.sha256((user_password + user['salt']).encode()).hexdigest()
                if password_hash != user['password_hash']:
                    conn.close()
                    self._send_json({'success': False, 'error': '密码错误'}, 401)
                    return

                token_encrypted = simple_encrypt(new_token, user_password)
                conn.execute('UPDATE users SET owner = ?, repo = ?, token_encrypted = ? WHERE id = ?',
                           (new_owner, new_repo, token_encrypted, user_id))
                conn.commit()
                conn.close()
                self._send_json({'success': True, 'message': 'GitHub信息更新成功（已加密存储）'})
            except ValueError:
                self._send_json({'success': False, 'error': '无效的用户ID'}, 400)
            return

        if path.startswith('/api/users/') and path.endswith('/password'):
            try:
                parts = path.split('/')
                user_id = int(parts[-2])
                old_password = data.get('old_password', '').strip()
                new_password = data.get('new_password', '').strip()

                if not old_password or not new_password:
                    self._send_json({'success': False, 'error': '旧密码和新密码都不能为空'}, 400)
                    return

                conn = get_db()
                cursor = conn.execute('SELECT password_hash, salt, token_encrypted FROM users WHERE id = ?', (user_id,))
                user = cursor.fetchone()
                if not user:
                    conn.close()
                    self._send_json({'success': False, 'error': '用户不存在'}, 404)
                    return

                old_hash = hashlib.sha256((old_password + user['salt']).encode()).hexdigest()
                if old_hash != user['password_hash']:
                    conn.close()
                    self._send_json({'success': False, 'error': '旧密码错误'}, 401)
                    return

                import random
                import string
                new_salt = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                new_hash = hashlib.sha256((new_password + new_salt).encode()).hexdigest()

                token_encrypted = user['token_encrypted']
                if token_encrypted:
                    token_encrypted = simple_encrypt(simple_decrypt(token_encrypted, old_password), new_password)

                conn.execute('UPDATE users SET password_hash = ?, salt = ?, token_encrypted = ? WHERE id = ?',
                           (new_hash, new_salt, token_encrypted, user_id))
                conn.commit()
                conn.close()
                self._send_json({'success': True, 'message': '密码修改成功'})
            except ValueError:
                self._send_json({'success': False, 'error': '无效的用户ID'}, 400)
            return

        if path.startswith('/api/users/'):
            try:
                user_id = int(path.split('/')[-1])
                new_username = data.get('username', '').strip()
                new_password = data.get('password', '').strip()

                conn = get_db()

                if new_username:
                    try:
                        conn.execute('UPDATE users SET username = ? WHERE id = ?', (new_username, user_id))
                    except sqlite3.IntegrityError:
                        conn.close()
                        self._send_json({'success': False, 'error': '用户名已存在'}, 400)
                        return

                if new_password:
                    import random
                    import string
                    salt = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                    password_hash = hashlib.sha256((new_password + salt).encode()).hexdigest()
                    conn.execute('UPDATE users SET password_hash = ?, salt = ? WHERE id = ?', (password_hash, salt, user_id))

                conn.commit()
                conn.close()
                self._send_json({'success': True, 'message': '用户信息更新成功'})
            except ValueError:
                self._send_json({'success': False, 'error': '无效的用户ID'}, 400)
            return

        self._send_json({'success': False, 'error': '无效的API路径'}, 404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith('/api/users/'):
            try:
                user_id = int(path.split('/')[-1])
                conn = get_db()
                conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
                conn.commit()
                conn.close()
                self._send_json({'success': True, 'message': '用户删除成功'})
            except ValueError:
                self._send_json({'success': False, 'error': '无效的用户ID'}, 400)
            return

        self._send_json({'success': False, 'error': '无效的API路径'}, 404)

    def serve_static_file(self, path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        decoded_path = unquote(path)

        if decoded_path == '/' or decoded_path == '':
            target_file = '文件管理器.html'
        else:
            target_file = decoded_path.lstrip('/')

        file_path = os.path.join(base_dir, target_file)
        print(f'Request: {path} -> {decoded_path} -> {file_path}')

        if os.path.isfile(file_path):
            self.send_response(200)
            if target_file.endswith('.html'):
                self.send_header('Content-Type', 'text/html; charset=utf-8')
            elif path.endswith('.js'):
                self.send_header('Content-Type', 'application/javascript')
            elif path.endswith('.css'):
                self.send_header('Content-Type', 'text/css')
            elif path.endswith('.db'):
                self.send_header('Content-Type', 'application/octet-stream')
            else:
                self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            print(f'File not found: {file_path}')
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

def run_server(port=8080):
    init_db()
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f'服务器已启动: http://localhost:{port}/文件管理器.html')
    print(f'API端点: http://localhost:{port}/api/')
    server.serve_forever()

if __name__ == '__main__':
    run_server()