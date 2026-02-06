# SiriBridge 优化与功能增强路线图 (Roadmap)

本文档是 SiriBridge 项目的唯一官方开发蓝本，记录了 Rick 与 Jarvis 关于将 Siri 打造为真正的 **Agentic AI 具身终端** 的全盘设想。

---

## 零、 产品定性与策略 (Product Strategy)

- **核心路线**：坚持 **SiriBridge (中间桥接层)** 方案，不开发独立 App。
- **价值主张**：利用 iOS 原生 Siri 实现最低摩擦感的交互；通过桥接层绕过 iOS 沙盒限制，实现对后端（Linux/macOS）资源的深度调度；开发性价比最高。

---

## 一、 后端服务 (Python/FastAPI) 优化

### 1. 场景化感知 (Scene-Awareness)
- **目标**：根据用户环境（车载、运动、深夜）自动调整回复风格。
- **方案**：`/ask` 接口增加 `scene` 参数，通过 System Prompt 切换模式（如：车载模式下回复控制在 30 字以内）。

### 2. 连续对话逻辑 (Follow-up Loop)
- **目标**：实现无缝接话，无需重复唤醒 Siri。
- **方案**：后端返回 `continue: true` 标志位，触发快捷指令自动进入下一轮听写。

### 3. 反向主动推送 (Proactive Push)
- **目标**：让 Jarvis 能够主动“开口”或弹窗。
- **方案**：集成 Bark/Pushcut 接口。任务完成时推送带 URL Scheme 的通知，点击即触发 Siri 朗读。

### 4. 多模态支持 (Visual Input)
- **目标**：支持“拍张照片问 Jarvis”。
- **方案**：接口支持 Base64 图片编码，调用 OpenClaw 多模态大模型进行视觉识别。

### 5. 系统指挥官 (OS Voice Controller)
- **目标**：通过手机语音控制 Mac 硬件。
- **实现**：后端集成 **AppleScript** 执行引擎。支持“关屏”、“休眠”、“静音”或从 iMessage 提取内容等指令。

---

## 二、 iOS 快捷指令 (Shortcuts) 优化

### 1. 混合输入模式
- **逻辑**：启动时判断剪贴板。有链接则询问是否总结，无内容则默认听写语音。

### 2. 智能链路自愈 (Self-Healing)
- **逻辑**：请求失败时自动检查网络及 Tailscale 状态，引导一键开启隧道。

### 3. 一键配置工作流 (Magic Setup)
- **方案 A (Local)**：创建 `Setup` 指令，将配置存入 iCloud Drive，主指令自动读取，实现“配置与逻辑分离”。
- **方案 B (Cloud)**：后端提供 `/setup` 网页，生成带参数的 `shortcuts://` 链接，用户扫码即完成 IP 和 Token 注入。

### 4. UI/UX 深度反馈
- **触感**：发送前轻震，开始听写前双震，成功后强震。
- **视觉**：调用“显示通知”或“显示结果”弹出“正在思考...”动态横幅。

---

## 三、 商业化与未来构想 (Jarvis 3.0)

### 1. 智能缓存 (Smart Cache)
- **目标**：基础查询（天气、时间）不消耗 LLM，由后端脚本直回。

### 2. 多用户与隐私隔离 (Multi-Tenant)
- **方案**：支持 `X-Bridge-Secret` 身份区分；采用“钥匙在手，货在云端”的加密隔离模式。

### 3. 指令集化 (Action Sets)
- **目标**：从问答器进化为任务流控制器。一句话触发一套复杂的生产力业务脚本。

---

**最后更新**：2026-02-05 15:15  
**记录人**：Jarvis (Consolidated from Memory & Roadmap files)
