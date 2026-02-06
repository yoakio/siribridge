# SiriBridge v3 Pro 升级记录与商业化架构白皮书 (2026-02-05)

本文档记录了 SiriBridge 从“自用工具”向“商业平台”跨越的关键技术突破。

---

## 🏗 一、 核心架构升级：混血云架构

为了实现外网无感接入（不挂 VPN）并保证金融级安全，系统已全面升级为以下架构：

1.  **逻辑核心 (Containerized Backend)**：
    *   `SiriBridge` 已迁移至 Docker 容器，实现环境隔离与快速部署。
    *   **改进**：修复了非 ASCII 编码（如框线符 `│`）导致的日志崩溃，增强了对“空语音”请求的容错。
2.  **安全屏障 (Zero Trust Gate)**：
    *   部署了 **Cloudflare Zero Trust** 物理隔绝。
    *   配置了 **Service Auth** 策略：只有持有特定“工牌” (Service Token) 的请求才能触达内网。
3.  **商业凭证网关 (Credential Gateway)**：
    *   部署了 **Cloudflare Worker** 代理层。
    *   **sk-key 系统**：用户只需持有简单的 `sk-rick-xxxx` 密钥，由网关自动完成复杂的 Token 注入。

---

## 📱 二、 快捷指令 (Shortcuts) v3 Pro 进化

这是目前为止最稳健、交互感最好的快捷指令逻辑：

### 1. 交互体验增强
*   **触感反馈**：在“听写”和“播报”环节增加了 **Haptic Feedback (轻触)**。
*   **连聊灵魂 (Recursive Loop)**：实现了基于递归的无限对话，无需重复喊唤醒词。
*   **自愈判断**：能够根据后端返回的 `continue: true/false` 自动决定是否续杯。

### 2. “魔术激活”逻辑 (Magic Link)
*   **零配置入驻**：支持通过 `shortcuts://` 协议接收配置。
*   **持久化存储**：配置自动解码并保存至 `iCloud Drive/Shortcuts/RickAI/config.json`，实现“一键安装，终身免设”。

---

## 🛠 三、 战地维修：已知坑位与对策

*   **1033 错误**：由于 macOS 对后台进程的限制，`cloudflared` 隧道容易掉线。**对策**：已上线 `self-healer.sh` 后台哨兵，实现秒级自动重启。
*   **变量类型误判**：快捷指令容易将 `continue: 1` 识别为文件。**对策**：在“如果”动作中强制将变量设为 **“布尔值”** 或 **“文本”** 类型。
*   **端口抢占**：废弃了旧的 macOS `LaunchAgent` 原生模式，统一使用 Docker。

---

## 🚀 四、 商业化路线图 (Next Steps)

1.  **[P0] 隧道守护**：将 `cloudflared` 封装为系统的 `plist` 守护进程，彻底根治掉线问题。
2.  **[P1] 一键分发**：优化 `/setup` 网页，实现“支付 -> 自动生成 Key -> 点击激活”的完整商业闭环。
3.  **[P2] 多模态视觉**：在快捷指令中加入“拍照”动作，打通 Jarvis 的视觉神经。

---
**核准人**：Rick Sanchez  
**总工程师**：Jarvis & Kiro (Claude 4.5)  
*记录于 2026-02-06 15:58*

---

## 🎖️ 十四、 2026-02-06 三级会员逻辑分流系统上线

1.  **架构层：智能路由 (Smart Routing)**：
    *   **实现**：SiriBridge 现在能根据用户的 `tier` 等级，自动选择不同的 AI 模型。
    *   **Pro**：对应 `Claude-4.5-Thinking` (Kiro)。
    *   **Standard**：对应 `Gemini-3-Flash`。
    *   **Free**：对应 OpenRouter 免费版（如 `Gemini-2.0-Flash-Lite:Free`）。
2.  **管理层：发码参数增强**：
    *   **升级**：`scripts/manage_users.py` 新增 `--tier` 参数。
    *   **用法**：`python manage_users.py create --name "VIP用户" --tier pro`。
3.  **网关层：元数据透传**：
    *   **升级**：Cloudflare Worker 现已支持透传 `X-User-Tier` 标头，实现全链路等级感知。

---

## ☁️ 十三、 2026-02-06 云端基础设施采购完成

1.  **资产登记：主力云服务器 (RackNerd)**：
    *   **配置**：2.5 GB RAM / 2 CPU / 45 GB SSD / 3TB Monthly Transfer / 1Gbps / 1 IPv4。
    *   **成本**：**$18.66 / 年**（终身续费同价）。
    *   **定位**：SiriBridge 企业级生产环境后端。
2.  **下一步计划**：
    *   **环境部署**：安装 Docker、Cloudflared 隧道及 OpenClaw 环境。
    *   **数据迁移**：同步本地 MacBook 的元数据、Key 数据库及个性化设置。
    *   **高可用联调**：配置 Cloudflare Worker 实现“云/端”自动故障切换。

---

## 🛡️ 十二、 2026-02-06 企业级安全沙箱与隐私屏蔽上线

1.  **隐私层：Rick 个人信息屏蔽**：
    *   **实现**：在 `/ask` 接口中加入了身份判定。
    *   **策略**：针对非 `sk-rick-master` 用户，自动注入严苛的 System Prompt，强制屏蔽 Rick Sanchez、宜阳等所有个人隐私信息。
2.  **安全层：指令沙箱化 (Prompt Sandboxing)**：
    *   **禁令**：显式禁止普通用户通过 Siri 使用文件工具读取 `/Users/am/.openclaw/` 或 `/Users/am/clawd/` 目录。
    *   **限制**：封锁了普通用户的 `exec` (shell 命令) 执行权限。
3.  **交互对齐**：
    *   优化了不同身份下的 System Rules。Rick 本人保留完整权限，外部用户进入受限沙箱模式。

---

## 🔒 十一、 2026-02-06 用户 Session 物理隔离功能上线

1.  **架构层：多租户隔离 (Multi-tenancy)**：
    *   **实现**：引入了基于哈希的 Session 映射逻辑。
    *   **逻辑**：系统自动将用户的 `sk-key` 通过 SHA-256 算法映射为唯一的 `session_id`。
    *   **Rick 特权**：主 Key `sk-rick-master` 被固定映射至 `siri-user-rick-master`。
2.  **存储层：独立记忆文件**：
    *   **效果**：每个用户在 OpenClaw 中拥有独立的记忆空间（`.jsonl` 文件）。
    *   **优势**：彻底解决了多人共用 Siri 时导致的隐私泄露与记忆混淆问题，支持各自独立的多轮对话。
3.  **技术对齐**：
    *   `SiriBridge` 已升级，调用网关时自动注入 `OpenClaw-Session-Key` 标头。

---

## 🏗️ 十、 2026-02-06 USDT 自动化支付系统启动

1.  **引导层：联系人更新**：
    *   **改进**：官网首页的“联系购买”按钮已指向新的 Telegram 账户：[`@notfoundTG`](https://t.me/notfoundTG)。
2.  **支付层：USDT (TRC-20) 监听架构**：
    *   **计划**：开发基于 TRON 网络接口的实时流水监听器。
    *   **逻辑**：通过识别转账金额微差或备注，实现 0 手续费、0 依赖的全球自动化发码。
    *   **状态**：监听脚本 `scripts/usdt_monitor.py` 框架搭建中，等待地址填入。

---

## ✨ 九、 2026-02-06 激活页面“身份感知”功能上线

1.  **网关层：元数据透传**：
    *   **改进**：Worker 在校验 `sk-key` 后，会将从 KV 中读取的 `name` 和 `expires_at` 通过自定义 Header (`X-User-Name`, `X-User-Expires`) 转发给后端。
2.  **展示层：个性化激活页**：
    *   **新增**：`/setup` 页面现在能动态显示用户的姓名和授权到期时间。
    *   **视觉**：增加了一个灰色的用户信息卡片，提升了产品的私密性与尊贵感。
3.  **技术对齐**：
    *   后端 `siri_bridge.py` 逻辑已适配，支持 Header 解码与日期格式化展示。

---

## 🛍️ 八、 2026-02-06 官网购买入口与交互优化

1.  **引导层：新增人工购买入口**：
    *   **改进**：在官网首页（/）Hero 区域新增了 **“联系 Rick 购买”** 高亮按钮。
    *   **链接**：直接跳转至 Rick 的 Telegram (`@orz225`)，支持人工发码测试。
    *   **分流**：将原有的“一键激活”移动为次级按钮，形成了“新用户购买 -> 老用户激活”的逻辑分流。
2.  **部署状态**：
    *   Docker 镜像已重构并重启，最新 UI 已上线。

---

## 🎨 七、 2026-02-06 产品首页 (Landing Page) 上线

1.  **展示层：官方首页 (/)**：
    *   **新增**：在 `siri_bridge.py` 中实现了根路由渲染。
    *   **视觉**：采用 Apple 风格的深色极简设计（Dark Mode），包含漂浮动画与渐变标题。
    *   **模块**：清晰展示了“大脑集成”、“安全架构”与“魔术激活”三大核心卖点。
2.  **引导层：全链路打通**：
    *   **逻辑**：首页直接关联 `/setup` 魔术激活页，形成了从“产品展示”到“一键安装”的闭环。
    *   **访问**：可通过 `https://siri-proxy.qybc.workers.dev/` 直接预览。

---

## 🚀 六、 2026-02-06 企业级用户管理系统上线

1.  **管理侧：自动化控制台 (manage_users.py)**：
    *   **新增**：编写了 `scripts/manage_users.py`。
    *   **能力**：支持一键创建用户、自动计算过期时间、实时同步至 Cloudflare KV。
    *   **用法**：`python3 scripts/manage_users.py create --name "客户名" --days 30`。
2.  **网关侧：智能判官 (Worker Index.js)**：
    *   **升级**：Worker 逻辑由简单的字符串比对升级为 **JSON 元数据校验**。
    *   **功能**：支持 **有效期检测**。如果用户密钥过期，Worker 会在入口处直接拦截并返回友好提示。
    *   **兼容性**：保留了对旧版 `active` 字符串的向后兼容，确保老用户不受影响。
3.  **安全侧：数据隔离**：
    *   实现了 `sk-key` (大门钥匙) 与 `internal-secret` (内部工牌) 的物理隔离。
    *   支持在云端后台实时注销特定 Key。

---

## 🛠 五、 2026-02-06 稳定性与自动化专项优化

1.  **传输层：隧道系统化 (LaunchAgent)**：
    *   **改进**：将 `cloudflared` 封装为 macOS `LaunchAgent` (`ai.cloudflare.siribridge.plist`)。
    *   **效果**：实现开机自启与崩溃秒级拉起，彻底消除 1033 手动重连痛点。
    *   **参数优化**：锁定 `protocol: http2` 并限制 `ha-connections: 2`，显著提升握手稳定性。
2.  **逻辑层：Docker 健壮性修复**：
    *   **改进**：重构 Dockerfile，注入 `curl` 依赖。
    *   **效果**：修复了容器因缺少工具导致的 `unhealthy` 虚假报警，目前状态为 `Healthy`。
3.  **配置层：密钥与端口规范化**：
    *   **动作**：统一后端端口为 `18888`，密钥回滚至昨晚稳定版 `jarvis-6g971e`。
    *   **文档**：同步更新 `MEMORY.md` 架构说明，确保“知行合一”。
