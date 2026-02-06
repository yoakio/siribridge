# SiriBridge 🚀：把你的 Siri “换脑”成真正的 Jarvis

<p align="center">
  <img src="assets/logo.svg" width="300" alt="SiriBridge Logo">
</p>
[中文说明](#chinese) | [English](#english)

---

<a name="chinese"></a>
## 中文说明

**SiriBridge** 是一个专门为 [OpenClaw](https://github.com/openclaw/openclaw) 设计的高性能轻量级 REST 桥接器。它彻底解决了原生 Siri “智商不足”的问题，通过将语音输入实时转发至你的私有 AI Agent（如 Claude 4.5、DeepSeek-V3），让你的 iPhone 拥有真正的“贾维斯”级大脑。

### ✨ 核心亮点：为什么选择它？
*   **智商降维打击**：不再听到“我在网上为你搜到了...”，而是听到逻辑严密的深度分析。
*   **原生交互**：无需打开 App，利用系统自带的“听写”与“朗读”能力，体验丝滑。
*   **极简部署**：一行 Docker 命令搞定，适配 VPS、Mac、树莓派、NAS。
*   **安全可控**：支持 Header 鉴权，建议配合 Tailscale 实现全链路内网加密，隐私 0 风险。

---

### 🛠 一、 准备工作

1.  **安装 OpenClaw**：确保你的 OpenClaw 网关正在运行。
2.  **获取 Token**：在 OpenClaw 终端执行以下命令获取你的网关令牌：
    ```bash
    openclaw config get gateway.auth.token
    ```
3.  **确定网关地址**：记下你运行 OpenClaw 的机器 IP（建议使用 Tailscale IP，例如 `100.x.x.x`）。

---

### 📦 二、 部署架构 (Current Architecture)

目前项目采用 **Docker 隔离 + macOS 原生隧道** 的混血架构运行：

1.  **逻辑层 (Docker)**：
    *   **容器名**：`siribridge`
    *   **运行命令**：`docker compose up -d`
    *   **端口映射**：`18888:18888`
    *   **配置文件**：`.env` (包含网关 Token 和访问密钥)
2.  **传输层 (Cloudflare Tunnel)**：
    *   **进程**：macOS 原生 `cloudflared` 进程。
    *   **隧道名**：`siribridge`
    *   **公网域名**：`https://siri.961213.xyz`
    *   **转发逻辑**：外网 HTTPS -> 本地 18888 端口。

---

### ⚠️ 维护笔记 (Maintenance Notes)

*   **避坑指南**：项目历史上曾尝试过 macOS 原生 `LaunchAgent` 部署（`ai.openclaw.siribridge.plist`）。**请注意**：目前已全面转向 Docker，若需修改代码或重启服务，请仅操作 Docker 容器。严禁同时启动原生进程，否则会导致 18888 端口冲突。
*   **清理指令**：若发现端口被占用，请执行 `launchctl unload ~/Library/LaunchAgents/ai.openclaw.siribridge.plist`。

---

### 📱 三、 iPhone 快捷指令配置 (关键步骤)

连接你和 AI 的最后一步：

1.  **导入模板**：我们为你准备了两个版本的快捷指令（功能一致，仅唤醒词不同）：
    *   **中文版 (推荐)**：[问贾维斯.shortcut](assets/问贾维斯.shortcut) —— 唤醒词：“嘿 Siri，**问贾维斯**”。
    *   **英文版**：[Ask_Jarvis.shortcut](assets/Ask_Jarvis.shortcut) —— 唤醒词：“Hey Siri, **Ask Jarvis**”。
2.  **配置 URL**：找到“获取 URL 内容”动作，改为：`http://[你的服务器IP]:18888/ask`。
3.  **配置鉴权**：在“头部”添加 `X-Bridge-Secret`，值为你在 Docker 命令中设置的暗号。

---

### ⚡️ 四、 进阶：如何更优雅地召唤 Jarvis？

除了喊“嘿 Siri”，你还可以用以下几种更硬核的方式触发：

*   **敲击手机背面 (推荐)**：
    -   进入 iPhone `设置` -> `辅助功能` -> `触控` -> `轻点背面`。
    -   选择 `轻点两下` 或 `轻点三下`，勾选 **“问贾维斯”**。
    -   *现在，只需帅气地敲两下手机，Jarvis 就会立刻听令。*
*   **Apple Watch 随身调遣**：
    -   在 Apple Watch 上打开“快捷指令”App 即可直接点击调用。
    -   建议将指令添加到 **表盘复杂功能**，实现抬手即问。
*   **Action Button (iPhone 15 Pro 及以上)**：
    -   在 `设置` -> `操作按钮` 中绑定 **“问贾维斯”**，实现实体按键一键召唤。

---

### 🛡️ 五、 进阶：极致的安全与隐私 (Tailscale)

强烈建议不要将 `18888` 端口暴露在公网。
*   **最佳实践**：在服务器和 iPhone 上同时开启 **Tailscale**。
*   将快捷指令中的 URL 改为服务器的 **Tailscale 内网 IP**。
*   这样即使在 5G 户外，你的数据也通过加密隧道传输，且公网黑客完全无法发现你的接口。

---

### ❓ 六、 常见问题排查 (Troubleshooting)

*   **Siri 报错“无法连接”**：检查服务器防火墙是否放行了 `18888` 端口；检查 Tailscale 是否处于 Connected 状态。
*   **gateway_connected 为 false**：说明 SiriBridge 连不上 OpenClaw。请确保 Docker 启动命令中的 `GATEWAY_BASE_URL` 使用的是宿主机的内网 IP，而非 `127.0.0.1`。
*   **Siri 朗读太长**：SiriBridge 默认开启了 1500 字熔断保护，防止 Siri 变成“碎碎念”。

---

<a name="english"></a>
## English

**SiriBridge** is a high-performance, lightweight REST bridge designed to connect Apple Siri with [OpenClaw](https://github.com/openclaw/openclaw). It bypasses the limitations of native Siri by routing voice inputs to your private AI agents (powered by Claude 4.5, DeepSeek, etc.) and reading back the intelligent responses natively on your iPhone.

### 🧠 Why SiriBridge?
Native Siri is often limited to simple tasks or web searches. SiriBridge gives it a "brain transplant":
- **Complex Reasoning**: Ask complicated logic or coding questions.
- **Private Knowledge**: Connect to your own local data via OpenClaw.
- **Extreme Speed**: Millisecond-level processing and response.
- **Privacy First**: Your data stays in your control.

### 🚀 Quick Start (Docker)
```bash
docker run -d \
  --name siribridge \
  -p 18888:18888 \
  --restart always \
  -e SIRIBRIDGE_GATEWAY_TOKEN="YOUR_OPENCLAW_TOKEN" \
  -e GATEWAY_BASE_URL="http://YOUR_GATEWAY_IP:18789" \
  -e SIRIBRIDGE_SECRET="YOUR_CUSTOM_SECRET" \
  yoakio/siribridge:latest
```

### 📱 iOS Shortcut Configuration
1. **Download**: [问贾维斯.shortcut](assets/问贾维斯.shortcut) or [Ask_Jarvis.shortcut](assets/Ask_Jarvis.shortcut).
2. **Setup**: Point the API URL to `http://YOUR_SERVER_IP:18888/ask`.
3. **Auth**: Add `X-Bridge-Secret` header if configured.

---

## 📄 LICENSE
[MIT License](LICENSE)

**Author**: Rick Sanchez  
**X (Twitter)**: [@QingBu9342](https://x.com/QingBu9342)  
**OpenClaw**: [Join Community](https://github.com/openclaw/openclaw)http://100.69.248.10:18888/health
