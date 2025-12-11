"""
AI-Powered Code Search Engine with Caching and Advanced Metrics
A semantic code search system with sub-50ms cached queries
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple
import hashlib
from collections import OrderedDict
from datetime import datetime
import threading

# AI and Search Libraries
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Web Framework
from flask import Flask, request, jsonify

class LRUCache:
    """Least Recently Used Cache implementation"""
    def __init__(self, capacity: int = 1000):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.hits = 0
        self.misses = 0
        self.lock = threading.Lock()
    
    def get(self, key: str):
        with self.lock:
            if key in self.cache:
                self.hits += 1
                self.cache.move_to_end(key)
                return self.cache[key]
            self.misses += 1
            return None
    
    def put(self, key: str, value):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)
    
    def get_stats(self):
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total_queries': total,
            'hit_rate': round(hit_rate, 2),
            'cache_size': len(self.cache)
        }

class MetricsTracker:
    """Track search engine performance metrics"""
    def __init__(self):
        self.total_queries = 0
        self.total_search_time = 0
        self.queries_under_50ms = 0
        self.queries_under_200ms = 0
        self.query_history = []
        self.lock = threading.Lock()
    
    def record_query(self, query: str, search_time_ms: float, from_cache: bool):
        with self.lock:
            self.total_queries += 1
            self.total_search_time += search_time_ms
            
            if search_time_ms < 50:
                self.queries_under_50ms += 1
            if search_time_ms < 200:
                self.queries_under_200ms += 1
            
            self.query_history.append({
                'query': query,
                'time_ms': search_time_ms,
                'cached': from_cache,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 1000 queries in memory
            if len(self.query_history) > 1000:
                self.query_history.pop(0)
    
    def get_stats(self):
        with self.lock:
            avg_time = (self.total_search_time / self.total_queries) if self.total_queries > 0 else 0
            sub_50_rate = (self.queries_under_50ms / self.total_queries * 100) if self.total_queries > 0 else 0
            sub_200_rate = (self.queries_under_200ms / self.total_queries * 100) if self.total_queries > 0 else 0
            
            return {
                'total_queries': self.total_queries,
                'average_search_time_ms': round(avg_time, 2),
                'queries_under_50ms': self.queries_under_50ms,
                'queries_under_200ms': self.queries_under_200ms,
                'sub_50ms_rate': round(sub_50_rate, 2),
                'sub_200ms_rate': round(sub_200_rate, 2),
                'recent_queries': self.query_history[-10:]
            }

class CodeSearchEngine:
    def __init__(self, index_dir="./code_index"):
        """Initialize the search engine with embedding model and storage"""
        print("🚀 Initializing AI-Powered Code Search Engine...")
        
        # Initialize the AI model for semantic understanding
        print("📥 Loading AI model (this may take a minute)...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ AI model loaded successfully!")
        
        # Storage paths
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(exist_ok=True)
        
        # Code storage
        self.code_snippets = []
        self.embeddings = None
        self.faiss_index = None
        
        # Caching and metrics
        self.cache = LRUCache(capacity=1000)
        self.metrics = MetricsTracker()
        
        # Supported file extensions
        self.supported_extensions = {
            '.py', '.java', '.cpp', '.c', '.js', '.jsx', '.ts', '.tsx',
            '.go', '.rs', '.rb', '.php', '.cs', '.swift', '.kt', '.scala',
            '.html', '.css', '.sql', '.sh', '.yaml', '.json', '.h', '.hpp'
        }
        
        # Metrics
        self.total_files_indexed = 0
        self.total_lines_indexed = 0
        self.total_repositories = 0
        
    def index_repository(self, repo_path: str):
        """Index all code files in a repository"""
        repo_path = Path(repo_path)
        
        if not repo_path.exists():
            print(f"❌ Error: Path {repo_path} does not exist")
            return
        
        print(f"\n📂 Indexing repository: {repo_path.name}")
        self.total_repositories += 1
        
        files_in_repo = 0
        lines_in_repo = 0
        
        # Walk through all files
        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in self.supported_extensions:
                # Skip common directories
                if any(skip in file_path.parts for skip in ['node_modules', '.git', '__pycache__', 'venv', 'dist', 'build', '.venv']):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        # Index in chunks of 50 lines
                        chunk_size = 50
                        for i in range(0, len(lines), chunk_size):
                            chunk_lines = lines[i:i+chunk_size]
                            chunk_content = '\n'.join(chunk_lines)
                            
                            if chunk_content.strip():
                                self.code_snippets.append({
                                    'file': str(file_path.relative_to(repo_path.parent)),
                                    'repo': repo_path.name,
                                    'content': chunk_content,
                                    'line_start': i + 1,
                                    'line_end': i + len(chunk_lines)
                                })
                        
                        files_in_repo += 1
                        lines_in_repo += len(lines)
                        
                except Exception as e:
                    pass  # Skip problematic files
        
        self.total_files_indexed += files_in_repo
        self.total_lines_indexed += lines_in_repo
        
        print(f"✅ Indexed {files_in_repo} files ({lines_in_repo:,} lines) from {repo_path.name}")
    
    def build_search_index(self):
        """Build FAISS index for fast similarity search"""
        if not self.code_snippets:
            print("❌ No code snippets to index!")
            return
        
        print(f"\n🔨 Building search index for {len(self.code_snippets)} code snippets...")
        start_time = time.time()
        
        # Generate embeddings for all code snippets
        texts = [snippet['content'] for snippet in self.code_snippets]
        
        print("🧠 Generating AI embeddings...")
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Create FAISS index for fast search
        print("⚡ Creating FAISS index...")
        dimension = self.embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatL2(dimension)
        self.faiss_index.add(self.embeddings.astype('float32'))
        
        build_time = time.time() - start_time
        print(f"✅ Search index built in {build_time:.2f} seconds!")
        
        # Save index to disk
        self.save_index()
    
    def save_index(self):
        """Save index and metadata to disk"""
        print("💾 Saving index to disk...")
        
        # Save FAISS index
        faiss.write_index(self.faiss_index, str(self.index_dir / "code.index"))
        
        # Save metadata
        with open(self.index_dir / "metadata.json", 'w') as f:
            json.dump({
                'code_snippets': self.code_snippets,
                'total_files': self.total_files_indexed,
                'total_lines': self.total_lines_indexed,
                'total_repositories': self.total_repositories
            }, f)
        
        print("✅ Index saved successfully!")
    
    def load_index(self):
        """Load index from disk"""
        index_file = self.index_dir / "code.index"
        metadata_file = self.index_dir / "metadata.json"
        
        if not index_file.exists() or not metadata_file.exists():
            print("⚠️  No existing index found. Please index repositories first.")
            return False
        
        print("📥 Loading index from disk...")
        
        # Load FAISS index
        self.faiss_index = faiss.read_index(str(index_file))
        
        # Load metadata
        with open(metadata_file, 'r') as f:
            data = json.load(f)
            self.code_snippets = data['code_snippets']
            self.total_files_indexed = data['total_files']
            self.total_lines_indexed = data['total_lines']
            self.total_repositories = data['total_repositories']
        
        print(f"✅ Loaded index with {len(self.code_snippets)} code snippets")
        print(f"📊 Indexed: {self.total_repositories} repos, {self.total_files_indexed} files, {self.total_lines_indexed:,} lines")
        return True
    
    def search(self, query: str, top_k: int = 10) -> Tuple[List[Dict], float, bool]:
        """Search for code snippets similar to the query"""
        if self.faiss_index is None:
            return [], 0, False
        
        # Generate cache key
        cache_key = hashlib.md5(f"{query}:{top_k}".encode()).hexdigest()
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            search_time = cached_result['search_time']
            results = cached_result['results']
            self.metrics.record_query(query, search_time, from_cache=True)
            return results, search_time, True
        
        # Perform actual search
        start_time = time.time()
        
        # Generate embedding for query
        query_embedding = self.model.encode([query])
        
        # Search in FAISS index
        distances, indices = self.faiss_index.search(query_embedding.astype('float32'), top_k)
        
        # Prepare results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.code_snippets):
                snippet = self.code_snippets[idx]
                results.append({
                    'file': snippet['file'],
                    'repo': snippet['repo'],
                    'content': snippet['content'],
                    'line_start': snippet['line_start'],
                    'line_end': snippet['line_end'],
                    'similarity_score': float(1 / (1 + distance))
                })
        
        search_time = (time.time() - start_time) * 1000  # milliseconds
        
        # Cache the result
        self.cache.put(cache_key, {
            'results': results,
            'search_time': search_time
        })
        
        # Record metrics
        self.metrics.record_query(query, search_time, from_cache=False)
        
        return results, search_time, False

# Initialize Flask app
app = Flask(__name__)
search_engine = CodeSearchEngine()

@app.route('/search', methods=['GET'])
def search_api():
    """API endpoint for searching code"""
    query = request.args.get('q', '')
    top_k = int(request.args.get('limit', 10))
    
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400
    
    results, search_time, from_cache = search_engine.search(query, top_k)
    
    return jsonify({
        'query': query,
        'results': results,
        'count': len(results),
        'search_time_ms': round(search_time, 2),
        'cached': from_cache,
        'indexed_files': search_engine.total_files_indexed,
        'indexed_lines': search_engine.total_lines_indexed
    })

@app.route('/stats', methods=['GET'])
def stats_api():
    """API endpoint for getting comprehensive statistics"""
    cache_stats = search_engine.cache.get_stats()
    metrics_stats = search_engine.metrics.get_stats()
    
    return jsonify({
        'index': {
            'total_repositories': search_engine.total_repositories,
            'total_files': search_engine.total_files_indexed,
            'total_lines': search_engine.total_lines_indexed,
            'total_snippets': len(search_engine.code_snippets)
        },
        'cache': cache_stats,
        'performance': metrics_stats
    })

@app.route('/metrics', methods=['GET'])
def metrics_api():
    """Detailed performance metrics endpoint"""
    return jsonify(search_engine.metrics.get_stats())

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'AI-Powered Code Search Engine with Caching',
        'version': '2.0',
        'endpoints': {
            '/search?q=<query>&limit=<number>': 'Search for code',
            '/stats': 'Get comprehensive statistics',
            '/metrics': 'Get performance metrics'
        }
    })

def simulate_load_test(num_queries=1000):
    """Simulate load to generate realistic metrics"""
    print(f"\n🔥 Running load test with {num_queries} queries...")
    
    test_queries = [
        "authentication login", "database connection", "error handling",
        "http request", "file upload", "user validation", "api endpoint",
        "cache implementation", "data processing", "security check",
        "unit test", "configuration", "logging debug", "async function",
        "json parsing", "form validation", "session management"
    ]
    
    start_time = time.time()
    
    for i in range(num_queries):
        query = test_queries[i % len(test_queries)]
        search_engine.search(query, top_k=5)
        
        if (i + 1) % 100 == 0:
            print(f"  Completed {i + 1}/{num_queries} queries...")
    
    total_time = time.time() - start_time
    
    print(f"\n✅ Load test completed!")
    print(f"📊 Results:")
    print(f"  Total queries: {num_queries}")
    print(f"  Total time: {total_time:.2f} seconds")
    print(f"  Queries per second: {num_queries/total_time:.2f}")
    
    # Show metrics
    cache_stats = search_engine.cache.get_stats()
    metrics_stats = search_engine.metrics.get_stats()
    
    print(f"\n📈 Cache Performance:")
    print(f"  Cache hit rate: {cache_stats['hit_rate']:.2f}%")
    print(f"  Cache hits: {cache_stats['hits']}")
    print(f"  Cache misses: {cache_stats['misses']}")
    
    print(f"\n⚡ Search Performance:")
    print(f"  Average search time: {metrics_stats['average_search_time_ms']:.2f}ms")
    print(f"  Queries under 50ms: {metrics_stats['queries_under_50ms']} ({metrics_stats['sub_50ms_rate']:.1f}%)")
    print(f"  Queries under 200ms: {metrics_stats['queries_under_200ms']} ({metrics_stats['sub_200ms_rate']:.1f}%)")

def main():
    """Main function to run the search engine"""
    print("=" * 60)
    print("🔍 AI-POWERED CODE SEARCH ENGINE V2.0")
    print("    With Caching & Performance Metrics")
    print("=" * 60)
    
    # Try to load existing index
    if not search_engine.load_index():
        print("\n📝 No index found. Let's create one!")
        print("\nOptions:")
        print("1. Index a local directory")
        print("2. Clone and index GitHub repositories")
        
        choice = input("\nEnter your choice (1 or 2): ").strip()
        
        if choice == "1":
            path = input("Enter the path to your code directory (or '.' for current folder): ").strip()
            if path == ".":
                path = os.getcwd()
            
            if os.path.exists(path):
                search_engine.index_repository(path)
                if len(search_engine.code_snippets) > 0:
                    search_engine.build_search_index()
                else:
                    print("❌ No code files found to index!")
                    return
            else:
                print(f"❌ Path not found: {path}")
                return
        
        elif choice == "2":
            print("\n📥 Cloning popular repositories...")
            
            repos = [
                "https://github.com/torvalds/linux",
                "https://github.com/microsoft/vscode",
                "https://github.com/tensorflow/tensorflow"
            ]
            
            custom = input("\nEnter a GitHub URL to clone (or press Enter to use defaults): ").strip()
            if custom:
                repos = [custom]
            
            clone_dir = Path("./cloned_repos")
            clone_dir.mkdir(exist_ok=True)
            
            for repo_url in repos:
                repo_name = repo_url.split('/')[-1].replace('.git', '')
                repo_path = clone_dir / repo_name
                
                if not repo_path.exists():
                    print(f"\n📥 Cloning {repo_name}...")
                    os.system(f'git clone --depth 1 {repo_url} {repo_path}')
                
                search_engine.index_repository(repo_path)
            
            search_engine.build_search_index()
    
    # Print statistics
    print("\n" + "=" * 60)
    print("📊 INDEX STATISTICS")
    print("=" * 60)
    print(f"Repositories: {search_engine.total_repositories}")
    print(f"Files Indexed: {search_engine.total_files_indexed:,}")
    print(f"Lines of Code: {search_engine.total_lines_indexed:,}")
    print(f"Code Snippets: {len(search_engine.code_snippets):,}")
    
    # Interactive menu
    print("\n" + "=" * 60)
    print("🎯 MAIN MENU")
    print("=" * 60)
    print("Commands:")
    print("  search  - Interactive search mode")
    print("  load    - Run load test (generate metrics)")
    print("  api     - Start API server")
    print("  stats   - Show current statistics")
    print("  quit    - Exit")
    
    while True:
        command = input("\n> ").strip().lower()
        
        if command == 'quit':
            break
        
        elif command == 'search':
            print("\n🔍 SEARCH MODE (type 'back' to return to menu)")
            while True:
                query = input("\n🔍 Search: ").strip()
                
                if query.lower() == 'back':
                    break
                
                if not query:
                    continue
                
                results, search_time, from_cache = search_engine.search(query, top_k=5)
                
                cache_indicator = "💾 CACHED" if from_cache else "🔍 NEW"
                print(f"\n✅ Found {len(results)} results in {search_time:.2f}ms {cache_indicator}")
                print("-" * 60)
                
                for i, result in enumerate(results, 1):
                    print(f"\n[{i}] {result['file']} (lines {result['line_start']}-{result['line_end']})")
                    print(f"Similarity: {result['similarity_score']:.2%}")
                    print(f"Preview: {result['content'][:150]}...")
        
        elif command == 'load':
            num = input("How many queries to simulate? (default 1000): ").strip()
            num_queries = int(num) if num.isdigit() else 1000
            simulate_load_test(num_queries)
        
        elif command == 'api':
            print("\n🚀 Starting API server...")
            print("API available at http://localhost:5000")
            print("\nTry these endpoints:")
            print("  http://localhost:5000/search?q=authentication&limit=5")
            print("  http://localhost:5000/stats")
            print("  http://localhost:5000/metrics")
            app.run(debug=False, port=5000, threaded=True)
            break
        
        elif command == 'stats':
            cache_stats = search_engine.cache.get_stats()
            metrics_stats = search_engine.metrics.get_stats()
            
            print("\n" + "=" * 60)
            print("📊 CURRENT STATISTICS")
            print("=" * 60)
            print(f"\n📦 Index:")
            print(f"  Repositories: {search_engine.total_repositories}")
            print(f"  Files: {search_engine.total_files_indexed:,}")
            print(f"  Lines: {search_engine.total_lines_indexed:,}")
            print(f"  Snippets: {len(search_engine.code_snippets):,}")
            
            print(f"\n💾 Cache:")
            print(f"  Hit rate: {cache_stats['hit_rate']:.2f}%")
            print(f"  Total queries: {cache_stats['total_queries']}")
            print(f"  Cache size: {cache_stats['cache_size']}")
            
            print(f"\n⚡ Performance:")
            print(f"  Total queries: {metrics_stats['total_queries']}")
            print(f"  Avg search time: {metrics_stats['average_search_time_ms']:.2f}ms")
            print(f"  Queries < 50ms: {metrics_stats['queries_under_50ms']} ({metrics_stats['sub_50ms_rate']:.1f}%)")
            print(f"  Queries < 200ms: {metrics_stats['queries_under_200ms']} ({metrics_stats['sub_200ms_rate']:.1f}%)")
        
        else:
            print("❌ Unknown command. Type 'search', 'load', 'api', 'stats', or 'quit'")

if __name__ == "__main__":
    main()