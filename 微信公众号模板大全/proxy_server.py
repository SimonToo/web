#!/usr/bin/env python3
import http.server
import urllib.request
import re
import os
from urllib.parse import urlparse, parse_qs

PORT = 8000
FETCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def extract_l_img(html):
    idx = html.find('<div class="l-img"')
    if idx == -1:
        idx = html.find("<div class='l-img'")
    if idx == -1:
        m = re.search(r'<div[^>]*class=(["\'])[^"\']*\bl-img\b[^"\']*\1[^>]*>', html, re.I)
        if not m:
            return ""
        idx = m.start()

    tag_end = html.find('>', idx)
    if tag_end == -1:
        return ""
    pos = tag_end + 1
    depth = 1

    while pos < len(html) and depth > 0:
        if html[pos:pos+4] == '<!--':
            end_idx = html.find('-->', pos+4)
            if end_idx > pos:
                pos = end_idx + 3
                continue

        lt = html.find('<', pos)
        if lt == -1:
            break

        if lt + 1 < len(html) and html[lt+1] == '/':
            gt = html.find('>', lt)
            if gt > lt:
                tag = html[lt+2:gt].strip().split()[0].lower() if gt > lt + 2 else ''
                if tag == 'div':
                    depth -= 1
                pos = gt + 1
                continue

        gt = html.find('>', lt)
        if gt > lt:
            inner = html[lt+1:gt].strip()
            tag_name = inner.split()[0].lower() if inner else ''
            if tag_name in ('script', 'style') and inner[-1] != '/':
                end_tag = f'</{tag_name}>'
                end_idx = html.find(end_tag, gt)
                if end_idx > gt:
                    pos = end_idx + len(end_tag)
                    continue
            if tag_name == 'div' and inner[-1] != '/':
                depth += 1
            pos = gt + 1

    return html[idx:pos]


def extract_styles(html):
    parts = []
    for m in re.finditer(r'<style[^>]*>.*?</style>', html, re.S | re.I):
        parts.append(m.group())
    for m in re.finditer(r'<link[^>]*rel=(["\'])stylesheet\1[^>]*>', html, re.S | re.I):
        parts.append(m.group())
    return '\n'.join(parts)


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == '/proxy' and 'id' in params:
            return self._proxy_template(params['id'][0])
        super().do_GET()

    def _proxy_template(self, tid):
        url = f"https://www.135editor.com/editor_styles/{tid}.html"
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": FETCH_HEADERS["User-Agent"],
                "Accept": FETCH_HEADERS["Accept"],
                "Accept-Language": FETCH_HEADERS["Accept-Language"],
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8', errors='replace')
        except urllib.request.HTTPError as e:
            self.send_error(e.code, f"135editor 返回错误 {e.code}")
            return
        except Exception as e:
            self.send_error(502, f"请求失败: {e}")
            return

        styles = extract_styles(html)
        l_img = extract_l_img(html)

        if not l_img:
            self.send_error(404, "未找到模板内容 (div.l-img)")
            return

        result = (
            '<!DOCTYPE html>\n<html><head><meta charset="utf-8">\n'
            f'<base href="https://www.135editor.com/">\n{styles}\n'
            '<style>body{text-align:center!important;margin:0;padding:10px}'
            '.l-img{display:inline-block!important;max-width:100%;margin:0 auto!important;float:none!important}'
            '.l-img img{max-width:100%!important;height:auto;display:block}</style>\n'
            f'</head><body>\n{l_img}\n</body></html>'
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(result.encode("utf-8"))

    def log_message(self, format, *args):
        msg = format % args
        if '/proxy?' in msg:
            print(f"[PROXY] {self.address_string()} - {msg}", flush=True)
        else:
            super().log_message(format, *args)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = http.server.HTTPServer(('0.0.0.0', PORT), ProxyHandler)
    print(f"  >>  135编辑器 模板代理服务器  <<")
    print(f"  启动于: http://localhost:{PORT}")
    print(f"  Ctrl+C 停止")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
