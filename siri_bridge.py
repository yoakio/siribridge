import json
import logging
import time
import os
import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# 加载环境变量
load_dotenv()

# --- 1. 日志配置 ---
LOG_FILE = "siri_bridge.log"
handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[handler, logging.StreamHandler()]
)

# --- 2. 环境变量解耦 ---
GATEWAY_BASE_URL = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:18789")
GATEWAY_TOKEN = os.getenv("SIRIBRIDGE_GATEWAY_TOKEN")
BRIDGE_SECRET = os.getenv("SIRIBRIDGE_SECRET")  # 接口鉴权暗号
MODEL_NAME = os.getenv("SIRIBRIDGE_MODEL", "google-antigravity/gemini-3-flash")
MAX_REPLY_LENGTH = int(os.getenv("MAX_REPLY_LENGTH", 1500))
PORT = int(os.getenv("SIRIBRIDGE_PORT", 18888))

GATEWAY_API_URL = f"{GATEWAY_BASE_URL}/v1/chat/completions"

# --- 3. 全局状态与资源管理 ---
class AppState:
    http_client: httpx.AsyncClient = None

state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: 初始化异步客户端
    logging.info("Starting SiriBridge...")
    state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(90.0, connect=10.0),
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
    )
    
    # 启动前检查
    if not GATEWAY_TOKEN:
        logging.error("FATAL: SIRIBRIDGE_GATEWAY_TOKEN is not set!")
    if not BRIDGE_SECRET:
        logging.warning("SECURITY: SIRIBRIDGE_SECRET is not set! API is exposed.")
    
    yield
    
    # Shutdown: 优雅关闭客户端
    logging.info("Shutting down SiriBridge...")
    if state.http_client:
        await state.http_client.aclose()

app = FastAPI(lifespan=lifespan)

class Query(BaseModel):
    text: str

# --- 4. 安全锁：Header 鉴权中间件 ---
async def verify_secret(request: Request):
    if BRIDGE_SECRET:  # 只有在 .env 设置了暗号时才启用鉴权
        header_secret = request.headers.get("X-Bridge-Secret")
        if header_secret != BRIDGE_SECRET:
            logging.warning(f"Unauthorized access attempt from {request.client.host}")
            raise HTTPException(status_code=403, detail="Unauthorized: Invalid Secret Key")
    else:
        # 如果 .env 没设暗号，打印一条安全警告但放行
        # logging.warning("SECURITY WARNING: Running without SIRIBRIDGE_SECRET!")
        pass

# --- 5. 接口定义 ---

@app.get("/health")
async def health_check():
    """健康检查接口，用于 Docker 和监控"""
    status = {
        "status": "healthy",
        "timestamp": time.time(),
        "gateway_connected": False
    }
    # 尝试轻量级探测网关
    try:
        if state.http_client:
            # 仅检查网关端口是否存活
            response = await state.http_client.get(GATEWAY_BASE_URL, timeout=2.0)
            status["gateway_connected"] = (response.status_code < 500)
    except Exception:
        status["gateway_connected"] = False
    
    return status

@app.post("/ask", dependencies=[Depends(verify_secret)])
async def ask_jarvis(query: Query):
    start_time = time.time()
    logging.info(f"--- Request: {query.text} ---")
    
    if not GATEWAY_TOKEN:
        return {"reply": "错误：网关令牌未配置。"}
    
    if not state.http_client:
        return {"reply": "错误：内部客户端未就绪。"}

    headers = {
        "Authorization": f"Bearer {GATEWAY_TOKEN}",
        "Content-Type": "application/json",
        "x-openclaw-agent-id": "main"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你现在处于 Siri 语音场景。请回答简洁、自然，严禁使用 Markdown、表格、列表。"},
            {"role": "user", "content": query.text}
        ],
        "user": "siri-user"
    }
    
    try:
        response = await state.http_client.post(GATEWAY_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            try:
                reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            except (IndexError, AttributeError):
                logging.error(f"Invalid JSON: {data}")
                return {"reply": "错误：网关返回了异常的数据格式。"}

            if not reply:
                return {"reply": "Jarvis 似乎没有说话。"}
            
            # 熔断锁
            if len(reply) > MAX_REPLY_LENGTH:
                logging.warning("SAFETY: Reply truncated.")
                return {"reply": "Rick，回复太长已截断。请查看 Telegram。"}
            
            logging.info(f"Success! ({time.time()-start_time:.2f}s)")
            return {"reply": reply}
            
        elif response.status_code == 401:
            logging.error("Gateway 401: Unauthorized")
            return {"reply": "Jarvis 拒绝了我的访问请求，可能是令牌失效了。"}
        else:
            logging.error(f"Gateway Error {response.status_code}: {response.text}")
            return {"reply": f"Jarvis 响应异常，错误码 {response.status_code}。"}
            
    except httpx.TimeoutException:
        logging.error("Gateway Timeout")
        return {"reply": "抱歉，Jarvis 思考太久超时了，请稍后再试。"}
    except httpx.ConnectError:
        logging.error("Gateway Connection Error")
        return {"reply": "抱歉，我无法连接到主网关，请检查服务器状态。"}
    except Exception as e:
        logging.error(f"Bridge Unexpected Error: {str(e)}")
        return {"reply": "发生了意外错误，无法连接 Jarvis。"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
