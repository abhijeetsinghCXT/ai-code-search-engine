# 🔍 AI-Powered Code Search Engine

A production-grade semantic code search system that indexes and searches through millions of lines of code using AI embeddings and vector similarity search.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue)

## 🎯 Project Highlights

- **13.3M+ lines of code indexed** across 43,346 files
- **40ms average query latency** (100% under 200ms SLA)
- **98.3% cache hit rate** with intelligent LRU caching
- **100% success rate** under load testing (1,000+ concurrent requests)
- **Production-ready** with Docker and Kubernetes configurations

## 🚀 Quick Start
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-code-search-engine.git
cd ai-code-search-engine

# Install dependencies
pip install -r requirements.txt

# Run the search engine
python code_search_engine.py
```

## 📊 Performance Metrics

| Metric | Achievement |
|--------|-------------|
| Lines Indexed | 13.3M+ |
| Files Processed | 43,346 |
| Code Snippets | 287,860 |
| Query Latency | 40ms avg |
| Cache Hit Rate | 98.3% |
| Load Test Success | 100% |

## 🛠️ Tech Stack

- **Languages:** Python, C++
- **AI/ML:** Sentence Transformers, FAISS
- **Web:** Flask REST API
- **Containerization:** Docker, Docker Compose
- **Orchestration:** Kubernetes with HPA
- **Testing:** asyncio, aiohttp

## 📡 API Endpoints

### Search Code
```bash
GET /search?q=<query>&limit=<number>
```

### Get Statistics
```bash
GET /stats
```

### Performance Metrics
```bash
GET /metrics
```

## 🐳 Docker Deployment
```bash
# Build image
docker build -t code-search-engine:latest .

# Run container
docker run -p 5000:5000 code-search-engine:latest
```

## ☸️ Kubernetes Deployment
```bash
# Deploy to cluster
kubectl apply -f kubernetes-deployment.yaml

# Check status
kubectl get pods -n code-search
```

**Features:**
- Horizontal Pod Autoscaling (2-10 replicas)
- Load balancing
- Health checks
- 99.95% uptime capability

## 🧪 Load Testing
```bash
# Install dependencies
pip install aiohttp

# Run load test
python load_test.py
```

## 📈 Key Features

- ✅ **Semantic Search:** AI-powered code understanding
- ✅ **High Performance:** Sub-50ms cached queries
- ✅ **Scalable Architecture:** Kubernetes-ready with autoscaling
- ✅ **Production-Ready:** Docker containerization
- ✅ **Comprehensive Metrics:** Real-time performance tracking

## 🎓 What I Learned

- Building scalable search infrastructure
- Implementing efficient caching strategies (98.3% hit rate)
- Vector similarity search with FAISS
- Kubernetes orchestration and autoscaling
- Performance optimization under concurrent load

## 👤 Author

**Abhijeet Singh**
- GitHub: [@abhijeetsinghCXT](https://github.com/abhijeetsinghCXT)
- LinkedIn: [abhijeet-0-singh](https://linkedin.com/in/abhijeet-0-singh)
- Email: abhijeetsingh555666@gmail.com

## 📝 License

MIT License

---

⭐ **Star this repo if you find it useful!**