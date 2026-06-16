import re
import httpx
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# ================= 大模型万能通用跨域代理服务器 =================
app = FastAPI()

# 配置 CORS，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/proxy/{target_url:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def universal_proxy(request: Request, target_url: str):
    """万能代理核心逻辑：动态捕获任意路径并透传"""
    
    # 1. 修复由于 FastAPI 路径解析机制可能导致的双斜杠丢失问题
    # 例如：https:/opencode.ai/... 会被还原为 https://opencode.ai/...
    target_url = re.sub(r'^(https?:)/+(.*)$', r'\1//\2', target_url)
    
    # 2. 拼接客户端携带的 Query 参数 (例如 ?limit=10)
    if request.url.query:
        target_url += f"?{request.url.query}"

    # 3. 构造请求头，剔除会导致代理冲突的关键字段
    headers = dict(request.headers)
    headers.pop("host", None)           # 必须移除，由 httpx 自动计算目标域名的 Host
    headers.pop("content-length", None) # 必须移除，避免重新封包时长度不匹配
    headers.pop("origin", None)         # 建议移除，防止目标服务器启用严格的跨域来源校验
    headers.pop("referer", None)
    headers.pop("accept-encoding", None) # 必须移除，避免上游返回压缩内容在 stream 模式下解压异常

    # 4. 读取原始请求体数据 (不解析 JSON，实现纯粹的字节流透传)
    body = await request.body()

    # 5. 发起向真实 API Base URL 的代理请求
    client = httpx.AsyncClient(timeout=120.0)
    req = client.build_request(request.method, target_url, headers=headers, content=body)
    
    try:
        # stream=True 允许我们第一时间拿到响应头，而不用等大模型把话说完
        resp = await client.send(req, stream=True)
    except Exception as e:
        await client.aclose()
        return Response(content=f'{{"error": "Proxy Connection Error: {str(e)}"}}', status_code=502, media_type="application/json")

    # 6. 定义异步生成器，用于实时转发上游数据包
    async def stream_generator():
        try:
            async for chunk in resp.aiter_bytes():
                yield chunk
        finally:
            # 无论流式传输正常结束还是异常中断，确保释放连接资源
            await resp.aclose()
            await client.aclose()

    # 7. 透传目标服务器的核心响应头 (例如 Content-Type 是 text/event-stream 还是 application/json)
    response_headers = {}
    if "Content-Type" in resp.headers:
        response_headers["Content-Type"] = resp.headers["Content-Type"]

    return StreamingResponse(
        stream_generator(),
        status_code=resp.status_code,
        headers=response_headers
    )

if __name__ == "__main__":
    print("="*65)
    print(" 🚀 大模型万能通用跨域反向代理已启动")
    print(" 监听端口 : 8317")
    print(" 配置方式 : 在网页端 AI 设置中，将原来的真实 Base URL 替换为：")
    print("            http://localhost:8317/proxy/真实的Base_URL")
    print(" 示例地址 : http://localhost:8317/proxy/https://opencode.ai/zen/v1")
    print("="*65)
    uvicorn.run(app, host="0.0.0.0", port=8317, log_level="info")