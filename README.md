# ScottLMS - Learning Management System

A modern, scalable Learning Management System built with FastAPI, Streamlit, MongoDB, Docker, and Kubernetes.

## 🏗️ Architecture

### Tech Stack
- **Backend**: Python FastAPI with Pydantic v2
- **Frontend**: Streamlit web application
- **Database**: MongoDB with Beanie ODM
- **Containerization**: Docker + Docker Compose (local) + Kubernetes (production)
- **Cloud**: Linode Kubernetes Engine (LKE) + MongoDB Atlas
- **Infrastructure as Code**: Terraform
- **CI/CD**: GitHub Actions

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Load Balancer │    │   LKE Cluster   │
│   (Streamlit)   │◄──►│   (Linode)      │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │ MongoDB Atlas   │
                                               │   (Database)    │
                                               └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- kubectl (for Kubernetes)
- Terraform (for infrastructure)
- Linode CLI configured
- MongoDB Atlas account

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ScottLMS
   ```

2. **Start with Docker Compose**
   ```bash
   # Start all services
   make docker-start
   
   # Or manually
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:8501
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - MongoDB Express: http://localhost:8081 (admin/admin)

### Development Commands

```bash
# View all available commands
make help

# Start development environment
make docker-start

# View logs
make docker-logs

# Stop development environment
make docker-stop

# Restart services
make docker-restart

# Run tests
make test

# Run backend tests only
make test-backend

# Run frontend tests only
make test-frontend

# Run tests with coverage
make test-coverage

# Test with Docker (using latest images)
make docker-test-backend
make docker-test-frontend
make docker-test-all

# Test with specific Docker tag
TAG=v1.0.0 make docker-test-all
```

## 📁 Project Structure

```
ScottLMS/
├── backend/                 # FastAPI backend application
│   ├── entities/           # Pydantic models and Beanie documents
│   │   ├── users.py        # User model
│   │   ├── courses.py      # Course model
│   │   └── enrollments.py  # Enrollment model
│   ├── routers/            # API routes and endpoints
│   │   ├── users.py        # User endpoints
│   │   ├── courses.py      # Course endpoints
│   │   └── enrollments.py  # Enrollment endpoints
│   ├── tests/              # Backend tests
│   │   ├── test_database.py
│   │   ├── test_main.py
│   │   ├── test_entities.py
│   │   └── test_routers.py
│   ├── database.py         # Database connection and initialization
│   ├── main.py             # FastAPI application entry point
│   ├── requirements.txt    # Backend dependencies
│   └── Dockerfile          # Backend Docker image
├── frontend/               # Streamlit frontend application
│   ├── components/         # Reusable UI components
│   │   ├── auth/          # Authentication components
│   │   ├── courses/       # Course-related components
│   │   ├── enrollments/   # Enrollment components
│   │   ├── users/         # User management components
│   │   └── shared/        # Shared components
│   ├── pages/             # Streamlit pages
│   │   ├── 1_Dashboard.py
│   │   ├── 2_Users.py
│   │   ├── 3_Courses.py
│   │   └── 4_Enrollments.py
│   ├── tests/             # Frontend tests
│   │   ├── test_components.py
│   │   ├── test_pages.py
│   │   └── test_frontend_config.py
│   ├── Home.py            # Main Streamlit application
│   ├── config.py          # Frontend configuration
│   ├── requirements.txt   # Frontend dependencies
│   └── Dockerfile         # Frontend Docker image
├── terraform/             # Infrastructure as Code
│   ├── main.tf           # Main Terraform configuration
│   ├── variables.tf      # Variable definitions
│   ├── outputs.tf        # Output definitions
│   ├── kubernetes.tf     # Kubernetes resources
│   └── terraform.tfvars  # Variable values
├── .github/              # GitHub Actions workflows
│   └── workflows/
│       └── pr-validation.yml  # PR validation pipeline
├── scripts/              # Utility scripts
│   └── mongo-init-local.js   # MongoDB initialization
├── docker-compose.yml    # Local development setup
├── Makefile             # Development commands
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017/scottlms` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-change-in-production` |
| `ENVIRONMENT` | Environment (development/production) | `development` |
| `LOG_LEVEL` | Logging level | `info` |
| `API_V1_STR` | API version prefix | `/api/v1` |

### MongoDB Atlas Setup

1. Create a MongoDB Atlas account
2. Create a new project
3. Create a cluster (M10 or higher for production)
4. Create a database user
5. Whitelist your IP addresses
6. Get the connection string

## 📚 API Documentation

### Core Endpoints

#### Users
- `POST /api/users/` - Create user
- `GET /api/users/` - List users
- `GET /api/users/{id}` - Get user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

#### Courses
- `POST /api/courses/` - Create course
- `GET /api/courses/` - List courses
- `GET /api/courses/{id}` - Get course
- `PUT /api/courses/{id}` - Update course
- `DELETE /api/courses/{id}` - Delete course

#### Enrollments
- `POST /api/enrollments/` - Create enrollment
- `GET /api/enrollments/` - List enrollments
- `GET /api/enrollments/{id}` - Get enrollment
- `PUT /api/enrollments/{id}` - Update enrollment
- `DELETE /api/enrollments/{id}` - Delete enrollment

### Interactive API Documentation
Visit `/docs` when running the application for Swagger UI documentation.

## 🧪 Testing

### Local Testing
```bash
# Run all tests
make test

# Run backend tests only
make test-backend

# Run frontend tests only
make test-frontend

# Run tests with coverage
make test-coverage
```

### Docker Testing
```bash
# Test with latest Docker images
make docker-test-backend
make docker-test-frontend
make docker-test-all

# Test with specific tag
TAG=v1.0.0 make docker-test-all
```

### Test Structure
- **Backend Tests**: Unit tests for API endpoints, database operations, and Pydantic models
- **Frontend Tests**: Component tests and page functionality tests
- **Integration Tests**: End-to-end testing with Docker containers

## 🚀 Deployment

### Local Development
```bash
# Start all services
make docker-start

# View logs
make docker-logs

# Stop services
make docker-stop

# Rebuild and restart
make docker-rebuild
```

### Production Deployment

1. **Infrastructure Setup**
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

2. **Application Deployment**
   ```bash
   # Build and push images
   make docker-build
   make docker-push
   
   # Deploy using Terraform
   cd terraform && terraform apply -auto-approve
   ```

## 🔒 Security

### Recent Security Updates
- ✅ **All dependencies updated** to latest secure versions
- ✅ **5 critical vulnerabilities fixed** (PyMongo, FastAPI, Requests)
- ✅ **Pydantic v2 migration** completed
- ✅ **Deprecation warnings resolved**

### Security Features
- JWT-based authentication (planned)
- Role-based access control (student, instructor, admin)
- Password hashing with bcrypt
- Input validation with Pydantic v2
- Security scanning in CI/CD pipeline

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Workflow
- All PRs are automatically validated with GitHub Actions
- Tests must pass before merging
- Security scanning is performed on all changes
- Docker images are built and tested with PR-specific tags

## 📊 Monitoring

### Health Checks
- Application health: `/health`
- Kubernetes liveness/readiness probes configured

### Logging
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### CI/CD Pipeline
- **PR Validation**: Terraform validation, Docker builds, tests, security scans
- **Automated Testing**: Backend and frontend tests with Docker
- **Security Scanning**: Trivy vulnerability scanning
- **Docker Tagging**: PR-specific image tags for testing

## 🗺️ Roadmap

- [x] Backend API with FastAPI
- [x] Frontend with Streamlit
- [x] MongoDB integration with Beanie
- [x] Docker containerization
- [x] Kubernetes deployment
- [x] CI/CD pipeline
- [x] Security vulnerability fixes
- [ ] Authentication & authorization
- [ ] File upload for course materials
- [ ] Real-time notifications
- [ ] Analytics and reporting
- [ ] Advanced course features (quizzes, assignments)
- [ ] Integration with external services

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, email support@scottlms.com or create an issue in the repository.

---

**ScottLMS** - A modern learning management system built with cutting-edge technologies.