.PHONY: install seed backend frontend dev clean

install:
	@echo "--- Installing backend deps ---"
	cd backend && pip install -r requirements.txt --break-system-packages
	@echo "--- Installing frontend deps ---"
	cd frontend && npm install

seed:
	@echo "--- Seeding demo data ---"
	cd backend && python ../datasets/seed.py --persona riya

seed-reset:
	@echo "--- Resetting DB and seeding demo data ---"
	cd backend && python ../datasets/seed.py --persona riya --reset

backend:
	@echo "--- Starting FastAPI backend ---"
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

frontend:
	@echo "--- Starting Next.js frontend ---"
	cd frontend && npm run dev

dev:
	@echo "--- Starting both servers (requires tmux or two terminals) ---"
	@echo "Run 'make backend' and 'make frontend' in separate terminals"

eval:
	cd backend && python evaluation/runner.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -f backend/db/*.db
