const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
// 数据库固定保存在当前目录下的 diary.db
const DB_FILE = path.join(__dirname, 'diary.db');

const server = http.createServer((req, res) => {
    // 1. 专门处理前端发来的“保存数据库”请求
    if (req.method === 'POST' && req.url === '/api/save') {
        let body = [];
        req.on('data', chunk => {
            body.push(chunk); // 接收二进制数据块
        });
        req.on('end', () => {
            const buffer = Buffer.concat(body);
            // 直接将收到的二进制流覆盖写入本地 diary.db
            fs.writeFile(DB_FILE, buffer, (err) => {
                if (err) {
                    res.writeHead(500, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ success: false, error: err.message }));
                } else {
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ success: true }));
                }
            });
        });
        return;
    }

    // 2. 处理常规的静态文件请求 (HTML, JS, CSS, 还有初始加载的 DB 文件)
    if (req.method === 'GET') {
        let filePath = path.join(__dirname, req.url === '/' ? 'index.html' : req.url);
        let extname = String(path.extname(filePath)).toLowerCase();
        
        const mimeTypes = {
            '.html': 'text/html; charset=utf-8',
            '.js': 'text/javascript',
            '.css': 'text/css',
            '.db': 'application/octet-stream' // 数据库文件
        };

        let contentType = mimeTypes[extname] || 'application/octet-stream';

        fs.readFile(filePath, (error, content) => {
            if (error) {
                if (error.code === 'ENOENT') {
                    // 如果文件不存在（比如第一次运行还没有 diary.db），返回 404，让前端自己新建
                    res.writeHead(404);
                    res.end('Not Found');
                } else {
                    res.writeHead(500);
                    res.end('服务器错误: ' + error.code);
                }
            } else {
                res.writeHead(200, { 'Content-Type': contentType });
                res.end(content);
            }
        });
    }
});

server.listen(PORT, () => {
    console.log(`\n🚀 终极完美版服务器已启动!`);
    console.log(`🌐 请在浏览器打开: http://localhost:${PORT}`);
    console.log(`📂 数据将静默保存在当前目录的: diary.db 中\n`);
});