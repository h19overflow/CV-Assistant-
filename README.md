# 🚀 Resume Optimization System

An AI-powered resume analysis and optimization platform that helps users create ATS-friendly resumes that get past automated screening systems and impress hiring managers.

## 🎯 Core Value Proposition

**Transform your resume into a job-winning document** with:
- **ATS Compatibility Analysis** - Ensure your resume passes automated screening
- **Job-Specific Tailoring** - Match your resume to specific job descriptions
- **Skills Gap Analysis** - Identify missing skills and suggest improvements
- **Achievement Quantification** - Convert responsibilities into impactful metrics

## 🏗️ Architecture Overview

```mermaid
graph TD
    A[Resume Upload] --> B[Document Processing]
    B --> C[Ve  ctor Store Analysis]
    C --> D[AI Analysis Engine]
    D --> E[Feedback Generation]
    E --> F[Optimized Resume]

    G[Job Description] --> D
    H[ATS Rules Database] --> D
```

## 🛠️ Tech Stack

### **Backend Core**
- **FastAPI** - High-performance API framework
- **PostgreSQL + pgvector** - Vector database for semantic search
- **SQLAlchemy** - Database ORM with relationship management
- **Prefect** - Workflow orchestration and task management

### **AI & ML**
- **LangChain** - Document processing and AI chains
- **HuggingFace Transformers** - Embedding models and NLP
- **Pydantic AI** - Structured AI agent framework
- **Semantic Chunking** - Intelligent document segmentation

### **Document Processing**
- **PyPDFium2** - PDF text extraction
- **Docling** - Advanced document parsing
- **Vector Embeddings** - Semantic similarity matching

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL with pgvector extension
- Docker (optional)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Resume_System

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Initialize database
python -m src.backend.boundary.databases.db.setup

# Pre-warm AI models for fast performance
python -m src.backend.core.pipelines.cv_analysis.startup

# Run the application
uvicorn src.main:app --reload
```

### Environment Configuration

```bash
# .env file
POSTGRES_CONNECTION_STRING=postgresql://user:password@localhost:5432/resume_db
HUGGINGFACE_API_KEY=your_hf_token
AWS_REGION=us-east-1
```

## 📊 System Performance

### **Vector Search Performance**
- **Cold Start**: ~7 seconds (first-time model loading)
- **Pre-warmed Queries**: ~100ms (after startup)
- **Cached Results**: Nearly instant
- **Speed Improvement**: 70x faster with optimization

### **Database Operations**
- **User Authentication**: <50ms
- **Resume Processing**: ~2-5 seconds per document
- **Semantic Search**: Sub-second results

## 🔧 Core Features

### **1. Resume Analysis Engine**
```python
from src.backend.core.pipelines.cv_analysis.flow import document_processing_flow

# Process resume document
chunks = document_processing_flow("path/to/resume.pdf")

# Search for specific information
results = fetch_context(["What are the candidate's Python skills?"])
```

### **2. User Authentication**
```python
from src.backend.boundary.databases.db import create_user, login_user

# Create new user
user = create_user("john@example.com", "secure_password")

# Authenticate user
authenticated_user = login_user("john@example.com", "secure_password")
```

### **3. Vector-Based Search**
```python
from src.backend.boundary.databases.vdb import get_vector_client

# Get optimized vector client
client = get_vector_client("cv_documents")

# Batch query for efficiency
results = client.query_batch([
    "Technical skills and experience",
    "Educational background",
    "Professional achievements"
], k=5)
```

## 🎯 API Endpoints

### **Resume Analysis**
```python
POST /analyze-resume
{
    "resume_file": "file.pdf",
    "job_description": "Software Engineer position..."
}
```

### **Job-Specific Optimization**
```python
POST /optimize-for-job
{
    "resume_file": "file.pdf",
    "job_posting": "Full job description text..."
}
```

### **ATS Compatibility Check**
```python
POST /ats-compatibility
{
    "resume_file": "file.pdf"
}
```

## 🏗️ Development Phases

### **Phase 1: Core CV Analysis (Day 1)**
- ✅ Resume parsing & text extraction
- ✅ Vector storage with semantic search
- ✅ ATS compatibility scoring
- ✅ Basic feedback generation

### **Phase 2: AWS Deployment (Day 2)**
- 🔄 Docker containerization
- 🔄 ECS Fargate deployment
- 🔄 RDS PostgreSQL with pgvector
- 🔄 CloudWatch monitoring

### **Phase 3: Advanced Features (Day 3)**
- 🔄 Job-specific optimization
- 🔄 Achievement enhancement
- 🔄 Skills development recommendations
- 🔄 Production polish

## 📈 Success Metrics

### **User Value**
- **ATS Score Improvement**: Before/after compatibility ratings
- **Keyword Match %**: Increase in job-relevant terms
- **Processing Speed**: Sub-second feedback generation
- **Actionable Insights**: Specific improvement suggestions

### **System Performance**
- **Response Time**: <100ms for cached queries
- **Throughput**: 1000+ resumes per hour
- **Availability**: 99.9% uptime target
- **Cost Efficiency**: ~$15-20 for 3-day implementation

## 🐳 Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and deploy
docker build -t resume-optimizer .
docker run -p 8000:8000 --env-file .env resume-optimizer
```

## 🔍 Database Schema

### **Core Tables**
- **`users`** - User accounts and authentication
- **`resumes`** - Uploaded resume content and metadata
- **`sections`** - Parsed resume sections (Education, Experience, etc.)
- **`entities`** - Extracted skills, companies, achievements
- **`feedback`** - AI-generated optimization suggestions

### **Vector Storage**
- **pgvector extension** - Semantic similarity search
- **Embedding models** - sentence-transformers/all-MiniLM-L6-v2
- **Chunking strategy** - Semantic segmentation for context

## 🔧 Performance Optimization

### **Model Pre-warming**
```python
from src.backend.boundary.databases.vdb import prewarm_models

# At application startup
prewarm_models()  # 10s one-time cost
# All subsequent queries: ~100ms
```

### **Caching Strategy**
- **Global embedding cache** - Prevent model reloading
- **Connection pooling** - Reuse database connections
- **Query result cache** - Instant repeated searches
- **Lazy initialization** - Load resources on-demand

## 🚀 Getting Started with Development

### **1. Set Up Development Environment**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Format code
black src/
isort src/
```

### **2. Database Operations**
```bash
# Create tables
python -m src.backend.boundary.databases.db.setup

# Test authentication
python test_auth.py

# Performance benchmarks
python speed_test.py
```

### **3. Vector Search Testing**
```bash
# Test document processing
python -m src.backend.core.pipelines.cv_analysis.flow.document_processing_flow

# Benchmark performance
python performance_test.py
```

## 📚 Documentation

- **API Documentation**: `/docs` (Swagger UI)
- **Database Schema**: `src/backend/boundary/databases/db/models.py`
- **Vector Operations**: `src/backend/boundary/databases/vdb/`
- **Processing Pipeline**: `src/backend/core/pipelines/cv_analysis/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

### **Immediate (Week 1)**
- [ ] Complete AWS deployment pipeline
- [ ] Add job description analysis
- [ ] Implement ATS scoring algorithm
- [ ] Create web interface

### **Short-term (Month 1)**
- [ ] Multi-format support (DOCX, TXT)
- [ ] Industry-specific templates
- [ ] Bulk processing capabilities
- [ ] Advanced analytics dashboard

### **Long-term (Quarter 1)**
- [ ] Machine learning model training
- [ ] A/B testing framework
- [ ] Mobile API support
- [ ] Enterprise features

---

<div align="center">

**🎯 Built to help you land your dream job with AI-optimized resumes**

[Documentation](./docs) • [API Reference](./api) • [Contributing](./CONTRIBUTING.md) • [Support](./issues)

</div>