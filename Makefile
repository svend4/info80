.PHONY: up down ui api shell

up:
	docker-compose up --build

down:
	docker-compose down -v

ui:
	streamlit run streamlit_app.py

api:
	uvicorn api.main:app --reload

shell:
	docker-compose exec app bash
