import os
from langchain_ollama import ChatOllama, OllamaLLM
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

llm = ChatOllama(model="llama3.2", temperature=0.3,
                 base_url=os.environ.get("BASE_URL"))

# llm = OllamaLLM(model="llama3.2", temperature=0.3,
#                 base_url=os.environ.get("BASE_URL"))

python_code = ""

with open("test.py", "r") as f:
    python_code = f.read()

template = """
You are a helpful assistant that only returns raw code, with no explanations and no formatting.
Rules:
- Convert the given {source_language} code to {target_language}.
- Do NOT wrap the code in backticks.
- Do NOT include any type of formatting.
- Just return raw code.
"""

prompt_template = ChatPromptTemplate([
    ("system", template),
    ("human", python_code)
])

# forming chains using LCEL (LangChain Expression Language)
chain = prompt_template | llm | StrOutputParser()

response = chain.invoke(
    {"source_language": "python", "target_language": "java"})

with open("Factorial3.java", "w") as f:
    f.write(response)
