FROM python:3.9
COPY . /crawlers/
WORKDIR /crawlers
RUN pip install -r requirements.txt
