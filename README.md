# ScottLMS - Learning Management System

A modern, scalable Learning Management System built with FastAPI, MongoDB, Docker, Kubernetes, and AWS.

## 🏗️ Architecture

### Tech Stack
- **Backend**: Python FastAPI
- **Database**: MongoDB (Atlas for production)
- **Containerization**: Docker + Docker Compose (local) + Kubernetes (production)
- **Cloud**: AWS (most services) + MongoDB Atlas (database)
- **Infrastructure as Code**: Terraform

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Load Balancer │    │   EKS Cluster   │
│   (Future)      │◄──►│   (ALB)         │◄──►│   (FastAPI)     │
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
- AWS CLI configured
- MongoDB Atlas account

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ScottLMS
   ```

2. **Set up environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - MongoDB Express: http://localhost:8081 (admin/admin)

### Production Deployment

1. **Set up AWS Infrastructure**
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   
   terraform init
   terraform plan
   terraform apply
   ```

2. **Build and push Docker image**
   ```bash
   # Build image
   docker build -t scottlms-api .
   
   # Tag for ECR
   docker tag scottlms-api:latest <ecr-repository-url>:latest
   
   # Push to ECR
   docker push <ecr-repository-url>:latest
   ```

3. **Deploy to Kubernetes**
   ```bash
   # Update kubeconfig
   aws eks update-kubeconfig --region us-west-2 --name scottlms-production
   
   # Deploy using Terraform
   cd terraform && terraform apply -var="image_tag=latest" -auto-approve
   ```

## 📁 Project Structure

```
ScottLMS/
├── app/                    # FastAPI application
│   ├── api/               # API routes and endpoints
│   │   ├── router.py      # API router configuration
│   │   ├── users.py       # User endpoints
│   │   ├── courses.py     # Course endpoints
│   │   └── enrollments.py # Enrollment endpoints
│   ├── core/              # Core application modules
│   │   ├── config.py      # Configuration settings
│   │   ├── database.py    # Database connection
│   │   └── exceptions.py  # Custom exceptions
│   ├── models/            # Data models
│   │   ├── user.py        # User model
│   │   ├── course.py      # Course model
│   │   └── enrollment.py  # Enrollment model
│   ├── services/          # Business logic layer
│   │   ├── user_service.py
│   │   ├── course_service.py
│   │   └── enrollment_service.py
│   └── main.py            # Application entry point
├── terraform/             # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── vpc.tf
│   ├── eks.tf
│   ├── ecr.tf
│   ├── alb.tf
│   ├── route53.tf
│   ├── mongodb.tf
│   └── terraform.tfvars.example
├── scripts/               # Utility scripts
│   └── mongo-init.js      # MongoDB initialization
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Local development setup
├── requirements.txt       # Python dependencies
└── README.md             # This file
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
- `POST /users/` - Create user
- `GET /users/` - List users
- `GET /users/{id}` - Get user
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

#### Courses
- `POST /courses/` - Create course
- `GET /courses/` - List courses
- `GET /courses/{id}` - Get course
- `PUT /courses/{id}` - Update course
- `DELETE /courses/{id}` - Delete course

#### Enrollments
- `POST /enrollments/` - Create enrollment
- `GET /enrollments/` - List enrollments
- `GET /enrollments/{id}` - Get enrollment
- `PUT /enrollments/{id}` - Update enrollment
- `DELETE /enrollments/{id}` - Delete enrollment

### Interactive API Documentation
Visit `/docs` when running the application for Swagger UI documentation.

## 🧪 Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_users.py
```

## 🚀 Deployment

### Local Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
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
   # Build and push image
   docker build -t scottlms-api .
   docker tag scottlms-api:latest <ecr-url>:latest
   docker push <ecr-url>:latest
   
   # Deploy using Terraform
   cd terraform && terraform apply -var="image_tag=latest" -auto-approve
   ```

## 📊 Monitoring

### Health Checks
- Application health: `/health`
- Kubernetes liveness/readiness probes configured

### Logging
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Metrics
- Prometheus metrics available at `/metrics`
- Kubernetes HPA configured for auto-scaling

## 🔒 Security

### Authentication & Authorization
- JWT-based authentication (to be implemented)
- Role-based access control (student, instructor, admin)
- Password hashing with bcrypt

### Infrastructure Security
- VPC with private subnets
- Security groups with minimal access
- SSL/TLS termination at load balancer
- Secrets managed via Kubernetes secrets and AWS Secrets Manager

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, email support@scottlms.com or create an issue in the repository.

## 🗺️ Roadmap

- [ ] Frontend application (React/Next.js)
- [ ] Authentication & authorization
- [ ] File upload for course materials
- [ ] Real-time notifications
- [ ] Analytics and reporting
- [ ] Mobile application
- [ ] Advanced course features (quizzes, assignments)
- [ ] Integration with external services
A learning management system that uses a bunch of cool technologies.
