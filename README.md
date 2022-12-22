
**Docker Commands(in cmd)**

docker build . -t simulation_prediction-docker -f Dockerfile.txt


docker run -p 8501:8501 simulation_prediction-docker:latest

**Docker login **

docker tag simulation_prediction-docker:latest alvijohn/simulation_prediction-docker

docker push alvijohn/simulation_prediction-docker

startup command for streamlit
python -m streamlit run hello --server.port 8000 --server.address 0.0.0.0
python -m streamlit run PredictionFunction_OD_SW_FP.py --server.port 8000 --server.address 0.0.0.0
