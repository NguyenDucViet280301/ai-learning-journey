import os
import io
import shutil
import requests
import pypdf
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from config import OLLAMA_BASE_URL, EMBEDDING_MODEL, DEFAULT_MODEL, FAISS_CHAT_DIR

class ChatbotEngine:
    """Conversational RAG engine that supports multi-document split/load/delete, query rephrasing, and chat memory."""

    @staticmethod
    def get_embeddings() -> OllamaEmbeddings:
        """Returns the configured OllamaEmbeddings instance."""
        return OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url=OLLAMA_BASE_URL
        )

    @staticmethod
    def get_llm(model_name: str = DEFAULT_MODEL, temperature: float = 0.0) -> ChatOllama:
        """Returns the ChatOllama LLM client for a specific model."""
        return ChatOllama(
            model=model_name,
            base_url=OLLAMA_BASE_URL,
            temperature=temperature
        )

    @staticmethod
    def get_local_ollama_models() -> list[str]:
        """Fetches available local models from the Ollama instance via API."""
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
            if response.status_code == 200:
                models = [m["name"] for m in response.json().get("models", [])]
                # Ensure the default model is present in the list
                if DEFAULT_MODEL not in models:
                    models.append(DEFAULT_MODEL)
                return sorted(list(set(models)))
        except Exception:
            pass
        return [DEFAULT_MODEL, "qwen2.5:7b", "llama3", "mistral"]

    @staticmethod
    def process_pdf(
        file_bytes: bytes, 
        filename: str, 
        chunk_size: int, 
        chunk_overlap: int, 
        path: str = FAISS_CHAT_DIR
    ) -> int:
        """Parses PDF page-by-page, splits it recursively, and appends vectors to the FAISS index.
        If the file already exists in the database, its previous chunks are replaced.
        """
        pdf_file = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_file)
        
        # Enforce defensive chunk overlap
        chunk_overlap = min(chunk_overlap, chunk_size - 1)
        if chunk_overlap < 0:
            chunk_overlap = 0

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True
        )
        
        all_docs = []
        for idx, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                docs = splitter.create_documents(
                    texts=[text],
                    metadatas=[{"source": filename, "page": idx + 1}]
                )
                all_docs.extend(docs)
                
        if not all_docs:
            raise ValueError("No extractable text found in this PDF file.")
            
        # Load existing store if it exists
        db = ChatbotEngine.load_store(path)
        if db is not None:
            # Delete old chunks belonging to the same filename to prevent duplication on re-upload
            ids_to_delete = [
                doc_id for doc_id, doc in db.docstore._dict.items()
                if doc.metadata.get("source") == filename
            ]
            if ids_to_delete:
                db.delete(ids_to_delete)
            
            # Add new documents to the existing index
            db.add_documents(all_docs)
            db.save_local(path)
        else:
            # Create a new index
            db = FAISS.from_documents(
                documents=all_docs,
                embedding=ChatbotEngine.get_embeddings(),
                distance_strategy=DistanceStrategy.COSINE
            )
            db.save_local(path)
        
        return len(all_docs)

    @staticmethod
    def delete_file(filename: str, path: str = FAISS_CHAT_DIR) -> bool:
        """Deletes all vector chunks associated with a specific file from the FAISS index.
        If no files remain, the index directory is deleted.
        """
        db = ChatbotEngine.load_store(path)
        if db is None:
            return False
            
        ids_to_delete = [
            doc_id for doc_id, doc in db.docstore._dict.items()
            if doc.metadata.get("source") == filename
        ]
        
        if not ids_to_delete:
            return False
            
        db.delete(ids_to_delete)
        
        # Check if the DB is now empty
        if len(db.docstore._dict) == 0:
            if os.path.exists(path):
                shutil.rmtree(path)
        else:
            db.save_local(path)
            
        return True

    @staticmethod
    def get_indexed_files(path: str = FAISS_CHAT_DIR) -> list[str]:
        """Scans the FAISS docstore metadata to find unique source filenames currently indexed."""
        db = ChatbotEngine.load_store(path)
        if db is None:
            return []
        files = set()
        for doc in db.docstore._dict.values():
            source = doc.metadata.get("source")
            if source:
                files.add(source)
        return sorted(list(files))

    @staticmethod
    def get_document_count(path: str = FAISS_CHAT_DIR) -> int:
        """Returns the total number of chunks currently stored in the database."""
        db = ChatbotEngine.load_store(path)
        if db is None:
            return 0
        return len(db.docstore._dict)

    @staticmethod
    def load_store(path: str = FAISS_CHAT_DIR) -> FAISS | None:
        """Loads the FAISS index from disk. Returns None if it does not exist."""
        faiss_file = os.path.join(path, "index.faiss")
        pkl_file = os.path.join(path, "index.pkl")
        
        if not (os.path.exists(faiss_file) and os.path.exists(pkl_file)):
            return None
            
        embeddings = ChatbotEngine.get_embeddings()
        return FAISS.load_local(
            folder_path=path,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )

    @staticmethod
    def rephrase_question(chat_history: list[dict], new_question: str, model_name: str = DEFAULT_MODEL) -> str:
        """Uses the LLM to rephrase a contextual follow-up question into a standalone query."""
        if not chat_history:
            return new_question
            
        # Format the last 5 turns of conversation
        history_str = ""
        for turn in chat_history[-5:]:
            role = "User" if turn["role"] == "user" else "AI Assistant"
            history_str += f"{role}: {turn['content']}\n"
            
        system_prompt = (
            "Given the following conversation history and a follow-up question from the user,\n"
            "rephrase the follow-up question to be a standalone question with complete subjects "
            "and clear context for information retrieval.\n"
            "Return ONLY the rephrased question as plain text. "
            "Do NOT answer the question and do NOT add any introductory or explanatory text.\n"
        )
        
        user_prompt = (
            f"--- Conversation History ---\n{history_str}\n"
            f"--- New Question ---\n{new_question}\n\n"
            "Rephrased Standalone Question:"
        )
        
        try:
            llm = ChatbotEngine.get_llm(model_name=model_name, temperature=0.0) # temperature=0 for exact rewrite
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            response = llm.invoke(messages)
            rephrased = response.content.strip()
            
            # Clean up potential wrapped quotes
            if rephrased.startswith('"') and rephrased.endswith('"'):
                rephrased = rephrased[1:-1].strip()
            if rephrased.startswith("'") and rephrased.endswith("'"):
                rephrased = rephrased[1:-1].strip()
                
            return rephrased if rephrased else new_question
        except Exception as e:
            print(f"Error rephrasing question: {e}")
            return new_question

    @staticmethod
    def conversational_rag(
        query: str, 
        chat_history: list[dict], 
        model_name: str = DEFAULT_MODEL,
        temperature: float = 0.2,
        top_k: int = 3, 
        search_strategy: str = "similarity", # "similarity" or "mmr"
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        path: str = FAISS_CHAT_DIR
    ) -> dict:
        """Executes the Conversational RAG pipeline with customizable model, search strategy, and parameters."""
        # 1. Rephrase follow-up query to a standalone query
        standalone_query = ChatbotEngine.rephrase_question(chat_history, query, model_name=model_name)
        
        # 2. Retrieve relevant contexts
        db = ChatbotEngine.load_store(path)
        if db is None:
            return {
                "answer": "No documents indexed. Please upload and index a PDF file in the sidebar first.",
                "sources": [],
                "standalone_query": standalone_query
            }
            
        # Select retrieval strategy
        if search_strategy == "mmr":
            docs = db.max_marginal_relevance_search(
                standalone_query, 
                k=top_k, 
                fetch_k=fetch_k, 
                lambda_mult=lambda_mult
            )
        else:
            docs = db.similarity_search(standalone_query, k=top_k)
        
        if not docs:
            return {
                "answer": "I could not find any information relevant to the question in the provided documents.",
                "sources": [],
                "standalone_query": standalone_query
            }
            
        # 3. Format context blocks and metadata sources
        context_blocks = []
        sources = []
        for idx, doc in enumerate(docs):
            source_name = doc.metadata.get("source", "Document")
            page_num = doc.metadata.get("page", "N/A")
            context_blocks.append(f"[Source: {source_name} - Page {page_num}]:\n{doc.page_content}")
            sources.append({
                "index": idx + 1,
                "source": source_name,
                "page": page_num,
                "text": doc.page_content
            })
        context_str = "\n\n".join(context_blocks)
        
        # 4. Construct system prompt
        system_prompt = (
            "You are an intelligent conversational AI chatbot assistant, "
            "specializing in answering questions based on the provided documents.\n"
            "Your task is to use the 'Context' section below to answer the user's question.\n"
            "Please answer naturally, politely, objectively, and directly. "
            "If the information is not found in the 'Context', answer exactly: "
            "'I cannot find this information in the provided documents.' Do NOT make up answers.\n\n"
            "--- Context ---\n"
            f"{context_str}\n"
        )
        
        # 5. Format Chat History + original new query for LLM generation
        messages = [SystemMessage(content=system_prompt)]
        
        # Format the last 5 turns for generation context
        for turn in chat_history[-5:]:
            if turn["role"] == "user":
                messages.append(HumanMessage(content=turn["content"]))
            else:
                messages.append(AIMessage(content=turn["content"]))
                
        # Append original new query
        messages.append(HumanMessage(content=query))
        
        # 6. Call LLM to generate response
        try:
            llm = ChatbotEngine.get_llm(model_name=model_name, temperature=temperature)
            response = llm.invoke(messages)
            answer = response.content
        except Exception as e:
            raise ConnectionError(
                f"Error connecting to or generating response from LLM model '{model_name}'. "
                f"Details: {e}"
            )
            
        return {
            "answer": answer,
            "sources": sources,
            "standalone_query": standalone_query
        }
