# SiriBridge 🚀

**SiriBridge** 是为 [OpenClaw](https://github.com/openclaw/openclaw) 量身定制的轻量级 REST 桥接器。它让你的 iPhone Siri 能够直接与你的私有 AI 助手（Jarvis）进行原生语音对话。

> “嘿 Siri，问 Jarvis：今天有什么重要新闻？”

## ✨ 核心特性

- **原生语音交互**：无需打开 App，直接通过 Siri 呼唤。
- **极简部署**：支持 Docker 一键运行，适配 amd64/arm64 (Mac/Linux/树莓派)。
- **安全鉴权**：支持 `X-Bridge-Secret` 头部鉴权，保护你的 Token 额度。
- **智能熔断**：内置回复长度限制，防止 Siri 朗读“小作文”。
- **健康自测**：自带 `/health` 接口，一秒确认网关连接状态。

---

## 🛠 1. 快速部署 (Docker 模式)

如果你有 Docker，只需运行以下命令（请替换你的 Token）：

```bash
docker run -d \
  --name siribridge \
  -p 18888:18888 \
  -e SIRIBRIDGE_GATEWAY_TOKEN="你的_OPENCLAW_网关令牌" \
  -e SIRIBRIDGE_SECRET="自定义一个访问暗号" \
  -e GATEWAY_BASE_URL="http://你的网关IP:18789" \
  justlikemaki/siribridge:latest
```

> **如何获取 Token？**  
> 在 OpenClaw 终端执行：`openclaw config get gateway.auth.token`

---

## 📱 2. iPhone 快捷指令配置

这是最关键的一步，我们已经为你准备好了模板：

1.  **下载快捷指令**：[点击此处下载 SiriBridge 快捷指令模板](assets/SiriBridge.shortcut) (或使用 iCloud 共享链接)。
2.  **配置参数**：
    -   **URL**: `http://你的服务器IP:18888/ask`
    -   **X-Bridge-Secret**: 填入你在 Docker 命令中设置的“访问暗号”。
3.  **唤醒词**：默认快捷指令名为“问 Jarvis”，你可以改为任何你喜欢的词。

---

## 🔒 安全性建议

- **私有网络优先**：强烈建议配合 **Tailscale** 使用，将 `18888` 端口保留在私有网络中。
- **暗号保护**：务必设置 `SIRIBRIDGE_SECRET`，防止接口被公网扫描器滥用。

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源。

**Author**: Rick Sanchez (@orz225)
