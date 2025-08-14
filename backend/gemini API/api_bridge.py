import sys
import json
import time
import argparse
import os

# Add parent directory to path untuk import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    parser = argparse.ArgumentParser(description='RAG API Bridge for Node.js')
    parser.add_argument('--mode', choices=['native', 'langchain', 'auto'], default='auto')
    parser.add_argument('--question', required=True, help='Question to ask')
    parser.add_argument('--user-id', default='anonymous', help='User ID')
    parser.add_argument('--format', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    try:
        start_time = time.time()
        
        # Simulasi response untuk testing
        # Nanti akan diganti dengan actual RAG system calls
        
        if args.mode == 'native':
            response = {
                "answer": f"[Native RAG] Jawaban untuk pertanyaan: {args.question}",
                "system": "native",
                "accuracy": 96.8,
                "response_time": (time.time() - start_time) * 1000,
                "sources": ["UUD1945.pdf", "Konstitusi.pdf"],
                "gemini_model": "gemini-2.5-flash",
                "user_id": args.user_id
            }
            
        elif args.mode == 'langchain':
            response = {
                "answer": f"[LangChain RAG] Jawaban untuk pertanyaan: {args.question}",
                "system": "langchain", 
                "accuracy": 63.6,
                "response_time": (time.time() - start_time) * 1000,
                "sources": ["VectorDB_Result.txt"],
                "gemini_model": "gemini-1.5-flash",
                "user_id": args.user_id
            }
            
        else:  # auto mode
            legal_keywords = ['pasal', 'undang', 'konstitusi', 'hukum', 'peraturan', 'UUD', 'ayat']
            is_legal = any(keyword.lower() in args.question.lower() for keyword in legal_keywords)
            
            if is_legal:
                system = "native"
                accuracy = 96.8
                model = "gemini-2.5-flash"
                answer = f"[Auto-Selected Native RAG] Jawaban hukum untuk: {args.question}"
            else:
                system = "langchain"
                accuracy = 63.6
                model = "gemini-1.5-flash"
                answer = f"[Auto-Selected LangChain RAG] Jawaban umum untuk: {args.question}"
            
            response = {
                "answer": answer,
                "system": system,
                "accuracy": accuracy,
                "response_time": (time.time() - start_time) * 1000,
                "sources": ["AutoSelected_Source.pdf"],
                "gemini_model": model,
                "user_id": args.user_id,
                "auto_selected": True
            }
        
        if args.format == 'json':
            print(json.dumps(response, ensure_ascii=False, indent=2))
        else:
            print(response["answer"])
            
    except Exception as e:
        error_response = {
            "error": str(e),
            "system": args.mode,
            "user_id": args.user_id,
            "response_time": (time.time() - start_time) * 1000
        }
        
        if args.format == 'json':
            print(json.dumps(error_response, ensure_ascii=False, indent=2))
        else:
            print(f"Error: {str(e)}")
        
        sys.exit(1)

if __name__ == "__main__":
    main()