
**Docker Commands(in cmd)**

docker build . -t simulation_prediction-docker -f Dockerfile.txt


docker run -p 8501:8501 simulation_prediction-docker:latest

**Docker login **

docker tag simulation_prediction-docker:latest alvijohn/simulation_prediction-docker

docker push alvijohn/simulation_prediction-docker

startup command for streamlit
python -m streamlit run Hello.py --server.port 8000
