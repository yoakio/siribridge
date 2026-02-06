import json
import logging
import time
import os
import httpx
import base64
import secrets
import string
import hashlib
from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from urllib.parse import unquote, quote

# 加载环境变量
load_dotenv()

# --- 1. 日志配置 ---
LOG_FILE = "siri_bridge.log"
handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[handler, logging.StreamHandler()]
)

# --- 2. 环境变量解耦 ---
GATEWAY_BASE_URL = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:18789")
GATEWAY_TOKEN = os.getenv("SIRIBRIDGE_GATEWAY_TOKEN")
BRIDGE_SECRET = os.getenv("SIRIBRIDGE_SECRET")  # 接口鉴权暗号
MAX_REPLY_LENGTH = int(os.getenv("MAX_REPLY_LENGTH", 1500))
PORT = int(os.getenv("SIRIBRIDGE_PORT", 18888))
WORKER_URL = os.getenv("SIRIBRIDGE_WORKER_URL", "https://siri-proxy.qybc.workers.dev")

# --- 2.1 默认模型路由 (AIClient2API 架构) ---
TIER_MODELS = {
    "pro": "openai/claude-4-5-thinking",
    "standard": "openai/gemini-3-flash",
    "free": "openrouter/google/gemini-2.0-flash-lite:free" # 兜底免费模型
}
DEFAULT_MODEL = TIER_MODELS["standard"]

# --- 2.2 企业级管理变量 ---
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_API_TOKEN = os.getenv("CF_API_TOKEN")
CF_KV_NAMESPACE_ID = os.getenv("CF_KV_NAMESPACE_ID", "8f64b8d609dc41a6ae89afa06908c859")

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
        timeout=httpx.Timeout(120.0, connect=10.0),
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
    )
    
    # 启动前检查
    if not GATEWAY_TOKEN:
        logging.error("FATAL: SIRIBRIDGE_GATEWAY_TOKEN is not set!")
    if not BRIDGE_SECRET:
        logging.warning("SECURITY: SIRIBRIDGE_SECRET is not set! API is exposed.")
    if not CF_API_TOKEN:
        logging.warning("PROVISIONING: CF_API_TOKEN is not set. Admin features will fail.")
    
    yield
    
    # Shutdown: 优雅关闭客户端
    logging.info("Shutting down SiriBridge...")
    if state.http_client:
        await state.http_client.aclose()

app = FastAPI(lifespan=lifespan)

class Query(BaseModel):
    text: str

class ProvisionRequest(BaseModel):
    name: str
    days: int = 30
    quota: int = 50
    admin_token: str

# --- 4. 辅助函数 ---

async def update_usage(user_key: str, metadata: dict):
    """异步更新 Cloudflare KV 中的使用量"""
    metadata["usage"] = metadata.get("usage", 0) + 1
    cf_url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{CF_KV_NAMESPACE_ID}/values/{user_key}"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.put(cf_url, content=json.dumps(metadata), headers=headers)
            resp.raise_for_status()
            logging.info(f"Usage updated for {user_key}: {metadata['usage']}")
    except Exception as e:
        logging.error(f"Failed to update usage for {user_key}: {e}")

# --- 5. 安全锁：Header 鉴权中间件 ---
async def verify_secret(request: Request):
    if BRIDGE_SECRET:  # 只有在 .env 设置了暗号时才启用鉴权
        header_secret = request.headers.get("X-Bridge-Secret")
        if header_secret != BRIDGE_SECRET:
            logging.warning(f"Unauthorized access attempt from {request.client.host}")
            raise HTTPException(status_code=403, detail="Unauthorized: Invalid Secret Key")

async def verify_admin(admin_token: str):
    if not ADMIN_TOKEN or admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Admin Token")

# --- 6. 接口定义 ---

@app.get("/", response_class=FileResponse)
async def landing_page():
    """产品官方首页 (Landing Page)"""
    return "templates/index.html"

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

@app.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request, key: str = "sk-rick-master"):
    """为用户生成一键安装页面"""
    shortcut_name = "问贾维斯"  # 必须与用户手机上的快捷指令名称完全一致
    
    # 从 Header 中提取由 Worker 传过来的元数据
    user_name = unquote(request.headers.get("X-User-Name", "尊敬的用户"))
    expires_at = request.headers.get("X-User-Expires", "永久有效")
    
    # 格式化日期 (如果是 ISO 格式)
    if expires_at != "永久有效":
        try:
            dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            expires_at = dt.strftime("%Y-%m-%d %H:%M")
        except:
            pass

    # 构造要注入的配置数据
    config_data = {
        "url": f"{WORKER_URL}/ask",
        "key": key
    }
    
    # 转为 JSON 并进行 Base64 编码，防止 URL 乱码
    config_str = json.dumps(config_data)
    encoded_config = base64.b64encode(config_str.encode()).decode()
    
    # 构造魔术链接 (URL 编码处理以兼容更多浏览器)
    magic_link = f"shortcuts://run-shortcut?name={quote(shortcut_name)}&input={quote(encoded_config)}"
    
    # 读取模板并渲染
    try:
        with open("templates/setup.html", "r", encoding="utf-8") as f:
            template = f.read()
        
        content = template.replace("{{ user_name }}", user_name)                           .replace("{{ expires_at }}", expires_at)                           .replace("{{ magic_link }}", magic_link)
        return content
    except Exception as e:
        logging.error(f"Template error: {e}")
        return f"Setup error: {str(e)}"

# --- 7. 企业级管理接口 (Admin) ---

@app.api_route("/admin/provision", methods=["GET", "POST"])
async def provision_user(
    request: Request,
    name: Optional[str] = None, 
    days: int = 30, 
    quota: int = 50,
    admin_token: Optional[str] = None
):
    """
    自动化发码接口：支持 POST JSON 或 GET Query
    """
    # 尝试从 POST JSON 中读取 (如果存在)
    if request.method == "POST":
        try:
            body = await request.json()
            name = body.get("name", name)
            days = int(body.get("days", days))
            quota = int(body.get("quota", quota))
            admin_token = body.get("admin_token", admin_token)
        except Exception:
            pass # 降级使用 Query 参数

    if not admin_token or admin_token != ADMIN_TOKEN:
        logging.warning(f"Provision failed: Invalid admin token. Provided: {admin_token}")
        raise HTTPException(status_code=401, detail="Invalid Admin Token")
    
    if not name:
        raise HTTPException(status_code=400, detail="Missing parameter: name")

    if not CF_API_TOKEN or not CF_ACCOUNT_ID:
        logging.error("PROVISION: Cloudflare credentials missing in .env")
        raise HTTPException(status_code=500, detail="Cloudflare API not configured on backend")

    # 1. 生成随机 Key
    new_key = "sk-rick-" + "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(16))
    
    # 2. 计算过期时间
    expire_date = datetime.now(timezone.utc) + timedelta(days=days)
    metadata = {
        "name": name,
        "status": "active",
        "tier": "standard", # 自动化接口默认设为标准版
        "usage": 0,
        "quota": quota,
        "expires_at": expire_date.isoformat().replace("+00:00", "Z"),
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }

    # 3. 同步至 Cloudflare KV
    cf_url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{CF_KV_NAMESPACE_ID}/values/{new_key}"
    
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.put(cf_url, content=json.dumps(metadata), headers=headers)
            resp.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to sync to Cloudflare: {e}")
        raise HTTPException(status_code=500, detail=f"Cloudflare Sync Failed: {str(e)}")

    return {
        "status": "success",
        "key": new_key,
        "quota": quota,
        "expires_at": metadata["expires_at"],
        "magic_link": f"{WORKER_URL}/setup?key={new_key}"
    }

@app.post("/ask", dependencies=[Depends(verify_secret)])
async def ask_jarvis(query: Query, request: Request, background_tasks: BackgroundTasks):
    start_time = time.time()
    
    # 预检：如果用户没说话，直接打回
    if not query.text or not query.text.strip():
        logging.info("--- Request: [Empty] ---")
        return {"reply": "我没听清你说什么，请再说一次。", "continue": 1}
    
    # 1. 提取用户身份并隔离 Session
    auth_header = request.headers.get("Authorization", "Bearer anonymous")
    user_token = auth_header.replace("Bearer ", "").strip()
    user_tier = request.headers.get("X-User-Tier", "standard").lower()
    
    is_master = (user_token == "sk-rick-master")
    
    # 2. 用量限额检查
    user_metadata = {}
    if not is_master:
        cf_get_url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{CF_KV_NAMESPACE_ID}/values/{user_token}"
        headers = {"Authorization": f"Bearer {CF_API_TOKEN}"}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(cf_get_url, headers=headers)
                if resp.status_code == 200:
                    user_metadata = resp.json()
                    usage = user_metadata.get("usage", 0)
                    quota = user_metadata.get("quota", 50)
                    if usage >= quota:
                        logging.info(f"Quota exceeded for {user_token} ({usage}/{quota})")
                        return {"reply": "您的配额已用完，请联系 @notfoundTG 续费。", "continue": False}
                else:
                    logging.warning(f"Failed to fetch metadata for {user_token}: {resp.status_code}")
        except Exception as e:
            logging.error(f"Error checking quota for {user_token}: {e}")

    # 3. 模型选择与 Session 隔离
    selected_model = TIER_MODELS.get(user_tier, DEFAULT_MODEL)
    if is_master: selected_model = TIER_MODELS["pro"]

    if is_master:
        # Rick 本人：使用固定且可识别的 Session ID
        session_id = "siri-user-rick-master"
        system_rules = "你现在处于 Siri 语音场景。请回答简洁、自然，严禁使用 Markdown、表格、列表。如果你有后续问题或认为对话应继续，请在回复末尾加上 [CONTINUE] 标记。"
    else:
        # 普通用户：对 Key 进行哈希，确保隐私的同时实现物理隔离
        user_hash = hashlib.sha256(user_token.encode()).hexdigest()[:12]
        session_id = f"siri-user-{user_hash}"
        # 企业级沙箱约束：屏蔽 Rick 个人信息，禁止访问敏感目录
        system_rules = (
            "你现在处于 Siri 语音场景。你是一位专业、简洁的 AI 助手。"
            "【安全沙箱约束】：\n"
            "1. 你严禁提及任何关于 'Rick Sanchez'、'qybc' 或 '宜阳' 的个人信息。如果被问及你是谁的助手，请回答：'我是您的专属 AI 助手'。\n"
            "2. 严禁使用任何文件管理工具读取或列出系统目录（特别是 /Users/am/.openclaw/ 或 /Users/am/clawd/）。\n"
            "3. 严禁执行 shell 命令 (exec) 或修改系统配置。\n"
            "4. 回答必须简洁，严禁使用 Markdown、表格、列表。对话结束请保持安静。"
        )

    logging.info(f"--- Request from [{session_id}]: {query.text} ---")
    
    if not GATEWAY_TOKEN:
        return {"reply": "错误：网关令牌未配置。"}
    
    if not state.http_client:
        return {"reply": "错误：内部客户端未就绪。"}

    headers = {
        "Authorization": f"Bearer {GATEWAY_TOKEN}",
        "Content-Type": "application/json",
        "x-openclaw-agent-id": "main",
        "OpenClaw-Session-Key": session_id
    }
    
    payload = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": system_rules},
            {"role": "user", "content": query.text}
        ],
        "user": session_id
    }
    
    # 物理沙箱：非 Rick 用户从物理上切断工具调用能力
    if not is_master:
        payload["tools"] = []
    
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
            
            # 检测连续对话标记
            should_continue = "[CONTINUE]" in reply
            reply = reply.replace("[CONTINUE]", "").strip()

            # 熔断锁
            if len(reply) > MAX_REPLY_LENGTH:
                logging.warning("SAFETY: Reply truncated.")
                return {"reply": "Rick，回复太长已截断。请查看 Telegram。"}
            
            # 异步计费
            if not is_master and user_metadata:
                background_tasks.add_task(update_usage, user_token, user_metadata)

            logging.info(f"Success! ({time.time()-start_time:.2f}s) - Continue: {should_continue}")
            return {"reply": reply, "continue": should_continue}
            
        elif response.status_code == 401:
            logging.error("Gateway 401: Unauthorized")
            return {"reply": "Jarvis 拒绝了我的访问请求，可能是令牌失效了。"}
        else:
            logging.error(f"Gateway Error {response.status_code}: {repr(response.text)}")
            return {"reply": f"Jarvis 响应异常，错误码 {response.status_code}。"}
            
    except httpx.TimeoutException:
        logging.error("Gateway Timeout")
        return {"reply": "抱歉，Jarvis 思考太久超时了，请稍后再试。"}
    except httpx.ConnectError:
        logging.error("Gateway Connection Error")
        return {"reply": "抱歉，我无法连接到主网关，请检查服务器状态。"}
    except Exception as e:
        logging.error(f"Bridge Unexpected Error: {repr(e)}")
        return {"reply": "发生了意外错误，无法连接 Jarvis。"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
