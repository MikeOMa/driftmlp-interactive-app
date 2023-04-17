create-env:
	conda env create -f environment.yml

run-app:
	python -m streamlit run streamlit_app.py

build:
	docker build . -t driftmlp-streamlit:v2

run-docker:
	docker run -p 8080:8080 driftmlp-streamlit:v2

deploy:
	gcloud builds submit --tag gcr.io/drifter-pathways/drifter-pathways --timeout=2h

deploy-gcloud:
	gcloud run deploy --image gcr.io/drifter-pathways/drifter-pathways --platform managed --region us-central1 --allow-unauthenticated