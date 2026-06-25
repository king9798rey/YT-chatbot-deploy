import os
from langchain_core.runnables import RunnableParallel,RunnableLambda, RunnablePassthrough
from youtube_transcript_api import YouTubeTranscriptApi , TranscriptsDisabled
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
import streamlit as st

load_dotenv()

@st.cache_resource
def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


#INDEXING

#Loading

#video_id=''
#transcript=""

def build_chain(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.fetch(video_id, languages=['en'])
        transcript = " ".join(chunk.text for chunk in transcript_list)
        print(transcript[:500])

    except Exception as e:
        raise Exception(f"Transcript Error: {e}")



#Splitting
    splitter= RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks=splitter.create_documents([transcript])
    print(f"Number of chunks created: {len(chunks)}")
    if len(chunks) == 0:
        print("Error: No chunks created from transcript. Transcript might be empty.")
        exit(1)

#Embedding
    embedding = get_embedding_model()
    print("Embeddings model loaded successfully")
    vector_store=FAISS.from_documents(chunks, embedding)
    print("Vector store created successfully")

#Retriveal

    retriver= vector_store.as_retriever(search_type='similarity', search_kwargs={'k':4})

#Promptng

    prompt=PromptTemplate(
        template='''You are a helpfull assistant
                Answer Only the provided transcript context.
                If context is insufficient, just say you don't Know.

                {context}
                Question: {question}
    ''',
        input_variables=['context','question']
    )

#llm

    llm=ChatGroq(
        model='llama-3.1-8b-instant',
        temperature=0.3,
    )

    def format_docs(docs):
        context_text='\n\n'.join(doc.page_content for doc in docs)
        return context_text

    parrallel_chain= RunnableParallel({
        'context': retriver | RunnableLambda(format_docs),
        'question': RunnablePassthrough()

    })

    parser=StrOutputParser()

    main_chain= parrallel_chain | prompt |llm | parser

    return main_chain
