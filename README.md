```markdown
# PDF 智能文档问答助手

基于 Python、Streamlit 和通义千问 API 开发的 AI 文档问答应用。用户上传 PDF 后，可以通过自然语言提问，系统检索相关内容并生成回答，同时展示引用的文件和页码。

## 项目功能

- 支持单个或多个 PDF 文件上传
- 自动提取 PDF 页面文本
- 文本切分与中文字符检索
- 基于通义千问 API 生成答案
- 支持连续多轮问答
- 展示回答对应的 PDF 文件名和页码
- 支持清空文档和对话

## 技术栈

- Python
- Streamlit
- PyMuPDF
- Scikit-learn
- OpenAI SDK
- 通义千问 API

## 项目结构

```text
ai-pdf-knowledge-assistant/
├── app.py
├── rag_utils.py
├── requirements.txt
├── README.md
├── .env.example
└── .gitignore
```

## 本地运行

安装依赖：

```bash
pip install -r requirements.txt
```

在项目根目录创建 `.env` 文件：

```env
DASHSCOPE_API_KEY=your_api_key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_MODEL=qwen-plus
```

启动应用：

```bash
streamlit run app.py
```

## 使用流程

1. 上传 PDF 文档。
2. 点击开始处理文档。
3. 系统提取文本并建立检索索引。
4. 输入自然语言问题。
5. 查看 AI 回答和引用来源。

## 安全说明

真实 API Key 保存在本地 `.env` 文件中，不要上传到 GitHub。

## 后续优化

- 增加扫描版 PDF 的 OCR 识别
- 优化语义检索效果
- 支持更多文档格式
- 增加文档管理和历史记录
```
