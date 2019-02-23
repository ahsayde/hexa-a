FROM python:latest
COPY . /code
WORKDIR /code
RUN pip3 install -r requirements.txt
RUN bash scripts/semantic.sh