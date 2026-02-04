# SiriBridge 🚀：把你的 Siri “换脑”成真正的 Jarvis

[English](#english) | [中文说明](#chinese)

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

### 🛠 System Architecture
1. **Frontend**: iOS Shortcuts handles "Speech-to-Text" and "Text-to-Speech".
2. **Bridge**: SiriBridge (FastAPI) converts Shortcut JSON payloads into OpenClaw compatible API calls.
3. **Backend**: OpenClaw Gateway manages model routing and agent logic.

### 🚀 1. Quick Start (Docker)
The easiest way to deploy is using our multi-arch Docker image (supports amd64/arm64):

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

### 📱 2. iOS Shortcut Configuration
We provide two versions of shortcuts (functionally identical, only the trigger phrase differs):

1. **Chinese (Recommended)**: [问贾维斯.shortcut](assets/问贾维斯.shortcut) — Trigger: "Hey Siri, **问贾维斯**".
2. **English**: [Ask_Jarvis.shortcut](assets/Ask_Jarvis.shortcut) — Trigger: "Hey Siri, **Ask Jarvis**".

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

### 📦 二、 部署 SiriBridge (Docker 模式)

在你的服务器或本地电脑运行以下命令：

```bash
docker run -d \
  --name siribridge \
  -p 18888:18888 \
  --restart always \
  -e SIRIBRIDGE_GATEWAY_TOKEN="填写你的OpenClaw令牌" \
  -e SIRIBRIDGE_SECRET="自定义一个访问暗号" \
  -e GATEWAY_BASE_URL="http://你的网关IP:18789" \
  yoakio/siribridge:latest
```

---

### 📱 三、 iPhone 快捷指令配置 (关键步骤)

连接你和 AI 的最后一步：

1.  **导入模板**：下载 [问贾维斯.shortcut](assets/问贾维斯.shortcut) 或 [Ask_Jarvis.shortcut](assets/Ask_Jarvis.shortcut) 并导入。
2.  **配置 URL**：找到“获取 URL 内容”动作，改为：`http://[你的服务器IP]:18888/ask`。
3.  **配置鉴权**：在“头部”添加 `X-Bridge-Secret`，值为你在 Docker 命令中设置的暗号。
4.  **配置请求体**：确保方法为 **POST**，格式为 **JSON**，包含 `text` 字段并关联到“听写的文本”。

---

### 🛡️ 四、 进阶：极致的安全与隐私 (Tailscale)

强烈建议不要将 `18888` 端口暴露在公网。
*   **最佳实践**：在服务器和 iPhone 上同时开启 **Tailscale**。
*   将快捷指令中的 URL 改为服务器的 **Tailscale 内网 IP**。
*   这样即使在 5G 户外，你的数据也通过加密隧道传输，且公网黑客完全无法发现你的接口。

---

### ❓ 五、 常见问题排查 (Troubleshooting)

*   **Siri 报错“无法连接”**：检查服务器防火墙是否放行了 `18888` 端口；检查 Tailscale 是否处于 Connected 状态。
*   **gateway_connected 为 false**：说明 SiriBridge 连不上 OpenClaw。请确保 Docker 启动命令中的 `GATEWAY_BASE_URL` 使用的是宿主机的内网 IP，而非 `127.0.0.1`。
*   **Siri 朗读太长**：SiriBridge 默认开启了 1500 字熔断保护，防止 Siri 变成“碎碎念”。

---

## 📄 LICENSE
[MIT License](LICENSE)

**Author**: Rick Sanchez  
**X (Twitter)**: [@QingBu9342](https://x.com/QingBu9342)  
**OpenClaw**: [Join Community](https://github.com/openclaw/openclaw)
