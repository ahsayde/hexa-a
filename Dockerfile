FROM ubuntu:latest
COPY . /code
WORKDIR /code
RUN apt update && apt install -y unzip curl docker.io python3-pip
RUN pip3 install -r requirements.txt
RUN bash scripts/semantic.sh