FROM python:3.8

WORKDIR /

ADD requirements.txt .
COPY app/* /

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 50051
CMD ["python", "-i", "main.py"]
