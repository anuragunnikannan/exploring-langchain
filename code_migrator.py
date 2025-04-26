import os
from langchain_ollama import ChatOllama, OllamaLLM
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

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


def write_code_to_text_file():
    files = get_all_files(
        ignore_files=["__pycache__", ".git", "README.md", "venv", "docker-compose.yml", "nginx.conf", ".gitignore", "Dockerfile_nginx"])

    text = ""
    for file in files:
        text += f"\n\nFilename: {file}\n\n"
        text += get_content(file)
        text += "\n\n----------------------------------\n\n"

    with open('project_source_code.txt', 'w') as f:
        f.write(text)


def split_text(text, chunk_size=4000, overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=overlap)

    return splitter.split_text(text)


def generate_tsd_from_chunk(llm, chunk):
    template = """
        You are a senior software architect, experienced in working in enterprise level projects. Based on the given codebase, create a technical specification document including modules, classes, DB tables, APIs and external dependencies. You should go through the snippet thoroughly before writing the document.
    """

    prompt_template = ChatPromptTemplate(
        [("system", template), ("human", "{chunk}")], format=None)

    chain = prompt_template | llm

    return chain.invoke({"chunk": chunk})


def generate_tsd():

    write_code_to_text_file()

    llm = ChatOllama(model="phi4", temperature=0.3,
                     base_url=os.environ.get("BASE_URL"))

    code = ""
    with open("project_source_code.txt", "r") as f:
        code = f.read()

    chunks = split_text(code)

    partial_tsds = [generate_tsd_from_chunk(llm, chunk) for chunk in chunks]
    combined_summary = "\n\n".join(partial_tsds)

    template = """
        You are an expert software developer with ample amount of experience working in enterprise level projects. Your task is to refine and consolidate the following technical specification documents without adding or removing any information.
    """

    prompt_template = ChatPromptTemplate(
        [("system", template), ("human", "{tsds}")])

    chain = prompt_template | llm

    final_tsd = chain.invoke({"tsds": combined_summary})

    with open("final_tsd.txt", "w") as f:
        f.write(final_tsd)


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
    generate_tsd()
