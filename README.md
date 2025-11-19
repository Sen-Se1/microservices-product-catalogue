# Microservices Product Catalogue Application

A complete microservices-based e-commerce product catalogue system demonstrating modern cloud-native architecture patterns. This full-stack application features multiple frontend applications, polyglot backend services, containerization, and API gateway implementation.

## 🏗️ Architecture Overview

### Frontend Applications
- **Admin Panel** (Angular 17+ + Bootstrap) - Product & inventory management dashboard
- **Public Website** (Next.js 14+ + TailwindCSS) - Customer-facing product catalogue

### Backend Microservices
- **Product Service** (FastAPI + PostgreSQL) - Product CRUD operations & category management
- **User Service** (Node.js/Express + MongoDB) - Authentication & user management
- **Analytics Service** (FastAPI + Redis + PostgreSQL) - Event tracking & dashboard metrics

### Infrastructure
- **API Gateway** (Nginx) - Centralized routing and service orchestration
- **Containerized** with Docker and Docker Compose
- **Multi-database** architecture (PostgreSQL, MongoDB, Redis)

## 🚀 Key Features

- **Product Management** - Full CRUD operations with image upload
- **User Authentication** - JWT-based with role-based access control
- **Analytics Dashboard** - Real-time metrics and product insights
- **Responsive Design** - Modern UI/UX with Bootstrap and TailwindCSS
- **Server-Side Rendering** - Next.js SSR/ISR for optimal performance
- **API Gateway** - Centralized routing with CORS and rate limiting

## 🛠️ Tech Stack

**Frontend:**
- Angular 17+, TypeScript, RxJS, Bootstrap 5
- Next.js 14+, React 18, TypeScript, TailwindCSS 3+

**Backend:**
- FastAPI (Python), Node.js/Express, JWT Authentication
- PostgreSQL, MongoDB, Redis

**DevOps:**
- Docker, Docker Compose, Nginx API Gateway

## 📁 Project Structure
```
microservices-product-catalogue/
├── frontend/
│   ├── admin-panel/          # Angular application
│   └── public-website/       # Next.js application
├── backend/
│   ├── product-service/      # FastAPI service
│   ├── user-service/         # Node.js service
│   └── analytics-service/    # FastAPI service
├── gateway/                  # Nginx configuration
└── docker-compose.yml        # Multi-container setup
```

## 🎯 Learning Outcomes

This project demonstrates:
- Microservices architecture design and implementation
- Polyglot programming across multiple frameworks
- Containerization with Docker and orchestration
- RESTful API design and security best practices
- Modern frontend development with Angular and Next.js
- Database management with both SQL and NoSQL systems
- DevOps practices including CI/CD readiness

## 🚀 Quick Start

1. Clone the repository
2. Run `docker-compose up` to start all services
3. Access:
   - Public Website: http://localhost:3000
   - Admin Panel: http://localhost:4200
   - API Gateway: http://localhost:80

---