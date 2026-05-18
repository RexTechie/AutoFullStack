#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler

from auto_full_stack.common.log import logger

dotenv.load_dotenv()

# Global token counters
TOTAL_INPUT_TOKEN = 0
TOTAL_OUTPUT_TOKEN = 0

class TokenCountingCallback(BaseCallbackHandler):
    """Token Counting Callback Handler"""

    def on_llm_start(self, serialized, prompts, **kwargs):
        """
        LLM start event
        """
        pass

    def on_llm_end(self, response, **kwargs):
        """
        LLM end event - count tokens
        """
        global TOTAL_INPUT_TOKEN, TOTAL_OUTPUT_TOKEN

        if hasattr(response, 'llm_output') and response.llm_output:
            token_usage = response.llm_output.get('token_usage', {})
            if token_usage:
                input_tokens = token_usage.get('prompt_tokens', 0)
                output_tokens = token_usage.get('completion_tokens', 0)
                total_tokens = token_usage.get('total_tokens', 0)
                TOTAL_INPUT_TOKEN += input_tokens
                TOTAL_OUTPUT_TOKEN += output_tokens
                logger.info("🧮 The token usage for this call - Input: {}, Output: {}, Total: {}".format(
                    input_tokens, output_tokens, total_tokens
                ))

def get_token_stats():
    """
    Get token total info
    """
    return {
        'total_input_tokens': TOTAL_INPUT_TOKEN,
        'total_output_tokens': TOTAL_OUTPUT_TOKEN,
        'total_tokens': TOTAL_INPUT_TOKEN + TOTAL_OUTPUT_TOKEN
    }

def reset_token_stats():
    """
    Reset token info
    """
    global TOTAL_INPUT_TOKEN, TOTAL_OUTPUT_TOKEN
    TOTAL_INPUT_TOKEN = 0
    TOTAL_OUTPUT_TOKEN = 0

# Initialize the model with the token counting callback
token_callback = TokenCountingCallback()

model = ChatOpenAI(
    model=os.getenv("LLM_MODEL"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    temperature=0.7,
    callbacks=[token_callback]  # Add the callback
)
