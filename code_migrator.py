import os
from langchain_ollama import ChatOllama, OllamaLLM
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

llm = ChatOllama(model="llama3.2", temperature=0.3,
                 base_url=os.environ.get("BASE_URL"))

BASE_DIR = "/media/anurag/mybkp/coderrank/coderrank-service"


def get_all_files(ignore_files):
    result = []

    for path, dirs, files in os.walk(BASE_DIR, topdown=True):
        dirs[:] = [d for d in dirs if d not in ignore_files]
        for i in files:
            if i not in ignore_files:
                result.append(path+"/"+i)

    return result


def get_content(filepath):
    content = ""
    with open(filepath, "r") as f:
        content = f.read()

    return content


def migrate_code():
    files = get_all_files(
        ignore_files=["__pycache__", ".git", "README.md", "venv", "docker-compose.yml", "nginx.conf", "Coderrank_DB.sql", "python_execute.sh", "java-execute.sh", "code-execute.sh", ".gitignore", "Dockerfile_nginx"])

    template = """
        You are a helpful assistant that only returns raw code, with no explanations and no formatting.
        Rules:
        - Convert the given python flask application to spring boot application.
        - Understand the logic of each file and use them to write your next file.
        - Best practices in Spring Boot must be followed.
        - Appropriate folder structure of a typical Spring Boot Application must be maintained
        - Do NOT wrap the code in backticks.
        - Do NOT include any type of formatting.
        - Just return raw code.
        - Do NOT ATTEMPT to refactor the supplied code.
        - Do NOT give any suggestions.
        - Just convert the code as ordered.
        - Before the start of each file provide JUST THE FILENAME of the converted code you are writing.
        - Your output should be in this format:

        \n
        ---------------------\n
        \nFilename: <filename>\n
        Source Code:\n\n
        <source_code>\n\n
        ---------------------
        \n
    """

    for i in files:
        content = get_content(i)
        instruction = f"Filename: {i}\nSource Code:\n{content.replace('{', '{{').replace('}', '}}')}"
        prompt_template = ChatPromptTemplate(
            [("system", template), ("human", instruction)], format=None)

        # forming chains using LCEL (LangChain Expression Language)
        chain = prompt_template | llm | StrOutputParser()

        response = chain.invoke({})

        with open("output.txt", "a") as f:
            f.write(response)


if __name__ == "__main__":
    migrate_code()
