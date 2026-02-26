# AI 智能圆桌会议系统 - 全栈技术实施文档 (V2.0)

## 1. 系统架构演进

### 1.1 总体架构

系统由 V1.0 的 Client-Side SPA 升级为标准的 **B/S 分层架构**。采用前后端分离模式，前端负责交互与渲染，后端负责业务逻辑、数据存储及 LLM 接口的安全转发。

* **前端层 (Presentation Layer)**: 保持 Vue.js 3 + Tailwind CSS 的轻量化设计，但移除本地数据文件依赖，改为通过 RESTful API 与后端通讯。
* **网关层 (Gateway Layer)**: Nginx (可选) 反向代理，处理 SSL 终端和静态资源服务。
* **应用层 (Application Layer)**: Node.js (Express/NestJS) 提供 API 服务。核心模块包括：鉴权守卫、模型配置管理、人才库管理、会议状态流转、LLM 流式代理。
* **数据层 (Data Layer)**: 关系型数据库 (SQLite/PostgreSQL) 存储配置、角色数据及会议历史记录。

### 1.2 数据流向变更

* **配置加载**: 浏览器 `GET /api/config/models` -> 后端查询 DB -> 返回脱敏配置 (不含 Key)。
* **对话请求**: 浏览器 `POST /api/chat` (带 JWT) -> 后端校验 -> 后端读取真实 Key -> 请求 LLM 厂商 -> 流式回写 (Pipe) 至前端。
* **数据保存**: 浏览器 -> 后端 -> 数据库 (替代原有的 JSON 文件导出)。

---

## 2. 技术栈选型 (Tech Stack)

### 2.1 前端 (Frontend)

* **Core Framework**: Vue.js 3.x (Composition API 风格重构推荐，但兼容 Options API)。
* **UI Library**: Tailwind CSS v3.x。
* **HTTP Client**: Axios (替代原生 Fetch，便于处理 Interceptors 和 Token)。
* **Markdown Engine**: Marked.js + Highlight.js (代码高亮)。
* **State Management**: Pinia (推荐) 或继续使用 Vue Reactive。

### 2.2 后端 (Backend)

* **Runtime**: Node.js (LTS 版本 >= 18.x)。
* **Web Framework**: **Express.js** (轻量灵活) 或 **NestJS** (企业级规范，推荐团队开发使用)。本文档按 Express 编写以降低迁移复杂度。
* **ORM**: **Prisma** (推荐) 或 TypeORM。提供强类型的数据库操作体验。
* **Validation**: Zod (参数校验)。

### 2.3 数据库 (Database)

* **Type**: Relational Database (RDBMS)。
* **Engine**:
* 开发/中小型部署: **SQLite** (单文件，无需运维，性能足以支撑百人并发)。
* 生产/集群部署: **PostgreSQL**。


* **Rationale**: 结构化存储模型配置和角色数据，同时利用 JSON 字段存储复杂的 Prompt 和会议上下文。

---

## 3. 数据库设计 (Schema Design)

使用 Prisma Schema Language 描述数据模型。

### 3.1 核心模型

```prisma
// schema.prisma

// 1. 模型配置表 (原 api.js)
model LlmModel {
  id          Int      @id @default(autoincrement())
  platform    String   // 平台名称 (如: 硅基流动)
  provider    String   // 供应商标识 (如: siliconflow, deepseek)
  name        String   // 模型名称 (如: Qwen/Qwen2.5-72B)
  endpoint    String   // API Base URL
  apiKey      String   // 真实 Key (后端加密存储，前端不可见)
  remark      String?  // 备注
  isDefault   Boolean  @default(false)
  createdAt   DateTime @default(now())
  
  // 关联
  talents     Talent[]
}

// 2. 人才/角色库表 (原 talentPool.js)
model Talent {
  id          Int      @id @default(autoincrement())
  name        String
  prompt      String   @db.Text // System Prompt
  category    String?  // 归属部门
  avatar      String?  // 头像/颜色代码
  
  // 绑定模型 (可选，空则使用系统默认)
  modelId     Int?
  model       LlmModel? @relation(fields: [modelId], references: [id])
  
  createdAt   DateTime @default(now())
}

// 3. 会议记录表 (新功能: 持久化存储)
model Meeting {
  id          String   @id @default(uuid())
  topic       String
  startTime   DateTime @default(now())
  endTime     DateTime?
  status      String   // 'running', 'finished'
  
  // 存储 JSON 格式的完整对话日志
  // 结构: Array<{ role: string, content: string, round: number, time: string }>
  logs        String   @db.Text 
  
  // 存储 JSON 格式的背景材料
  materials   String?  @db.Text
  
  // 最终产出的 Markdown 纪要
  finalReport String?  @db.Text
}

// 4. 管理员表 (新功能: 系统安全)
model Admin {
  id       Int    @id @default(autoincrement())
  username String @unique
  password String // Bcrypt Hash
}

```

---

## 4. 后端 API 接口设计

所有接口位于 `/api/v1` 前缀下。

### 4.1 认证模块 (Auth)

* `POST /auth/login`: 传入用户名密码，返回 JWT Token。
* **Middleware**: `authMiddleware`，拦截所有非 GET 请求，验证 JWT。

### 4.2 配置管理 (Configuration)

* `GET /models`: 获取模型列表。**注意**：返回数据中 `apiKey` 字段应被脱敏（如替换为 `******`）。
* `POST /models`: 新增模型配置（加密存储 Key）。
* `PUT /models/:id`: 更新配置。
* `DELETE /models/:id`: 删除配置。

### 4.3 角色管理 (Talent)

* `GET /talents`: 获取角色列表（支持 query: `category`, `name`）。
* `POST /talents`: 创建新角色。
* `PUT /talents/:id`: 更新角色信息。

### 4.4 核心业务：LLM 代理 (Chat Proxy)

此接口替代前端直接调用 LLM 的逻辑，确保 Key 不泄露。

* **Endpoint**: `POST /chat/completions`
* **Headers**: `Authorization: Bearer <JWT_TOKEN>` (或前端专用 Access Token)
* **Body**:
```json
{
  "modelId": 1, // 前端仅传 ID，后端查库获取 Key
  "messages": [...],
  "stream": true
}

```


* **Implementation Logic (Express)**:
1. 校验 Token。
2. 根据 `modelId` 查询 `LlmModel` 表，解密获取 `apiKey` 和 `endpoint`。
3. 构建向 LLM 厂商的 Request。
4. 建立流式管道 (Pipeline)：`LLM Response Stream` -> `Express Response`。
5. (可选) 异步将对话记录写入 `Meeting` 数据库表用于审计。



### 4.5 会议管理 (Meeting)

* `POST /meetings/save`: 会议结束时，将前端的 `messages` 和 `finalReport` 上传存档。
* `GET /meetings`: 查看历史会议列表。
* `GET /meetings/:id`: 查看某场会议详情。

---

## 5. 前端重构指南

### 5.1 数据源改造

修改 `admin.html` 和 `AI智能圆桌会议系统.html` 中的 `onMounted` 逻辑。

* **移除**: `window.API_LIBRARY` 和 `window.TALENT_POOL` 的读取。
* **新增**: `api.js` 工具类（封装 Axios）。

```javascript
// src/utils/request.js (新建)
const apiClient = axios.create({
    baseURL: '/api/v1',
    timeout: 10000
});

// 在 main.js 或 HTML script 中引用
const fetchModels = async () => {
    const { data } = await apiClient.get('/models');
    // 注意：这里的 model.key 是脱敏的，仅用于 UI 显示"已配置"状态
    return data;
};

const fetchTalents = async () => {
    const { data } = await apiClient.get('/talents');
    return data;
};

```

### 5.2 对话调用改造

修改 `AI智能圆桌会议系统.html` 中的 `callLLMStream` 函数。

```javascript
const callLLMStream = async (sys, usr, onChunk, roleConfig) => {
    try {
        const response = await fetch('/api/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}` // 鉴权
            },
            body: JSON.stringify({
                modelId: roleConfig.modelId, // 传 ID 而不是 URL/Key
                messages: [
                    { role: 'system', content: sys },
                    { role: 'user', content: usr }
                ],
                stream: true
            })
        });
        
        // ... 原有的流式解码逻辑保持不变 (TextDecoder 读取 reader) ...
        
    } catch (e) {
        console.error("Backend Proxy Error", e);
    }
};

```

---

## 6. 安全实施细节

1. **API Key 存储安全**:
* 在数据库中存储 `apiKey` 时，建议使用 AES-256 进行对称加密。后端启动时通过环境变量 `APP_SECRET` 读取解密密钥。
* **原则**: 数据库即时被拖库，攻击者没有 `APP_SECRET` 也无法还原真实的 API Key。


2. **前端访问控制**:
* `admin.html` 页面加载时检查 `localStorage` 是否有 Token，无则跳转登录页。
* `meeting.html` 可以设计为开放或密码访问，根据 Token 限制是否允许调用 `/chat/completions` 接口。



---

## 7. 部署方案 (Deployment)

### 7.1 Docker 容器化

推荐使用 Docker Compose 一键拉起 "App + DB"。

**Dockerfile (Backend)**

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY prisma ./prisma/
RUN npx prisma generate
COPY . .
EXPOSE 3000
CMD ["npm", "start"]

```

**docker-compose.yml**

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=file:./dev.db
      - JWT_SECRET=change_me_in_prod
    volumes:
      - ./data:/app/prisma/data # 持久化 SQLite 文件

  frontend:
    image: nginx:alpine
    volumes:
      - ./frontend:/usr/share/nginx/html # 挂载 HTML 文件
      - ./nginx.conf:/etc/nginx/conf.d/default.conf # 反向代理配置
    ports:
      - "80:80"
    depends_on:
      - backend

```

### 7.2 Nginx 配置 (Proxy Pass)

前端通过 `/api` 访问后端，避免 CORS 问题。

```nginx
location /api/ {
    proxy_pass http://backend:3000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    
    # 关键：支持 SSE 流式响应
    proxy_buffering off;
    proxy_cache off;
    proxy_set_header Connection '';
    proxy_http_version 1.1;
    chunked_transfer_encoding off;
}

```

---

## 8. 开发路线图 (Roadmap)

1. **Phase 1 (后端基础)**: 搭建 Express + Prisma 环境，实现 Model/Talent 的 CRUD 接口。
2. **Phase 2 (代理联调)**: 实现 `/chat/completions` 代理接口，联调前端，确保流式输出正常。
3. **Phase 3 (前端适配)**: 移除 `window` 全局变量，接入 API，增加登录页。
4. **Phase 4 (持久化)**: 实现会议记录保存与回放功能。