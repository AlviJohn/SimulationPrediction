
Docker Commands

docker build . -t simulation_Prediction-docker -f Dockerfile.txt
docker run -p 8501:8501 simulation_Prediction-docker:latest

Docker login 

docker tag simulation_Prediction-docker:latest  alvijohn/simulation_Prediction-docker
docker push alvijohn/simulation_Prediction-docker
