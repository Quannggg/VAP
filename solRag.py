import os
from langchain_community.vectorstores.chroma import Chroma
from langchain import hub


from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from langchain_core.runnables import RunnableParallel
from nltk.stem import WordNetLemmatizer
import re
import bs4
import pprint

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

stop_words = set(stopwords.words('english'))

lemmatizer = WordNetLemmatizer()


def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    filtered_tokens = [lemmatizer.lemmatize(w) for w in tokens if w.isalpha() and w not in stop_words]
    return ' '.join(filtered_tokens)


def clean_html(html_content):
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    text = soup.get_text()
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


"""

BASE_URL = "https://solanacookbook.com/"
lists_of_links: Sequence[str] = [
    BASE_URL + "",
    BASE_URL + "core-concepts/accounts.html",
    BASE_URL + "core-concepts/programs.html",
    BASE_URL + "core-concepts/transactions.html",
    BASE_URL + "core-concepts/pdas.html",
    BASE_URL + "core-concepts/cpi.html",
    BASE_URL + "guides/get-program-account.html",
    BASE_URL + "guides/serialization.html",
    BASE_URL + "guides/data-migration.html",
    BASE_URL + "guides/account-maps.html",
    BASE_URL + "guides/retrying-transactions.html",
    BASE_URL + "guides/debugging-solana-programs.html",
    BASE_URL + "guides/working-with-accounts.html",
    BASE_URL + "guides/feature-parity-testing.html",
    BASE_URL + "guides/versioned-transactions.html",
    BASE_URL + "reference/local-development.html",
    BASE_URL + "reference/keypairs-and-wallets.html",
    BASE_URL + "reference/basic-transactions.html",
    BASE_URL + "reference/programs.html",
    BASE_URL + "reference/token.html",
    BASE_URL + "reference/staking.html",
    BASE_URL + "reference/nfts.html",
    BASE_URL + "reference/offline-transactions.html",
    BASE_URL + "reference/name-service.html",
]
loader = WebBaseLoader(
    web_paths=lists_of_links,
)

docs = loader.load()

for doc in docs:
    doc.page_content = clean_html(doc.page_content)
    doc.page_content = preprocess_text(doc.page_content)


text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(), persist_directory="solanacookbook")

Only run this once to create the vectorstore => solanacookbook
"""

vectorstore = Chroma(persist_directory="solanacookbook", embedding_function=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

prompt = hub.pull("rlm/rag-prompt")

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)


rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | prompt
        | llm
        | StrOutputParser()
)


rag_chain_with_source = RunnableParallel(
    {"context": retriever, "question": RunnablePassthrough()}
).assign(answer=rag_chain_from_docs)


def get_response(question):
    response = rag_chain_with_source.invoke(question)
    return response["answer"]

if __name__ == "__main__":
    print(get_response("What is Solana?"))
