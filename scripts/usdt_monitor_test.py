import asyncio
import httpx
import sys
import logging
import argparse
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# --- 配置区 ---
# 测试地址 (Rick 的 TRON 地址作为监听目标)
WATCH_ADDRESS = "TDUzF5BvXidqX78B6G71B7G81234567890" # 示例地址
# TRON API (使用 Trongrid 或类似公开接口)
# 这里为了演示方便，使用一个简化的接口逻辑。实际生产建议使用 Trongrid API Key。
TRONSCAN_API_URL = f"https://apilist.tronscan.org/api/transaction?sort=-timestamp&count=1&limit=20&address={WATCH_ADDRESS}"
USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

# SiriBridge 管理接口
PROVISION_URL = "http://localhost:18888/admin/provision"
ADMIN_TOKEN = "your_admin_token_here" # 脚本运行时需要确保环境中有这个或者手动填入

async def provision_key(tx_id: str, amount: str):
    """调用 SiriBridge 接口发放 Key"""
    logging.info(f"🚀 Detected payment! TX: {tx_id}, Amount: {amount} USDT")
    
    payload = {
        "name": f"USDT_User_{tx_id[:8]}",
        "days": 30,
        "admin_token": ADMIN_TOKEN
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # 兼容 SiriBridge 的 POST JSON 逻辑
            response = await client.post(PROVISION_URL, json=payload, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                logging.info(f"✅ Key Provisioned: {data.get('key')}")
                logging.info(f"🔗 Magic Link: {data.get('magic_link')}")
            else:
                logging.error(f"❌ Provision failed: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"❌ Error calling provision API: {e}")

async def monitor_loop():
    """轮询逻辑"""
    last_tx_id = None
    logging.info(f"👀 Monitoring TRON address: {WATCH_ADDRESS} for USDT transfers...")
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # 实际 API 调用逻辑 (以 Tronscan 为例)
                # 注意：实际使用时需要处理 USDT (TRC20) 的 transfer 逻辑，通常在 token_transfers 字段中
                response = await client.get(TRONSCAN_API_URL, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    # 假设我们只看第一条
                    transactions = data.get("data", [])
                    if transactions:
                        current_tx = transactions[0]
                        tx_id = current_tx.get("hash")
                        
                        # 简单的防重逻辑
                        if last_tx_id is None:
                            last_tx_id = tx_id
                            logging.info(f"Initialized. Latest TX: {tx_id}")
                        elif tx_id != last_tx_id:
                            last_tx_id = tx_id
                            # 这里应增加 USDT 合约校验和金额校验逻辑
                            await provision_key(tx_id, "Unknown (Check required)")
                
            except Exception as e:
                logging.error(f"Monitoring error: {e}")
            
            await asyncio.sleep(30) # 30秒轮询一次

async def simulate_payment():
    """模拟支付成功链路"""
    logging.info("🛠️ Running SIMULATION mode...")
    fake_tx_id = "simulated_" + str(int(time.time()))
    await provision_key(fake_tx_id, "10.0 (SIMULATED)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="USDT Payment Monitor for SiriBridge")
    parser.add_argument("--simulate", action="store_true", help="Simulate a payment success")
    parser.add_argument("--token", type=str, help="Admin token for provision API")
    
    args = parser.parse_args()
    
    if args.token:
        ADMIN_TOKEN = args.token

    if args.simulate:
        asyncio.run(simulate_payment())
    else:
        try:
            asyncio.run(monitor_loop())
        except KeyboardInterrupt:
            logging.info("Stopped by user.")
