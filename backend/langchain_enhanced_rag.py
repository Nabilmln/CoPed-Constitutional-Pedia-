"""
LangChain Enhanced Document Understanding System
Advanced RAG dengan Vector Database untuk akurasi maksimal
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# LangChain imports
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain.schema import Document

# Existing imports
from document_cache import DocumentCache
import google.generativeai as genai

class LangChainEnhancedRAG:
    def __init__(self, persist_directory="./chroma_db"):
        """Initialize LangChain enhanced RAG system"""
        self.persist_directory = persist_directory
        self.cache = DocumentCache()
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None
        
        # Setup components
        self.setup_embeddings()
        self.setup_llm()
        self.setup_text_splitter()
        self.setup_prompt_template()
        
        print("🚀 LangChain Enhanced RAG initialized")
    
    def setup_embeddings(self):
        """Setup sentence transformer embeddings untuk semantic search"""
        try:
            # Use multilingual model untuk Indonesian + English
            self.embeddings = SentenceTransformerEmbeddings(
                model_name="paraphrase-multilingual-MiniLM-L12-v2"
            )
            print("✅ Multilingual embeddings loaded")
        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
            # Fallback to simpler model
            self.embeddings = SentenceTransformerEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )
            print("⚠️ Using fallback embeddings")
    
    def setup_llm(self):
        """Setup Google Gemini LLM via LangChain"""
        try:
            self.llm = GoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key="AIzaSyDPVaD6JBzYf6fTzmPeR3eUck0Mm62LvHM",
                temperature=0.1  # Low temperature untuk faktual accuracy
            )
            print("✅ Gemini LLM initialized via LangChain")
        except Exception as e:
            print(f"❌ Error setting up LLM: {e}")
    
    def setup_text_splitter(self):
        """Setup intelligent text splitter"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,           # Optimal chunk size untuk legal docs
            chunk_overlap=200,         # Overlap untuk context preservation
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]  # Hierarchical splitting
        )
        print("✅ Intelligent text splitter configured")
    
    def setup_prompt_template(self):
        """Setup optimized prompt template untuk Indonesian legal docs"""
        template = """
Anda adalah AI assistant ahli hukum konstitusi Indonesia. Berdasarkan dokumen-dokumen UUD 1945 dan konstitusi terkait, jawab pertanyaan dengan akurat dan komprehensif.

KONTEKS DOKUMEN:
{context}

INSTRUKSI:
1. Berikan jawaban yang faktual dan akurat berdasarkan dokumen
2. Sebutkan pasal, ayat, atau bagian spesifik jika relevan
3. Gunakan bahasa Indonesia yang formal dan jelas
4. Jika informasi tidak tersedia dalam dokumen, jelaskan dengan jujur
5. Struktur jawaban dengan bullet points atau numbering jika perlu

PERTANYAAN: {question}

JAWABAN KOMPREHENSIF:
"""
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        print("✅ Optimized prompt template created")
    
    def load_and_process_documents(self, pdf_directory="data/"):
        """Load dan process multiple PDFs dengan LangChain loaders"""
        print(f"\n📚 Loading and processing documents from {pdf_directory}")
        
        documents = []
        processed_files = []
        
        # Get all PDF files
        pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            file_path = os.path.join(pdf_directory, pdf_file)
            try:
                print(f"📄 Processing: {pdf_file}")
                
                # Use LangChain PDF loader
                loader = PyPDFLoader(file_path)
                pages = loader.load()
                
                # Add metadata
                for page in pages:
                    page.metadata['source_file'] = pdf_file
                    page.metadata['file_path'] = file_path
                
                documents.extend(pages)
                processed_files.append(pdf_file)
                print(f"  ✅ Loaded {len(pages)} pages")
                
            except Exception as e:
                print(f"  ❌ Error processing {pdf_file}: {e}")
        
        # Split documents into chunks
        print(f"\n🔀 Splitting documents into chunks...")
        split_docs = self.text_splitter.split_documents(documents)
        
        print(f"📊 Processing summary:")
        print(f"  📁 Files processed: {len(processed_files)}")
        print(f"  📄 Total pages: {len(documents)}")
        print(f"  📝 Total chunks: {len(split_docs)}")
        print(f"  📋 Files: {', '.join(processed_files)}")
        
        return split_docs, processed_files
    
    def build_vector_database(self, documents: List[Document], force_rebuild=False):
        """Build vector database dengan Chroma"""
        print(f"\n🔍 Building vector database...")
        
        # Check if database already exists
        if os.path.exists(self.persist_directory) and not force_rebuild:
            print(f"📦 Loading existing vector database from {self.persist_directory}")
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            print(f"🔨 Creating new vector database...")
            
            # Create vectorstore
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            # Persist to disk
            self.vectorstore.persist()
            print(f"💾 Vector database saved to {self.persist_directory}")
        
        # Setup retriever
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}  # Retrieve top 5 most relevant chunks
        )
        
        print(f"✅ Vector database ready with {self.vectorstore._collection.count()} chunks")
        return self.vectorstore
    
    def setup_qa_chain(self):
        """Setup QA chain dengan retrieval"""
        if not self.retriever:
            raise ValueError("Retriever not setup. Build vector database first.")
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",  # Stuff all retrieved docs into prompt
            retriever=self.retriever,
            chain_type_kwargs={"prompt": self.prompt},
            return_source_documents=True
        )
        
        print("✅ QA Chain configured with retrieval")
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query the enhanced RAG system"""
        if not self.qa_chain:
            raise ValueError("QA Chain not setup. Call setup_qa_chain() first.")
        
        print(f"\n🔍 Processing query: {question}")
        
        try:
            # Run the chain
            result = self.qa_chain({"query": question})
            
            # Extract source information
            sources = []
            for doc in result.get("source_documents", []):
                sources.append({
                    "file": doc.metadata.get("source_file", "Unknown"),
                    "page": doc.metadata.get("page", "Unknown"),
                    "content_preview": doc.page_content[:100] + "..."
                })
            
            enhanced_result = {
                "question": question,
                "answer": result["result"],
                "sources": sources,
                "num_sources": len(sources),
                "retrieval_method": "semantic_similarity",
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Query processed with {len(sources)} source chunks")
            return enhanced_result
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            return {
                "question": question,
                "answer": f"Error: {e}",
                "sources": [],
                "error": True
            }
    
    def compare_with_baseline(self, question: str, baseline_answer: str = None):
        """Compare LangChain results dengan baseline system"""
        print(f"\n COMPARISON: LangChain vs Baseline")
        
        # LangChain result
        langchain_result = self.query(question)
        
        # Baseline result (if provided)
        if baseline_answer:
            comparison = {
                "question": question,
                "langchain": {
                    "answer": langchain_result["answer"],
                    "sources": len(langchain_result["sources"]),
                    "method": "semantic_retrieval + optimized_prompt"
                },
                "baseline": {
                    "answer": baseline_answer,
                    "method": "simple_text_matching"
                },
                "comparison_timestamp": datetime.now().isoformat()
            }
            
            print(f"📊 LangChain sources: {len(langchain_result['sources'])}")
            print(f"📄 LangChain answer length: {len(langchain_result['answer'])} chars")
            
            return comparison
        
        return langchain_result
    
    def evaluate_accuracy(self, test_questions: List[Dict]):
        """Evaluate system accuracy dengan test questions"""
        print(f"\n📊 EVALUATING ACCURACY dengan {len(test_questions)} questions")
        
        results = []
        total_score = 0
        
        for i, test_case in enumerate(test_questions, 1):
            question = test_case["question"]
            expected_keywords = test_case.get("expected_keywords", [])
            
            print(f"\n❓ Question {i}: {question}")
            
            # Get answer
            result = self.query(question)
            answer = result["answer"]
            
            # Simple accuracy scoring based on keyword presence
            score = 0
            if expected_keywords:
                found_keywords = sum(1 for keyword in expected_keywords if keyword.lower() in answer.lower())
                score = (found_keywords / len(expected_keywords)) * 10
            
            result_record = {
                "question": question,
                "answer": answer,
                "expected_keywords": expected_keywords,
                "score": score,
                "sources_used": len(result["sources"])
            }
            
            results.append(result_record)
            total_score += score
            
            print(f"📊 Score: {score:.1f}/10 ({len(result['sources'])} sources)")
        
        average_accuracy = total_score / len(test_questions)
        
        evaluation_summary = {
            "total_questions": len(test_questions),
            "average_accuracy": average_accuracy,
            "accuracy_percentage": f"{average_accuracy * 10:.1f}%",
            "detailed_results": results,
            "evaluation_timestamp": datetime.now().isoformat()
        }
        
        print(f"\n🎯 FINAL ACCURACY: {average_accuracy * 10:.1f}%")
        
        return evaluation_summary
    
    def get_system_info(self):
        """Get comprehensive system information"""
        info = {
            "system_type": "LangChain Enhanced RAG",
            "components": {
                "embeddings": "paraphrase-multilingual-MiniLM-L12-v2",
                "vector_db": "ChromaDB",
                "llm": "Google Gemini Pro",
                "text_splitter": "RecursiveCharacterTextSplitter",
                "retrieval_method": "Semantic Similarity Search"
            },
            "configuration": {
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "retrieval_k": 5,
                "temperature": 0.1
            },
            "database_path": self.persist_directory,
            "total_chunks": self.vectorstore._collection.count() if self.vectorstore else 0
        }
        
        return info

def demo_langchain_rag():
    """Demo comprehensive LangChain RAG system"""
    print("🚀 LANGCHAIN ENHANCED RAG DEMO")
    
    # Initialize system
    rag = LangChainEnhancedRAG()
    
    # Load and process documents
    documents, files = rag.load_and_process_documents()
    
    # Build vector database
    vectorstore = rag.build_vector_database(documents, force_rebuild=True)
    
    # Setup QA chain
    rag.setup_qa_chain()
    
    # Demo queries
    test_questions = [
        {
            "question": "Apa isi pasal 1 ayat 1 UUD 1945?",
            "expected_keywords": ["negara indonesia", "negara kesatuan", "republik"]
        },
        {
            "question": "Apa yang dimaksud dengan kedaulatan rakyat?",
            "expected_keywords": ["kedaulatan", "rakyat", "undang-undang dasar"]
        },
        {
            "question": "Bagaimana sistem checks and balances dalam UUD 1945?",
            "expected_keywords": ["checks and balances", "lembaga negara", "kekuasaan"]
        }
    ]
    
    # Evaluate accuracy
    evaluation = rag.evaluate_accuracy(test_questions)
    
    # Show system info
    info = rag.get_system_info()
    print(f"\n🔧 SYSTEM INFO:")
    print(f"  Vector DB: {info['total_chunks']} chunks")
    print(f"  Embeddings: {info['components']['embeddings']}")
    print(f"  Accuracy: {evaluation['accuracy_percentage']}")
    
    return rag, evaluation

if __name__ == "__main__":
    demo_langchain_rag()
