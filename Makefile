.PHONY: help install start stop restart logs test clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

start: ## Start all services
	docker-compose up -d
	cd backend && python -m app.main &
	cd frontend && npm run dev

stop: ## Stop all services
	docker-compose down
	pkill -f "uvicorn app.main" || true
	pkill -f "vite" || true

restart: ## Restart all services
	$(MAKE) stop
	$(MAKE) start

logs: ## Show Docker logs
	docker-compose logs -f

test: ## Run tests
	cd backend && pytest tests/ -v

clean: ## Clean temporary files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf frontend/dist frontend/node_modules/.vite

init-data: ## Initialize database data
	cd backend && python scripts/init_milvus.py
	cd backend && python scripts/init_neo4j.py

status: ## Show service status
	@echo "=== Docker Services ==="
	docker-compose ps
	@echo "\n=== Backend ==="
	curl -s http://localhost:8000/api/health | python -m json.tool || echo "Backend not running"
	@echo "\n=== Frontend ==="
	curl -s http://localhost:5173 > /dev/null && echo "Frontend is running" || echo "Frontend not running"
