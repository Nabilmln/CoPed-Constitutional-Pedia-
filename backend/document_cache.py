"""
Document Cache System untuk optimasi frontend integration
Menyimpan hasil ekstraksi PDF agar tidak perlu re-process setiap request
"""

import os
import json
import hashlib
from datetime import datetime
import PyPDF2

class DocumentCache:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        self.ensure_cache_dir()
    
    def ensure_cache_dir(self):
        """Pastikan direktori cache ada"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def get_file_hash(self, file_path):
        """Generate hash untuk file PDF"""
        with open(file_path, 'rb') as f:
            content = f.read()
            return hashlib.md5(content).hexdigest()
    
    def get_cache_path(self, file_path):
        """Generate path untuk cache file"""
        file_hash = self.get_file_hash(file_path)
        filename = os.path.basename(file_path).replace('.pdf', '')
        return os.path.join(self.cache_dir, f"{filename}_{file_hash}.json")
    
    def is_cached(self, file_path):
        """Check apakah file sudah di-cache"""
        cache_path = self.get_cache_path(file_path)
        return os.path.exists(cache_path)
    
    def extract_and_cache(self, file_path):
        """Extract PDF dan simpan ke cache"""
        print(f"📄 Extracting dan caching: {file_path}")
        
        # Extract text
        text = self._extract_pdf_text(file_path)
        if not text:
            return None
        
        # Prepare cache data
        cache_data = {
            "file_path": file_path,
            "file_hash": self.get_file_hash(file_path),
            "extracted_text": text,
            "extraction_date": datetime.now().isoformat(),
            "character_count": len(text),
            "word_count": len(text.split()),
            "metadata": {
                "file_size": os.path.getsize(file_path),
                "file_name": os.path.basename(file_path)
            }
        }
        
        # Save to cache
        cache_path = self.get_cache_path(file_path)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Cache saved: {cache_path}")
        return cache_data
    
    def load_from_cache(self, file_path):
        """Load text dari cache"""
        cache_path = self.get_cache_path(file_path)
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Verify file hasn't changed
            current_hash = self.get_file_hash(file_path)
            if cache_data["file_hash"] != current_hash:
                print("⚠️ File changed, cache invalid")
                return None
            
            print(f"✅ Loaded from cache: {len(cache_data['extracted_text'])} characters")
            return cache_data
            
        except Exception as e:
            print(f"❌ Error loading cache: {e}")
            return None
    
    def get_document_text(self, file_path):
        """Get document text (from cache or extract)"""
        if self.is_cached(file_path):
            cache_data = self.load_from_cache(file_path)
            if cache_data:
                return cache_data["extracted_text"]
        
        # Cache miss or invalid, extract fresh
        cache_data = self.extract_and_cache(file_path)
        return cache_data["extracted_text"] if cache_data else None
    
    def _extract_pdf_text(self, pdf_path):
        """Internal method untuk extract PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return None
    
    def list_cached_documents(self):
        """List semua dokumen yang sudah di-cache"""
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
        
        documents = []
        for cache_file in cache_files:
            try:
                with open(os.path.join(self.cache_dir, cache_file), 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    documents.append({
                        "file_name": cache_data["metadata"]["file_name"],
                        "cached_date": cache_data["extraction_date"],
                        "character_count": cache_data["character_count"],
                        "word_count": cache_data["word_count"]
                    })
            except Exception as e:
                print(f"Error reading {cache_file}: {e}")
        
        return documents
    
    def clear_cache(self, file_path=None):
        """Clear cache (specific file atau semua)"""
        if file_path:
            cache_path = self.get_cache_path(file_path)
            if os.path.exists(cache_path):
                os.remove(cache_path)
                print(f"🗑️ Cache cleared for: {file_path}")
        else:
            # Clear all cache
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
            for cache_file in cache_files:
                os.remove(os.path.join(self.cache_dir, cache_file))
            print(f"🗑️ All cache cleared: {len(cache_files)} files")

def main():
    """Demo document caching"""
    print("=== DOCUMENT CACHE SYSTEM ===")
    
    cache = DocumentCache()
    
    # Test dengan UUD 1945
    pdf_path = "data/UUD1945.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    print(f"\n📂 Processing: {pdf_path}")
    
    # Get text (will cache if not cached)
    text = cache.get_document_text(pdf_path)
    
    if text:
        print(f"✅ Text extracted: {len(text)} characters")
        print(f"📝 Sample: {text[:200]}...")
        
        # Show cache info
        print(f"\n📊 Cached Documents:")
        docs = cache.list_cached_documents()
        for doc in docs:
            print(f"- {doc['file_name']}: {doc['character_count']} chars, cached on {doc['cached_date'][:19]}")
    
    # Demo API: simulate frontend calls
    print(f"\n🔄 Simulating Frontend Calls...")
    
    import time
    for i in range(3):
        start_time = time.time()
        text = cache.get_document_text(pdf_path)
        end_time = time.time()
        print(f"Call {i+1}: {end_time - start_time:.3f}s - {len(text)} chars")

if __name__ == "__main__":
    main()
