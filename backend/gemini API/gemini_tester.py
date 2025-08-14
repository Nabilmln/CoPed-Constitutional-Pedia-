"""
Document Understanding Project dengan Gemini API
API Key: AIzaSyDPVaD6JBzYf6fTzmPeR3eUck0Mm62LvHM
Model: gemini-2.5-flash

Cara penggunaan:
1. python gemini_tester.py - untuk testing dasar
2. python gemini_tester.py chat - untuk chat mode
3. python gemini_tester.py pdf - untuk analisis PDF
"""

import os
import sys
import PyPDF2
import google.generativeai as genai
from document_cache import DocumentCache
from multi_document_processor import MultiDocumentProcessor
from dataset_builder import DatasetBuilder

class GeminiTester:
    def __init__(self):
        self.api_key = 'AIzaSyDPVaD6JBzYf6fTzmPeR3eUck0Mm62LvHM'
        self.client = None
        self.cache = DocumentCache()
        self.multi_processor = MultiDocumentProcessor()  # ✨ New multi-document support
        self.dataset_builder = DatasetBuilder()  # 🎯 NEW: Combined dataset learning  # Initialize document cache
        self.setup_api()
    
    def setup_api(self):
        """Setup Gemini API"""
        try:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel('gemini-2.5-flash')
            print("✓ Gemini API berhasil diinisialisasi")
            return True
        except Exception as e:
            print(f"❌ Error setup API: {e}")
            return False
    
    def test_connection(self):
        """Test koneksi API"""
        print("\n=== Testing Koneksi API ===")
        try:
            response = self.client.generate_content("Halo, apa kabar?")
            print("✓ Koneksi berhasil!")
            print(f"Response: {response.text}")
            return True
        except Exception as e:
            print(f"❌ Koneksi gagal: {e}")
            return False
    
    def ask_question(self, question):
        """Tanya jawab sederhana"""
        try:
            response = self.client.generate_content(question)
            return response.text
        except Exception as e:
            return f"Error: {e}"
    
    def extract_pdf_text(self, pdf_path):
        """Extract text dari PDF dengan caching"""
        return self.cache.get_document_text(pdf_path)
    
    def analyze_document(self, text, question):
        """Analisis dokumen dengan pertanyaan"""
        # Batasi teks untuk menghindari token limit
        max_chars = 8000
        if len(text) > max_chars:
            text = text[:max_chars] + "...\n[Dokumen dipotong karena terlalu panjang]"
        
        prompt = f"""
        Berdasarkan dokumen berikut, jawab pertanyaan: {question}

        Dokumen:
        {text}

        Berikan jawaban yang detail dan akurat berdasarkan isi dokumen.
        Jika informasi tidak tersedia, jelaskan hal tersebut.
        """
        
        return self.ask_question(prompt)
    
    def evaluate_accuracy(self, text, test_questions):
        """Evaluasi akurasi jawaban AI dengan pertanyaan test"""
        print("\n=== EVALUASI AKURASI JAWABAN AI ===")
        print(f"Menguji {len(test_questions)} pertanyaan...")
        
        results = []
        
        for i, (question, expected_answer) in enumerate(test_questions, 1):
            print(f"\n[{i}/{len(test_questions)}] Testing: {question}")
            
            # Dapatkan jawaban dari AI
            ai_answer = self.analyze_document(text, question)
            
            # Evaluasi manual atau otomatis
            print(f"\n🤖 Jawaban AI:")
            print("-" * 40)
            print(ai_answer)
            print("-" * 40)
            
            print(f"\n📚 Jawaban yang Diharapkan:")
            print("-" * 40)
            print(expected_answer)
            print("-" * 40)
            
            # Input manual scoring
            while True:
                try:
                    score = input("\n📊 Berikan skor akurasi (0-10): ")
                    score = int(score)
                    if 0 <= score <= 10:
                        break
                    else:
                        print("Skor harus antara 0-10")
                except ValueError:
                    print("Masukkan angka yang valid")
            
            notes = input("💭 Catatan evaluasi (opsional): ")
            
            result = {
                'question': question,
                'expected': expected_answer,
                'ai_answer': ai_answer,
                'score': score,
                'notes': notes
            }
            results.append(result)
            
            print(f"✅ Skor: {score}/10")
        
        # Tampilkan hasil evaluasi
        self.show_evaluation_results(results)
        return results
    
    def auto_evaluate_accuracy(self, text, test_questions):
        """Evaluasi otomatis menggunakan AI untuk menilai AI"""
        print("\n=== EVALUASI OTOMATIS AKURASI ===")
        print(f"Menguji {len(test_questions)} pertanyaan dengan evaluasi otomatis...")
        
        results = []
        
        for i, (question, expected_answer) in enumerate(test_questions, 1):
            print(f"\n[{i}/{len(test_questions)}] Testing: {question}")
            
            # Dapatkan jawaban dari AI
            ai_answer = self.analyze_document(text, question)
            
            # Evaluasi otomatis menggunakan AI lain
            evaluation_prompt = f"""
            Sebagai evaluator yang objektif, bandingkan jawaban AI dengan jawaban yang diharapkan.
            Berikan skor 0-10 dan penjelasan singkat.

            PERTANYAAN: {question}

            JAWABAN AI:
            {ai_answer}

            JAWABAN YANG DIHARAPKAN:
            {expected_answer}

            Kriteria evaluasi:
            - Akurasi faktual (40%)
            - Kelengkapan informasi (30%) 
            - Kejelasan penjelasan (20%)
            - Relevansi dengan pertanyaan (10%)

            Format jawaban:
            SKOR: [0-10]
            PENJELASAN: [penjelasan singkat]
            """
            
            evaluation = self.ask_question(evaluation_prompt)
            
            # Extract score dari evaluasi
            score = self.extract_score_from_evaluation(evaluation)
            
            print(f"🤖 Jawaban AI: {ai_answer[:100]}...")
            print(f"📚 Expected: {expected_answer[:100]}...")
            print(f"🎯 Auto Score: {score}/10")
            print(f"📝 Evaluasi: {evaluation}")
            
            result = {
                'question': question,
                'expected': expected_answer,
                'ai_answer': ai_answer,
                'score': score,
                'evaluation': evaluation
            }
            results.append(result)
        
        self.show_evaluation_results(results)
        return results
    
    def extract_score_from_evaluation(self, evaluation_text):
        """Extract skor dari teks evaluasi"""
        import re
        
        # Cari pattern "SKOR: X" atau "Score: X"
        patterns = [
            r'SKOR:\s*(\d+)',
            r'Score:\s*(\d+)', 
            r'skor\s*(\d+)',
            r'score\s*(\d+)',
            r'(\d+)/10',
            r'(\d+)\s*dari\s*10'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, evaluation_text, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                return min(max(score, 0), 10)  # Ensure 0-10 range
        
        # Fallback: return 5 if no score found
        return 5
    
    def show_evaluation_results(self, results):
        """Tampilkan hasil evaluasi"""
        print("\n" + "="*60)
        print("📊 HASIL EVALUASI AKURASI")
        print("="*60)
        
        total_score = sum(r['score'] for r in results)
        avg_score = total_score / len(results) if results else 0
        
        print(f"Total Pertanyaan: {len(results)}")
        print(f"Rata-rata Skor: {avg_score:.1f}/10")
        print(f"Persentase Akurasi: {(avg_score/10)*100:.1f}%")
        
        # Kategorisasi hasil
        excellent = sum(1 for r in results if r['score'] >= 9)
        good = sum(1 for r in results if 7 <= r['score'] < 9)
        fair = sum(1 for r in results if 5 <= r['score'] < 7)
        poor = sum(1 for r in results if r['score'] < 5)
        
        print(f"\n📈 Distribusi Skor:")
        print(f"Excellent (9-10): {excellent} ({excellent/len(results)*100:.1f}%)")
        print(f"Good (7-8): {good} ({good/len(results)*100:.1f}%)")
        print(f"Fair (5-6): {fair} ({fair/len(results)*100:.1f}%)")
        print(f"Poor (0-4): {poor} ({poor/len(results)*100:.1f}%)")
        
        # Pertanyaan dengan skor terendah
        lowest_scores = sorted(results, key=lambda x: x['score'])[:3]
        print(f"\n⚠️  Pertanyaan dengan Skor Terendah:")
        for i, result in enumerate(lowest_scores, 1):
            print(f"{i}. \"{result['question']}\" - Skor: {result['score']}/10")
    
    def load_test_questions(self):
        """Load predefined test questions untuk UUD 1945"""
        return [
            ("Apa isi pasal 1 ayat 1 UUD 1945?", 
             "Pasal 1 ayat 1 UUD 1945 berbunyi: 'Negara Indonesia ialah Negara Kesatuan, yang berbentuk Republik.' Pasal ini menegaskan bentuk negara Indonesia sebagai negara kesatuan dan bentuk pemerintahan sebagai republik."),
            
            ("Apa yang dimaksud dengan kedaulatan rakyat dalam UUD 1945?", 
             "Kedaulatan rakyat dalam UUD 1945 diatur dalam Pasal 1 ayat 2 yang menyatakan 'Kedaulatan berada di tangan rakyat dan dilaksanakan menurut Undang-Undang Dasar.' Ini berarti kekuasaan tertinggi berada di tangan rakyat dan pelaksanaannya diatur sesuai konstitusi."),
            
            ("Bagaimana ketentuan tentang hak asasi manusia dalam UUD 1945?", 
             "Hak asasi manusia dalam UUD 1945 diatur secara komprehensif dalam Bab XA (Pasal 28A-28J). Mencakup hak untuk hidup, hak kemerdekaan, hak atas pendidikan, hak beragama, dan berbagai hak fundamental lainnya dengan pembatasan yang ditetapkan undang-undang."),
            
            ("Apa yang dimaksud dengan sistem pemerintahan presidensial dalam UUD 1945?", 
             "Sistem pemerintahan presidensial dalam UUD 1945 berarti Presiden adalah kepala negara sekaligus kepala pemerintahan. Presiden memiliki kekuasaan eksekutif yang tidak bergantung pada parlemen, dipilih langsung oleh rakyat, dan bertanggung jawab kepada rakyat melalui MPR."),
            
            ("Bagaimana pembagian kekuasaan negara dalam UUD 1945?", 
             "UUD 1945 menganut sistem pembagian kekuasaan dengan prinsip checks and balances: Kekuasaan Eksekutif (Presiden), Kekuasaan Legislatif (DPR, DPD, MPR), Kekuasaan Yudikatif (MA, MK, KY), serta lembaga negara lainnya yang saling mengawasi dan menyeimbangkan.")
        ]
    
    def accuracy_test_mode(self):
        """Mode untuk testing akurasi"""
        print("\n=== ACCURACY TEST MODE ===")
        
        pdf_path = "data/UUD1945.pdf"
        if not os.path.exists(pdf_path):
            print(f"❌ File PDF tidak ditemukan: {pdf_path}")
            return
        
        print("📄 Mengekstrak teks dari PDF...")
        text = self.extract_pdf_text(pdf_path)
        
        if not text:
            print("❌ Gagal mengekstrak teks dari PDF")
            return
        
        print(f"✓ Berhasil mengekstrak {len(text)} karakter")
        
        # Load test questions
        test_questions = self.load_test_questions()
        
        print(f"\n📝 Tersedia {len(test_questions)} pertanyaan test")
        print("\nPilih mode evaluasi:")
        print("1. Manual - Anda menilai sendiri")
        print("2. Otomatis - AI menilai AI")
        print("3. Custom - Tambah pertanyaan sendiri")
        
        choice = input("\nPilihan (1/2/3): ").strip()
        
        if choice == '1':
            results = self.evaluate_accuracy(text, test_questions)
        elif choice == '2':
            results = self.auto_evaluate_accuracy(text, test_questions)
        elif choice == '3':
            custom_questions = self.get_custom_questions()
            if custom_questions:
                results = self.evaluate_accuracy(text, custom_questions)
            else:
                print("Tidak ada pertanyaan custom yang ditambahkan.")
                return
        else:
            print("Pilihan tidak valid.")
            return
        
        # Save results
        self.save_evaluation_results(results)
    
    def get_custom_questions(self):
        """Mendapatkan pertanyaan custom dari user"""
        questions = []
        print("\n=== TAMBAH PERTANYAAN CUSTOM ===")
        print("Masukkan pertanyaan dan jawaban yang diharapkan.")
        print("Ketik 'done' pada pertanyaan untuk selesai.\n")
        
        while True:
            question = input("Pertanyaan: ").strip()
            if question.lower() == 'done':
                break
            
            if question:
                expected = input("Jawaban yang diharapkan: ").strip()
                if expected:
                    questions.append((question, expected))
                    print(f"✅ Pertanyaan {len(questions)} ditambahkan\n")
        
        return questions
    
    def save_evaluation_results(self, results):
        """Simpan hasil evaluasi ke file"""
        import json
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Hasil evaluasi disimpan ke: {filename}")
        except Exception as e:
            print(f"❌ Error menyimpan file: {e}")
    
    def chat_mode(self):
        """Mode chat interaktif"""
        print("\n=== CHAT MODE ===")
        print("Tanya apa saja ke Gemini!")
        print("Ketik 'quit' untuk keluar\n")
        
        while True:
            try:
                question = input("Anda: ")
                
                if question.lower().strip() in ['quit', 'exit', 'q', 'keluar']:
                    print("Sampai jumpa!")
                    break
                
                if question.strip() == "":
                    continue
                
                print("\nGemini: ", end="")
                answer = self.ask_question(question)
                print(answer)
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n\nChat dihentikan. Sampai jumpa!")
                break
    
    def pdf_mode(self):
        """Mode analisis PDF"""
        print("\n=== PDF ANALYSIS MODE ===")
        
        pdf_path = "data/UUD1945.pdf"
        if not os.path.exists(pdf_path):
            print(f"❌ File PDF tidak ditemukan: {pdf_path}")
            return
        
        print("📄 Mengekstrak teks dari PDF...")
        text = self.extract_pdf_text(pdf_path)
        
        if not text:
            print("❌ Gagal mengekstrak teks dari PDF")
            return
        
        print(f"✓ Berhasil mengekstrak {len(text)} karakter")
        print("✓ Siap untuk analisis dokumen UUD 1945!")
        print("\nTanya apa saja tentang UUD 1945. Ketik 'quit' untuk keluar\n")
        
        while True:
            try:
                question = input("Pertanyaan: ")
                
                if question.lower().strip() in ['quit', 'exit', 'q', 'keluar']:
                    print("Sampai jumpa!")
                    break
                
                if question.strip() == "":
                    continue
                
                print("\n🔍 Menganalisis dokumen...")
                answer = self.analyze_document(text, question)
                
                print("\n📋 Jawaban:")
                print("=" * 60)
                print(answer)
                print("=" * 60)
                print()
                
            except KeyboardInterrupt:
                print("\n\nAnalisis dihentikan. Sampai jumpa!")
                break
    
    def show_help(self):
        """Tampilkan bantuan"""
        print("""
=== GEMINI DOCUMENT UNDERSTANDING TESTER ===

Cara penggunaan:
1. python gemini_tester.py           - Testing koneksi API
2. python gemini_tester.py chat      - Mode chat dengan Gemini
3. python gemini_tester.py pdf       - Analisis dokumen PDF UUD 1945
4. python gemini_tester.py accuracy  - Test akurasi jawaban AI
5. python gemini_tester.py multidoc  - ✨ Multi-document analysis 
6. python gemini_tester.py compare   - ✨ Single vs Multi comparison
7. python gemini_tester.py dataset   - 🎯 Combined dataset learning (RECOMMENDED!)
8. python gemini_tester.py rebuild   - 🔨 Force rebuild dataset cache
9. python gemini_tester.py help      - Tampilkan bantuan ini

API Key: AIzaSyDPVaD6JBzYf6fTzmPeR3eUck0Mm62LvHM
Model: gemini-2.5-flash

🎯 DATASET MODE (RECOMMENDED):
- Menggabungkan semua PDF menjadi satu dataset besar
- Caching otomatis untuk performa maksimal 
- AI "belajar" dari dataset gabungan secara persistent
- Jawaban berdasarkan pengetahuan yang sudah dipelajari
- Mode interaktif untuk tanya jawab

Multi-Document Features:
- Analisis menggunakan multiple PDF files
- Auto-discovery dokumen dalam folder data/
- Context enrichment dari berbagai sumber
- Perbandingan single vs multi-document analysis

Contoh pertanyaan untuk mode PDF:
- "Apa isi pasal 1 ayat 1 UUD 1945?"
- "Apa yang dimaksud dengan kedaulatan rakyat?"
- "Bagaimana ketentuan hak asasi manusia dalam UUD 1945?"
- "Apa sistem pemerintahan menurut UUD 1945?"

Mode Accuracy Testing:
- Manual evaluation: Anda menilai jawaban AI secara manual
- Auto evaluation: AI menilai jawaban AI lainnya  
- Custom questions: Tambah pertanyaan test sendiri
- Hasil disimpan dalam file JSON dengan timestamp
        """)

def main():
    """Main function - Enhanced with RAG Selector integration"""
    tester = GeminiTester()
    
    if len(sys.argv) < 2:
        # Default: Show main menu with RAG Selector option
        print("🤖 GEMINI TESTER - Enhanced Multi-Document Analysis")
        print("=" * 55)
        print("MODERN RAG SYSTEMS:")
        print("1. RAG System Selector (RECOMMENDED)")
        print("   - Native Multi-Document RAG (96.8% accuracy)")
        print("   - LangChain Enhanced RAG (63.6% accuracy)")
        print("   - Comparison mode")
        print("")
        print("LEGACY MODES:")
        print("2. Test connection")
        print("3. Show help")
        print("")
        print("COMMAND LINE OPTIONS:")
        print("python gemini_tester.py rag      - Launch RAG Selector")
        print("python gemini_tester.py dataset  - Legacy dataset mode")
        print("python gemini_tester.py help     - Show all options")
        print("=" * 55)
        
        while True:
            choice = input("\nSelect option (1-3, or 'rag'): ").strip().lower()
            
            if choice == '1' or choice == 'rag':
                try:
                    from rag_selector import RAGSelector
                    print("\n🚀 Launching RAG System Selector...")
                    selector = RAGSelector()
                    selector.run()
                    break
                except ImportError:
                    print("❌ RAG Selector not found. Please ensure rag_selector.py exists.")
                except Exception as e:
                    print(f"❌ Error running RAG Selector: {e}")
            elif choice == '2':
                tester.test_connection()
                break
            elif choice == '3':
                tester.show_help()
                break
            else:
                print("❌ Invalid choice. Please select 1-3 or 'rag'.")
    
    elif sys.argv[1] == 'rag':
        # Direct launch of RAG selector
        try:
            from rag_selector import RAGSelector
            print("🚀 Launching RAG System Selector...")
            selector = RAGSelector()
            selector.run()
        except ImportError:
            print("❌ RAG Selector not found. Please ensure rag_selector.py exists.")
        except Exception as e:
            print(f"❌ Error running RAG Selector: {e}")
    
    elif sys.argv[1] == 'chat':
        tester.chat_mode()
    
    elif sys.argv[1] == 'pdf':
        tester.pdf_mode()
    
    elif sys.argv[1] == 'accuracy':
        tester.accuracy_test_mode()
        
    elif sys.argv[1] == 'multidoc':
        # ✨ NEW: Multi-document analysis mode
        print("🚀 Multi-Document Analysis Mode")
        processor = MultiDocumentProcessor()
        
        # Auto-discover and process documents
        discovered = processor.discover_documents()
        processor.document_sets.update(discovered)
        
        print("\n📚 Available Document Sets:")
        for set_name, set_info in processor.document_sets.items():
            print(f"  {set_name}: {len(set_info['files'])} files")
        
        # Interactive analysis
        while True:
            question = input("\n🔍 Enter question (or 'quit'): ")
            if question.lower() == 'quit':
                break
            
            doc_set = input("📚 Document set (default: UUD1945): ") or "UUD1945"
            
            if doc_set in processor.document_sets:
                result = processor.analyze_with_multidoc(question, doc_set)
                if isinstance(result, dict):
                    print(f"\n📋 ANSWER ({', '.join(result['source_info']['source_files'])}):")
                    print(result['answer'])
                else:
                    print(f"❌ Error: {result}")
            else:
                print(f"❌ Document set '{doc_set}' not found")
    
    elif sys.argv[1] == 'compare':
        # ✨ NEW: Single vs Multi-document comparison
        print("⚖️  Comparison Mode: Single vs Multi-Document")
        processor = MultiDocumentProcessor()
        
        question = input("🔍 Enter question to compare: ")
        comparison = processor.compare_single_vs_multi(question)
        
        print(f"\n📊 COMPARISON RESULTS:")
        print(f"\n📄 SINGLE DOCUMENT:")
        print(f"Source: {comparison['single_document']['source']}")
        print(f"Answer: {comparison['single_document']['answer'][:300]}...")
        
        print(f"\n📚 MULTI-DOCUMENT:")
        print(f"Sources: {comparison['multi_document']['sources']}")
        print(f"Answer: {comparison['multi_document']['answer'][:300]}...")
    
    elif sys.argv[1] == 'dataset':
        # 🎯 ENHANCED: Combined dataset learning mode dengan multi-method analysis
        print("🎯 Enhanced Dataset Learning Mode (LEGACY)")
        print("⚠️  Recommendation: Use 'python gemini_tester.py rag' for modern interface")
        
        builder = DatasetBuilder()
        
        # Build dataset
        print("📚 Building/Loading combined dataset...")
        dataset = builder.build_combined_dataset()
        
        if dataset:
            print(builder.get_dataset_summary())
            builder.interactive_qa_mode_enhanced()
        else:
            print("❌ Failed to build dataset")
    
    elif sys.argv[1] == 'rebuild':
        # 🔨 NEW: Force rebuild dataset
        print("🔨 Force Rebuilding Dataset...")
        builder = DatasetBuilder()
        dataset = builder.build_combined_dataset(force_rebuild=True)
        
        if dataset:
            print(builder.get_dataset_summary())
            
            # Quick test
            test_question = "Apa isi pasal 1 ayat 1 UUD 1945?"
            print(f"\n🧪 Quick test: {test_question}")
            result = builder.answer_question_from_dataset(test_question)
            if isinstance(result, dict):
                print(f"💬 {result['answer']}")
            else:
                print(f"❌ {result}")
        else:
            print("❌ Failed to rebuild dataset")
        
        if dataset:
            print(builder.get_dataset_summary())
            
            # Quick test
            test_question = "Apa isi pasal 1 ayat 1 UUD 1945?"
            print(f"\n🧪 Quick test: {test_question}")
            result = builder.answer_question_from_dataset(test_question)
            if isinstance(result, dict):
                print(f"💬 {result['answer']}")
            else:
                print(f"❌ {result}")
        else:
            print("❌ Failed to rebuild dataset")
    
    elif sys.argv[1] == 'help':
        tester.show_help()
    
    else:
        print("Argumen tidak dikenal. Gunakan 'help' untuk bantuan.")

if __name__ == "__main__":
    main()
