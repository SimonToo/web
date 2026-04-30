# -*- coding: utf-8 -*-
import sqlite3
import hashlib
import os
import base64

DB_PATH = 'D:/Users/Administrator/Desktop/文件管理器/api.db'

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

username = input('用户名: ')
password = input('密码: ')
new_owner = input('GitHub用户名: ')
new_repo = input('仓库名: ')
new_token = input('GitHub Token: ')

# 获取当前salt
conn = sqlite3.connect(DB_PATH)
cursor = conn.execute('SELECT salt FROM users WHERE username = ?', (username,))
row = cursor.fetchone()
if not row:
    print('用户不存在')
    exit()

salt = row[0]
password_hash = hashlib.sha256((password + salt).encode()).hexdigest()

# 验证密码
cursor = conn.execute('SELECT password_hash FROM users WHERE username = ? AND password_hash = ?', (username, password_hash))
if not cursor.fetchone():
    print('密码错误')
    exit()

# 更新
token_encrypted = simple_encrypt(new_token, password)
conn.execute('UPDATE users SET owner = ?, repo = ?, token_encrypted = ? WHERE username = ?',
             (new_owner, new_repo, token_encrypted, username))
conn.commit()
conn.close()
print('更新成功!')