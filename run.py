import os
from news_pull import pull
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
import textwrap

# Just adds newlines for formatting
def format_text(text, width=80):
    # Split the text into paragraphs
    paragraphs = text.split('\n')

    # Wrap each paragraph using the specified width
    wrapped_paragraphs = [textwrap.fill(paragraph, width=width) for paragraph in paragraphs if paragraph]

    # Join the wrapped paragraphs with two newline characters for paragraph breaks
    formatted_text = '\n\n'.join(wrapped_paragraphs)

    return formatted_text


#threat_actor = input("Enter the name of the threat you want a report on: ")
threat_actor = "Volt Typhoon"

pull.get_newsapi_articles(threat_actor)

with open("articles.txt", 'r', encoding='utf-8') as file:
    articles = file.read()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=20,
    length_function=len,
    is_separator_regex=False,
)

os.environ['OPENAI_API_KEY'] = "*******************************"
os.environ['LANGCHAIN_TRACING_V2'] = "true"
os.environ['LANGCHAIN_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGCHAIN_API_KEY'] = "*******************************"
os.environ['LANGCHAIN_PROJECT'] = "threat_reporting"

docs = splitter.create_documents(texts=[articles])

embedding = OpenAIEmbeddings()

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embedding,
    persist_directory= f"Threat Reporting DB - {threat_actor}")

template = """Produce a summary of recent news articles relating to the following threat actor:
{threat_actor}

Use only reports relevant to the descriptions of these news articles on the threat actor:
{context}

Make the summaries 20-30 sentences long and use natural language.  
"""

prompt = ChatPromptTemplate.from_template(template)

model = ChatOpenAI()

#Explanation of metadata
metadata_field_info = [
    AttributeInfo(
        name="Article",
        description="Name of the article",
        type="string",
    ),
    AttributeInfo(
        name="description",
        description="Description of the article",
        type="integer",
    ),
    AttributeInfo(
        name="content_short",
        description="Brief excerpt from the article",
        type="integer",
    ),
    AttributeInfo(
        name="content",
        description="Content of the article",
        type="string",
    ),
    AttributeInfo(
        name="publishedAt",
        description="Time the article was published",
        type="string"
    ),
    AttributeInfo(
        name="publishedBy",
        description="Site the article was published",
        type="string"
    ),
]

document_content_description = f"Articles on Threat Actor {threat_actor}"

retriever = SelfQueryRetriever.from_llm(
    model, vectorstore, document_content_description, metadata_field_info, verbose=True)

chain = (prompt | model | StrOutputParser())

raw_output = chain.invoke({"context": retriever, "threat_actor": threat_actor})

# adds newlines for readability
output = format_text(raw_output)

with open("output_report.txt", "w", encoding='utf-8') as file:
    file.write(output)

print(output)