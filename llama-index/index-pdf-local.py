import os
import jwt
import time
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext, load_index_from_storage
# from llama_index.llms.ollama import Ollama
# from llama_index.embeddings.ollama import OllamaEmbedding
# from llama_index.llms.openai import OpenAI
# from langchain.llms import OpenAI
# from llama_index.llms.langchain import LangChainLLM
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
# from llama_index.core.llms import CustomLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.file import PDFReader
import requests
from typing import Any
from llama_index.core.llms.callbacks import llm_completion_callback
from llama_index.core.base.llms.types import LLMMetadata, CompletionResponse, CompletionResponseGen

#加载环境变量
load_dotenv()
# 获取环境变量
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("API_BASE")

LLM_MODEL = "medical_robot"
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=API_BASE
                )

# load pdf！！！
parser = PDFReader()
file_extractor = {".pdf": parser}
documents = SimpleDirectoryReader(
   "/home/gcj/cgft-llm/llama-index/pdf", file_extractor=file_extractor 
).load_data()
    

# emb ！！！
# Settings.embed_model = OllamaEmbedding(model_name="wangshenzhi/llama3-8b-chinese-chat-ollama-q8")  
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sensenova/piccolo-base-zh"
)

# llm！！！！
# Settings.llm = Ollama(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q8", request_timeout=360)  


# class OpenAILLM(CustomLLM):
#     context_window: int = 4096
#     num_output: int = 2048
#     model_name: str = LLM_MODEL

#     @property
#     def metadata(self) -> LLMMetadata:
#         return LLMMetadata(
#             context_window=self.context_window,
#             num_output=self.num_output,
#             model_name=self.model_name,
#         )
    
#     def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
#     # 将 prompt 格式化为消息列表
#         messages = [{"role": "user", "content": prompt}]
#         resp = client.chat.completions.create(
#             model=LLM_MODEL,
#             messages=messages,
#             max_tokens=self.num_output
#         )
#         # 正确访问消息内容
#         return CompletionResponse(text=resp.choices[0].message['content'].strip())

#     @llm_completion_callback()
#     def stream_complete(
#         self, prompt: str, **kwargs: Any
#     ) -> CompletionResponseGen:
#         # 将 prompt 格式化为消息列表
#         messages = [{"role": "user", "content": prompt}]
#         resp = client.chat.completions.create(
#             model=LLM_MODEL,
#             messages=messages,
#             max_tokens=self.num_output,
#             stream=True
#         )
#         response = ""
#         for event in resp:
#             # 正确处理流式响应
#             token = event['choices'][0]['delta']['content']
#             response += token
#             yield CompletionResponse(text=response, delta=token)



custom_llm = ChatAI()

# 使用自定义的LLM
Settings.llm = custom_llm



if not os.path.exists("llama-index/db/pdf-db"):
    index = VectorStoreIndex.from_documents(
        documents
    )
    index.storage_context.persist(persist_dir="llama-index/db/pdf-db")
    
else:
    storage_context = StorageContext.from_defaults(persist_dir="llama-index/db/pdf-db")
    index = load_index_from_storage(storage_context)

query_engine = index.as_query_engine()

# 执行查询并获取响应

response = query_engine.query("如果我想获得澳洲500签证， TOEFL最少要考多少分？")
print(response)