#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/8/27 16:06
@Author  : Rex
@File    : token_test.py
"""
import tiktoken
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import dotenv
import os

dotenv.load_dotenv("../../.env")

# 测试文本
text = "Hello world"

# 1. 计算纯文本 token 数
enc = tiktoken.encoding_for_model("gpt-4o-mini")
pure_tokens = len(enc.encode(text))
print("pure_tokens:", pure_tokens)

llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
)
res = llm.invoke([HumanMessage(content=text)])
lc_tokens=res.response_metadata["token_usage"]["completion_tokens"]
print("lc_tokens:", lc_tokens)

print("The extra token:", lc_tokens - pure_tokens)
