FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install pandas kafka-python mysql-connector-python

CMD ["tail", "-f", "/dev/null"]

