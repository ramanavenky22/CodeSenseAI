# CodeSense AI 🧠🔍
**AI-powered code review assistant** for GitHub pull requests. Combines static analysis tools with **LangChain + GPT-4** to provide intelligent code reviews, detect bugs, security vulnerabilities, and suggest improvements—all integrated seamlessly with your GitHub workflow.

[![CI](https://img.shields.io/github/actions/workflow/status/your-org/codesense-ai/ci.yml?label=CI)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)]()
[![Made with FastAPI](https://img.shields.io/badge/backend-FastAPI-blue)]()
[![LangChain](https://img.shields.io/badge/AI-LangChain-purple)]()
[![Dockerized](https://img.shields.io/badge/Container-Docker-informational)]()

---

## ✨ Features

### 🤖 AI-Powered Analysis
- **LangChain Integration**: Uses advanced LLM chains for intelligent code analysis
- **Multi-Model Support**: GPT-4, Codex, and other OpenAI models
- **Context-Aware**: Understands project structure and coding patterns
- **Confidence Scoring**: AI confidence levels for each finding

### 🔍 Comprehensive Code Review
- **Bug Detection**: Identifies logic errors, edge cases, and potential runtime issues
- **Security Analysis**: Detects vulnerabilities, unsafe patterns, and security anti-patterns
- **Code Quality**: Reviews complexity, naming conventions, and maintainability
- **Best Practices**: Suggests improvements based on industry standards

### 🛠️ Static Analysis Integration
- **Bandit**: Python security analysis
- **Semgrep**: Multi-language security and quality rules
- **Safety**: Dependency vulnerability scanning
- **Custom Rules**: Extensible rule system

### 📊 Real-Time Dashboard
- **Live Monitoring**: Track review progress and results
- **Analytics**: Repository insights and trend analysis
- **Manual Analysis**: Test code snippets without GitHub integration
- **Issue Management**: Track and resolve findings

### 🔗 GitHub Integration
- **Webhook Support**: Automatic PR analysis on open/update
- **Inline Comments**: Direct feedback on specific lines
- **Review Summaries**: Comprehensive analysis reports
- **Status Checks**: Integration with GitHub's review system

---

## 🏗️ Architecture

### Backend (FastAPI + LangChain)
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub API    │◄──►│   FastAPI App    │◄──►│   LangChain     │
│   Webhooks      │    │   - Routes       │    │   - GPT-4       │
│   - PR Events   │    │   - Services     │    │   - Prompts     │
│   - File Data   │    │   - Database     │    │   - Chains      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   PostgreSQL    │
                       │   - Reviews     │
                       │   - Sessions    │
                       │   - Analytics   │
                       └──────────────────┘
```

### Frontend (React + TypeScript)
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Dashboard     │    │   Repositories   │    │ Manual Analysis │
│   - Stats       │    │   - Analytics    │    │   - Code Input  │
│   - Trends      │    │   - PR History   │    │   - Results     │
│   - Charts      │    │   - Issues       │    │   - Suggestions │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Static Analysis Pipeline
```
Code Input → AI Analysis → Static Analysis → Combined Results → GitHub Comments
     │            │              │                │
     ▼            ▼              ▼                ▼
  LangChain   GPT-4 Chain    Bandit/Semgrep   Review Service
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- OpenAI API Key
- GitHub Personal Access Token

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/codesense-ai.git
cd codesense-ai
```

2. **Set up environment variables**
```bash
cp env.example .env
# Edit .env with your API keys and configuration
```

3. **Start with Docker Compose (Recommended)**
```bash
docker-compose up -d
```

4. **Or run locally**

**Backend:**
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

---

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_TOKEN=your_github_token_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
DATABASE_URL=postgresql://user:password@localhost:5432/codesense_ai
SECRET_KEY=your_secret_key_here

# Optional
SONARQUBE_URL=http://localhost:9000
SONARQUBE_TOKEN=your_sonarqube_token_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key_here
```

### GitHub Webhook Setup
1. Go to your repository settings
2. Navigate to Webhooks
3. Add webhook URL: `https://your-domain.com/api/v1/webhooks/github`
4. Select events: `Pull requests`, `Pushes`, `Repository`
5. Set content type to `application/json`

---

## 📖 Usage

### Manual Code Analysis
1. Navigate to the Manual Analysis page
2. Select programming language
3. Paste your code
4. Click "Analyze Code"
5. Review AI suggestions and static analysis results

### GitHub Integration
1. Set up webhook in your repository
2. Create or update a pull request
3. CodeSense AI automatically analyzes changes
4. Review comments appear in the PR
5. Check dashboard for detailed analytics

### Dashboard Analytics
- **Overview**: Repository and review statistics
- **Trends**: Activity charts and issue breakdowns
- **Repositories**: Track multiple projects
- **Sessions**: Monitor analysis progress

---

## 🧪 Testing

### Backend Tests
```bash
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Security Scanning
```bash
bandit -r app/
safety check
semgrep --config=auto .
```

---

## 📊 API Documentation

### Core Endpoints

#### Reviews
- `POST /api/v1/reviews/analyze` - Start code analysis
- `GET /api/v1/reviews/session/{session_id}` - Get session status
- `GET /api/v1/reviews/session/{session_id}/results` - Get analysis results
- `POST /api/v1/reviews/manual` - Manual code analysis

#### Webhooks
- `POST /api/v1/webhooks/github` - GitHub webhook handler

#### Dashboard
- `GET /api/v1/dashboard/stats` - Dashboard statistics
- `GET /api/v1/dashboard/trends` - Trend data
- `GET /api/v1/dashboard/repositories/{id}/analytics` - Repository analytics

### Example API Usage

**Manual Analysis:**
```bash
curl -X POST "http://localhost:8000/api/v1/reviews/manual" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello():\n    print(\"Hello, World!\")",
    "file_path": "hello.py",
    "language": "python"
  }'
```

**Get Session Status:**
```bash
curl "http://localhost:8000/api/v1/reviews/session/{session_id}"
```

---

## 🔒 Security Features

- **Webhook Signature Verification**: Ensures GitHub webhook authenticity
- **API Key Management**: Secure handling of OpenAI and GitHub tokens
- **Input Validation**: Comprehensive request validation
- **Rate Limiting**: Protection against abuse
- **Static Analysis**: Built-in security scanning tools

---

## 🛠️ Development

### Project Structure
```
codesense-ai/
├── app/
│   ├── api/routes/          # API endpoints
│   ├── core/                # Configuration and database
│   ├── services/            # Business logic
│   └── schemas/             # Pydantic models
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/           # Page components
│   │   └── services/        # API client
├── tests/                   # Test files
├── docker-compose.yml       # Docker setup
└── requirements.txt         # Python dependencies
```

### Adding New Analysis Rules
1. Create new prompt templates in `app/services/code_analysis.py`
2. Add corresponding static analysis tools
3. Update the frontend to display new issue types
4. Add tests for new functionality

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📈 Performance & Scalability

- **Async Processing**: Background tasks for large PRs
- **Caching**: Redis for session and result caching
- **Database Optimization**: Indexed queries and connection pooling
- **Horizontal Scaling**: Docker-based deployment
- **Monitoring**: Health checks and logging

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Install dependencies
2. Set up local database
3. Configure environment variables
4. Run tests
5. Start development servers

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangChain** for the powerful LLM framework
- **OpenAI** for GPT-4 and Codex models
- **FastAPI** for the excellent web framework
- **React** and **Material-UI** for the frontend
- **GitHub** for the comprehensive API

---

## 📞 Support

- **Documentation**: [Full Documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-username/codesense-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/codesense-ai/discussions)

---

**Built with ❤️ for the developer community**

