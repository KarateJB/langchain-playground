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
docker-compose exec agent-langgraph /bin/bash

# Run agent commands
python -m agent_langgraph.app "Your question here"
python -m agent_langgraph.app gatsby
python -m agent_langgraph.app ainews
```

### View logs

```bash
docker-compose logs -f agent-langgraph
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
│  │   agent-langgraph Container     │   │
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

---
## Next Steps

To enable PostgreSQL integration in the agent:
1. Update `agent_langgraph/app.py` to use `PostgresSaver` instead of `InMemorySaver`
2. Connection string will be auto-configured from environment variables:
   - `POSTGRES_HOST`: postgres
   - `POSTGRES_PORT`: 5432
   - `POSTGRES_DB`: postgres
   - `POSTGRES_USER`: postgres
   - `POSTGRES_PASSWORD`: from `.env`
