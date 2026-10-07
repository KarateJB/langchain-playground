# Deploy to local Docker host

---
## Requirements

### Environment Variables

Copy `.env.sample` to `.env` and update the values:

```bash
cp .env.sample .env
```

Update the following in `.env`:
- `GOOGLE_API_KEY`: Your Google API key for LangChain agent
- `POSTGRES_PASSWORD`: Your PostgreSQL password (optional, but recommended for security)

---
## Start Services

```bash
make build
make run
```

Or directly with docker-compose:

```bash
docker-compose build
docker-compose up -d
```

---
## Working with the Agent Container

### Run agent commands interactively

```bash
# Access the container shell
docker compose exec agent bash
# or
docker exec -it agent bash

# Run agent commands (check agents/README.md for more details)
python -m agent_langgraph.app --thread ai-news ainews
```

### View logs

```bash
docker-compose logs -f agent
docker-compose logs -f postgres
```

### Stop services

```bash
docker-compose down
```

### Remove volumes (to reset database)

```bash
docker-compose down -v
```

---
## Push Docker Images

To push images to Docker Hub:
```bash
docker login -u <DOCKERHUB_USER>
echo "<DOCKERHUB_PASSWORD>" | docker login -u <DOCKERHUB_USER> --password-stdin
make push_dockerhub
```

And for Azure Container Registry (ACR):

```bash
# You have to login to ACR
export AZURECR=<name>.azurecr.io
az acr login --name $AZURECR
make push_azurecr
```

---
## Architecture

```
┌─────────────────────────────────────────┐
│     LangChain Playground (Docker)       │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  agent Container     │   │
│  │  (Python 3.11 + Dependencies)   │   │
│  │  - Processes AI queries         │   │
│  │  - Stores session memory        │   │
│  └────────────┬────────────────────┘   │
│               │                        │
│               │ (TCP 5432)             │
│               ▼                        │
│  ┌─────────────────────────────────┐   │
│  │   PostgreSQL Container          │   │
│  │  - Persists conversation data   │   │
│  │  - Stores agent checkpoints     │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

