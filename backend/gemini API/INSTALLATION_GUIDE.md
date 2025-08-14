# 🚀 QUICK INSTALLATION GUIDE

## 📦 Install All Dependencies:

```bash
pip install -r requirements.txt
```

## 🔧 Manual Installation (if needed):

```bash
# Core AI & Google Integration
pip install google-generativeai python-dotenv

# Document Processing
pip install PyPDF2 pypdf

# LangChain RAG System
pip install langchain langchain-community langchain-google-genai langchain-text-splitters

# Vector Database & Embeddings
pip install chromadb sentence-transformers faiss-cpu

# Data Processing
pip install numpy pandas

# Optional Enhancements
pip install tiktoken unstructured
```

## ⚠️ Known Issues:

1. **LangChain Deprecation Warnings**: Normal and safe to ignore
2. **ChromaDB**: May require C++ build tools on some systems
3. **FAISS**: CPU version included for compatibility

## ✅ Verify Installation:

```bash
python -c "from rag_selector import RAGSelector; print('✅ Installation successful!')"
```

## 🎯 Ready to Run:

```bash
python rag_selector.py
```
