
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from rag_utils import extract_pdf_pages, split_into_chunks, search_chunks

load_dotenv()

st.set_page_config(
    page_title="AI PDF 智能文档问答助手",
    page_icon="📚",
    layout="wide",
)

st.title("📚 AI PDF 智能文档问答助手")
st.caption("上传 PDF 文档，向 AI 提问，并查看答案对应的文档来源。")

api_key = os.getenv("DASHSCOPE_API_KEY")
base_url = os.getenv(
    "DASHSCOPE_BASE_URL",
    "https://dashscope.aliyuncs.com/compatible-mode/v1",
)
model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")

if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "document_names" not in st.session_state:
    st.session_state.document_names = []

with st.sidebar:
    st.header("📄 文档管理")

    uploaded_files = st.file_uploader(
        "上传 PDF 文件",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if st.button("开始处理文档", type="primary", use_container_width=True):
        if not uploaded_files:
            st.warning("请先上传 PDF 文件。")
        else:
            all_pages = []
            failed_files = []

            progress = st.progress(0)

            for index, file in enumerate(uploaded_files):
                try:
                    pages = extract_pdf_pages(file.getvalue(), file.name)
                    all_pages.extend(pages)
                except Exception as error:
                    failed_files.append(f"{file.name}：{error}")

                progress.progress((index + 1) / len(uploaded_files))

            chunks = split_into_chunks(all_pages)

            st.session_state.chunks = chunks
            st.session_state.messages = []
            st.session_state.document_names = list(
                dict.fromkeys(
                    page["filename"] for page in all_pages
                )
            )

            progress.empty()

            for error in failed_files:
                st.error(error)

            if chunks:
                st.success(
                    f"处理完成！共提取 {len(all_pages)} 页，"
                    f"生成 {len(chunks)} 个文本片段。"
                )
            else:
                st.warning("没有提取到文字，请检查 PDF 文件。")

    st.divider()
    st.subheader("📊 文档状态")
    st.write(f"文本片段：{len(st.session_state.chunks)}")
    st.write(f"已处理文件：{len(st.session_state.document_names)}")

    for name in st.session_state.document_names:
        st.caption(f"📄 {name}")

    if st.button("清空文档和对话", use_container_width=True):
        st.session_state.chunks = []
        st.session_state.messages = []
        st.session_state.document_names = []
        st.rerun()

    st.divider()
    st.caption(f"AI 模型：{model}")

if not st.session_state.chunks:
    st.info("请先在左侧上传 PDF 文件，然后点击「开始处理文档」。")

    st.markdown(
        """
        ### 使用步骤

        1. 上传一份或多份 PDF 文件。
        2. 点击「开始处理文档」。
        3. 等待系统提取文档内容。
        4. 在下方输入问题。
        5. 查看 AI 回答和引用页码。

        ### 示例问题

        - 请总结这份文档的核心内容。
        - 文档中提到了哪些重要数据？
        - 请列出文档中的主要结论。
        - 这份文档主要讨论了什么问题？
        """
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("sources"):
            with st.expander("📚 查看引用来源"):
                for source in message["sources"]:
                    st.markdown(
                        f"**{source['filename']} · 第 {source['page']} 页**"
                    )
                    st.write(source["text"])

question = st.chat_input(
    "输入你想了解的文档问题……",
    disabled=not st.session_state.chunks,
)

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        if not api_key:
            answer = "未检测到 API Key，请检查项目根目录中的 .env 文件。"
            st.error(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": []}
            )
        else:
            with st.spinner("正在检索文档并生成回答……"):
                try:
                    results = search_chunks(
                        st.session_state.chunks,
                        question,
                        top_k=4,
                    )

                    if not results:
                        answer = "没有在当前文档中找到相关内容，请尝试换一种问法。"
                        sources = []
                    else:
                        context = "\n\n".join(
                            [
                                f"文件：{item['filename']}\n"
                                f"页码：第 {item['page']} 页\n"
                                f"内容：{item['text']}"
                                for item in results
                            ]
                        )

                        client = OpenAI(
                            api_key=api_key,
                            base_url=base_url,
                            timeout=30,
                            max_retries=0,
                        )

                        response = client.chat.completions.create(
                            model=model,
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "你是一个严谨的 PDF 文档问答助手。"
                                        "请根据提供的文档内容回答问题。"
                                        "不要编造文档中没有的信息。"
                                        "如果文档没有相关信息，请明确说明。"
                                        "请使用中文回答。"
                                    ),
                                },
                                {
                                    "role": "user",
                                    "content": (
                                        f"文档内容：\n\n{context}\n\n"
                                        f"用户问题：{question}"
                                    ),
                                },
                            ],
                            max_tokens=800,
                        )

                        answer = (
                            response.choices[0].message.content
                            or "AI 暂时没有返回有效内容。"
                        )
                        sources = results

                    st.markdown(answer)

                    if sources:
                        with st.expander("📚 查看引用来源"):
                            for source in sources:
                                st.markdown(
                                    f"**{source['filename']} · "
                                    f"第 {source['page']} 页**"
                                )
                                st.write(source["text"])

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                        }
                    )

                except Exception as error:
                    error_message = f"AI 请求失败：{error}"
                    st.error(error_message)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": error_message,
                            "sources": [],
                        }
                    )
