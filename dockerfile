#Dockerfile
FROM python:3.10.13
RUN apt-get -y update && apt-get -y upgrade
COPY src/ ./
COPY requirements.txt ./
WORKDIR .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]