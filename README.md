# SiriBridge 🚀

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English

**SiriBridge** is a lightweight REST bridge specifically designed for [OpenClaw](https://github.com/openclaw/openclaw). It enables your iPhone Siri to talk directly with your private AI assistant (Jarvis) using native voice interactions.

> "Hey Siri, ask Jarvis: What's the latest tech news for today?"

### ✨ Key Features
- **Native Voice Interaction**: No app needed, just use Siri.
- **Ultra-Lightweight**: Docker-ready, supports amd64/arm64 (Mac/Linux/Raspberry Pi).
- **Secure**: Supports `X-Bridge-Secret` header authentication to protect your token.
- **Smart Truncation**: Built-in reply length limit to keep Siri's responses concise.
- **Health Check**: `/health` endpoint included for easy gateway connectivity testing.

### 🛠 Quick Start (Docker)
Run the following command (replace with your own token and secret):
```bash
docker run -d \
  --name siribridge \
  -p 18888:18888 \
  -e SIRIBRIDGE_GATEWAY_TOKEN="YOUR_OPENCLAW_TOKEN" \
  -e SIRIBRIDGE_SECRET="YOUR_CUSTOM_SECRET" \
  -e GATEWAY_BASE_URL="http://YOUR_GATEWAY_IP:18789" \
  justlikemaki/siribridge:latest
```

---

<a name="chinese"></a>
## 中文

**SiriBridge** 是为 [OpenClaw](https://github.com/openclaw/openclaw) 量身定制的轻量级 REST 桥接器。它让你的 iPhone Siri 能够直接与你的私有 AI 助手（Jarvis）进行原生语音对话。

> “嘿 Siri，问 Jarvis：今天有什么重要新闻？”

### ✨ 核心特性
- **原生语音交互**：无需打开 App，直接通过 Siri 呼唤。
- **极简部署**：支持 Docker 一键运行，适配 amd64/arm64 (Mac/Linux/树莓派)。
- **安全鉴权**：支持 `X-Bridge-Secret` 头部鉴权，保护你的 Token 额度。
- **智能熔断**：内置回复长度限制，防止 Siri 朗读“小作文”。
- **健康自测**：自带 `/health` 接口，一秒确认网关连接状态。

### 🛠 1. 快速部署 (Docker 模式)
如果你有 Docker，只需运行以下命令：
```bash
docker run -d \
  --name siribridge \
  -p 18888:18888 \
  -e SIRIBRIDGE_GATEWAY_TOKEN="你的_OPENCLAW_网关令牌" \
  -e SIRIBRIDGE_SECRET="自定义一个访问暗号" \
  -e GATEWAY_BASE_URL="http://你的网关IP:18789" \
  justlikemaki/siribridge:latest
```

### 📱 2. iPhone 快捷指令配置
1.  **下载模板**：[点击此处下载 SiriBridge.shortcut](assets/SiriBridge.shortcut)。
2.  **配置参数**：
    -   **URL**: `http://你的服务器IP:18888/ask`
    -   **X-Bridge-Secret**: 填入你在 Docker 命令中设置的“访问暗号”。
3.  **唤醒词**：默认快捷指令名为“问 Jarvis”，你可以改为任何你喜欢的词。

---

## 📄 LICENSE
[MIT License](LICENSE)

**Author**: Rick Sanchez (@orz225)
