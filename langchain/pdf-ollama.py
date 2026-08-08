# Importing the necessary packages
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.chains import RetrievalQA
import textwrap
import datetime
# This will load the PDF file
def load_pdf_data(file_path):
    # Creating a PyMuPDFLoader object with file_path
    loader = PyMuPDFLoader(file_path=file_path)
    
    # loading the PDF file
    docs = loader.load()
    
    # returning the loaded document
    return docs



# Responsible for splitting the documents into several chunks
def split_docs(documents, chunk_size=1000, chunk_overlap=20):
    
    # Initializing the RecursiveCharacterTextSplitter with
    # chunk_size and chunk_overlap
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    # Splitting the documents into chunks
    chunks = text_splitter.split_documents(documents=documents)
    
    # returning the document chunks
    return chunks


# function for loading the embedding model
def load_embedding_model(model_path, normalize_embedding=True):
    return HuggingFaceEmbeddings(
        model_name=model_path,
        model_kwargs={'device':'cpu'}, # here we will run the model with CPU only
        encode_kwargs = {
            'normalize_embeddings': normalize_embedding # keep True to compute cosine similarity
        }
    )


# Function for creating embeddings using FAISS
def create_embeddings(chunks, embedding_model, storing_path="vectorstore"):
    # Creating the embeddings using FAISS
    vectorstore = FAISS.from_documents(chunks, embedding_model)
    
    # Saving the model in current directory
    vectorstore.save_local(storing_path)
    
    # returning the vectorstore
    return vectorstore



prompt = """
### System:
You are an AI Assistant that follows instructions extreamly well. \
Help as much as you can.

### User:
{prompt}

### Response:

"""


template = """
### System:
You are an respectful and honest assistant. You have to answer the user's \
questions using only the context provided to you. If you don't know the answer, \
just say you don't know. Don't try to make up an answer.

### Context:
{context}

### User:
{question}

### Response:
"""


# Creating the chain for Question Answering
def load_qa_chain(retriever, llm, prompt):
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever, # here we are using the vectorstore as a retriever
        chain_type="stuff",
        return_source_documents=True, # including source documents in output
        chain_type_kwargs={'prompt': prompt} # customizing the prompt
    )


# Prettifying the response
def get_response(query, chain):
    # Getting response from chain
    response = chain.invoke({'query': query})
    
    # Wrapping the text for better output in Jupyter Notebook
    wrapped_text = textwrap.fill(response['result'], width=100)
    print(wrapped_text)



# Loading orca-mini from Ollama
from langchain_ollama import OllamaEmbeddings,OllamaLLM
llm = OllamaLLM(model="mistral", temperature=0)

# Loading the Embedding Model
embed = OllamaEmbeddings(base_url="http://localhost:11434", model="mxbai-embed-large")



# loading and splitting the documents
docs = load_pdf_data(file_path="data/a1.pdf")
loader = PyPDFDirectoryLoader("E:/05-Learning")
docs = loader.load()

documents = split_docs(documents=docs)


# creating vectorstore
vectorstore = create_embeddings(documents, embed)

# converting vectorstore to a retriever
retriever = vectorstore.as_retriever()


# Creating the prompt from the template which we created before
from langchain_core.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_template(template)

# Creating the chain
chain = load_qa_chain(retriever, llm, prompt)
print(datetime.datetime.now())
get_response("怎么样销售最有效？", chain)
print(datetime.datetime.now())
get_response("怎么样进行共情销售？", chain)
print(datetime.datetime.now())

import pickle 
def save_object(obj, filename):
    with open(filename, 'wb') as outp:  # Overwrites any existing file.
        pickle.dump(obj, outp, pickle.HIGHEST_PROTOCOL)




#save_object(chain,"model/a1.pkl")

#with open('retriever.pkl', 'rb') as inp:
#    big_chunks_retriever = pickle.load(inp)

def newSaveLoad():
    #vectorstore = FAISS.from_documents(docs, embed)
    with open("base_documents.pkl", "wb") as f:
                pickle.dump(documents, f)
    with open('base_documents.pkl', 'rb') as inp:
        big_chunks_retriever = pickle.load(inp)