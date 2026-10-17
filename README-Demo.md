# 基金公告运营助手 Demo

## 运行方式

1. 安装 Node.js 18 或更新版本。
2. 将 `.env.example` 复制为 `.env`，填写 DeepSeek API Key。
3. PDF 上传需要 Python 3 与 `pdfplumber`。可运行 `python3 -m pip install -r requirements.txt` 安装依赖。
4. 启动服务：

   ```sh
   node server.js
   ```

5. 浏览器访问 <http://localhost:4173>。

## 发布到 Vercel

项目已提供 Vercel Functions 入口：`/api/status`、`/api/generate` 使用 Node.js Function，`/api/extract-pdf` 使用 Python Function。普通 HTML/CSS/JS 由 Vercel 作为静态资源发布。

1. 将代码放入 **私有** GitHub 仓库，并将仓库关联到 Vercel。不要提交 `.env`、真实 API Key 或任何访问口令；`.gitignore` 已排除 `.env`。
2. 在 Vercel 项目设置中添加环境变量：`MODEL_BASE_URL`、`MODEL_API_KEY`、`MODEL_NAME`、`MODEL_AVAILABLE_MODELS`、`DEMO_ACCESS_PASSWORD`。API Key 标记为 Sensitive；访问口令使用随机长密码。公网接口在没有访问口令时会拒绝生成请求。
3. 框架预设选 Other；无需 Build Command，静态输出目录使用项目根目录。Python Function 依赖由 `requirements.txt` 安装。
4. 将 Vercel 提供的自定义域名 DNS 记录添加到域名 DNS 控制台。Vercel 为绑定域名配置 HTTPS 后即可访问。
5. GitHub 每次推送会触发新部署；生产分支（通常为 `main`）更新后，绑定域名会更新到新版本。每次修改 Vercel 环境变量后也要重新部署。

Vercel Function 请求体限制为 4.5 MB；因此公网版 PDF 上传限制为 3 MB，本地版仍为 12 MB。对话暂存在浏览器内存中，刷新后不会保留。

模型密钥由服务端读取，仅保存在本地 `.env`；不要把真实密钥放进网页代码或提交到仓库。

## 对话流程

- 新建对话时显示产品介绍和消息输入区。
- 用户上传 PDF、TXT 或 Markdown 公告，PDF 在本地提取文本；也可从「案例与历史对话」选择示例公告。
- 案例 A/B/C 会预载题目原文公告与对应任务提示词；提示词可在发送前修改，公告附件上的「查看 / 编辑」可检查或修改公告原文。
- 每次案例请求都会将材料一产品基本资料作为固定背景，与案例公告和任务一起发送给 DeepSeek。公告原文在发送后固定在当前会话中；如需改动，请新建对话。
- 模型结果接在对话中，包含公告摘要、用户影响、客服回复、运营材料、待确认事项及可核对原文依据；引用会按公告原文校验并强制标注来源。
- 关键案例规则由服务端追加确定性核对说明：案例 A 核对离任原因及不得推断业绩；案例 B 核对起始日、合并限额及恢复日期未知；案例 C 计算分红金额并提示登记记录确认分红方式。
- 对话支持连续追问；追问会携带最近的用户与助手消息，并沿用当前公告和材料一。对话按标题列在「案例与历史对话」中，刷新后清空。
- 客服回复可复制，分析结果可复制或导出 Markdown。模型格式异常时可在错误卡片中重试。示例只预填题目材料，不预置模型答案；模型结论由实时 API 调用生成。

## 提交留档

本地交付还需保存案例 A/B/C 的实际模型运行结果截图。截图应来自本地服务运行后的真实输出，并在提交前人工核对案例验收规则；本仓库未内置模拟回答或伪造结果截图。本次开发核查中案例 A 曾成功返回；案例 B/C 的模型接口出现空内容或格式错误，因此三案例结果截图尚未齐备。

## 模型接口

使用 DeepSeek OpenAI-compatible Chat Completions：`https://api.deepseek.com`，默认模型 `deepseek-flash`，响应使用 JSON Output。`.env` 示例：

```env
MODEL_BASE_URL=https://api.deepseek.com
MODEL_API_KEY=你的DeepSeek_API_Key
MODEL_NAME=deepseek-flash
MODEL_AVAILABLE_MODELS=deepseek-flash
PORT=4173
```

`MODEL_NAME` 配置的模型会作为默认选项。若同一服务端点和 API Key 还接入了其他模型 ID，可将它们列在 `MODEL_AVAILABLE_MODELS` 中；模型选择菜单会启用已接入的模型，并将其余选项标记为「暂未接入」。

## 边界

PDF 文本提取在本机完成；扫描图片版 PDF 暂不支持 OCR。模型分析会将固定考试背景材料、案例或用户上传的公告文本、提示词发送至 DeepSeek API。题目中的基金、公司、人物与数据均为虚构，仅用于考试演示。Demo 不连接真实基金账户、交易系统或客服系统，无法核验账户持仓、申请受理状态或登记机构记录。模型输出需运营人员根据公告原文复核。
