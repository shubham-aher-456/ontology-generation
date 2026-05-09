# Docker Setup Guide

## Environment Configuration

This project supports both Docker and local development environments with different database connection configurations.

### For Docker Deployment (Recommended)

The current `.env` file is configured for Docker deployment with container service names:

```bash
# Start all services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### For Local Development

If you want to run the application locally (without Docker) while using local database instances:

1. Copy the local environment template:
```bash
cp .env.local .env
```

2. Make sure you have local instances of:
   - PostgreSQL running on localhost:5432
   - Neo4j running on localhost:7687
   - Redis running on localhost:6379

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Environment Files

- `.env` - Current environment configuration (Docker by default)
- `.env.example` - Template with documentation
- `.env.local` - Template for local development
- `.env` is used by both Docker Compose and the application

## Database Hosts

| Environment | PostgreSQL | Neo4j | Redis |
|-------------|------------|-------|-------|
| Docker | `postgres` | `neo4j` | `redis` |
| Local | `localhost` | `localhost` | `localhost` |

## Docker Services

The `docker-compose.yml` includes:

- **postgres**: PostgreSQL 15 database (port 5433 → 5432)
- **neo4j**: Neo4j 5.16 graph database (ports 7475 → 7474, 7688 → 7687)
- **redis**: Redis 7 cache (port 6380 → 6379)
- **api**: FastAPI application (port 8000)

All services include health checks and proper dependency management.

## Port Mapping

| Service | Host Port | Container Port | Access URL |
|---------|-----------|----------------|------------|
| API | 8001 | 8000 | http://localhost:8001 |
| PostgreSQL | 5433 | 5432 | localhost:5433 |
| Neo4j Browser | 7475 | 7474 | http://localhost:7475 |
| Neo4j Bolt | 7688 | 7687 | bolt://localhost:7688 |
| Redis | 6380 | 6379 | localhost:6380 |

*Note: Different host ports are used to avoid conflicts with local services*

## Quick Start

1. Ensure Docker and Docker Compose are installed
2. Copy environment file: `cp .env.example .env`
3. Update `.env` with your Azure OpenAI credentials
4. Start services: `docker-compose up -d`
5. Access API at: http://localhost:8001
6. Access Neo4j browser at: http://localhost:7475

## Troubleshooting

### Port Conflicts
If you get "port already allocated" errors:
- **PostgreSQL (5432)**: We use port 5433 to avoid conflicts
- **Neo4j (7474/7687)**: We use ports 7475/7688 to avoid conflicts  
- **Redis (6379)**: We use port 6380 to avoid conflicts

### Common Commands
- Check service health: `docker-compose ps`
- View logs: `docker-compose logs [service-name]`
- View API logs: `docker-compose logs -f api`
- Restart services: `docker-compose restart`
- Clean restart: `docker-compose down && docker-compose up -d`
- Stop and remove: `docker-compose down -v` (removes volumes too)

### Database Connections
- **PostgreSQL**: `postgresql://postgres:postgres@localhost:5433/ontology_kb`
- **Neo4j**: `bolt://neo4j:ontology123@localhost:7688`
- **Redis**: `redis://localhost:6380`