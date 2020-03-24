FROM alpine
FROM python:3.7

COPY data /usr/haiku_writer/data
COPY properties /usr/haiku_writer/properties
COPY source /usr/haiku_writer/source
COPY requirements.txt /usr/haiku_writer/requirements.txt

WORKDIR /usr/haiku_writer/source

RUN pip3 install -r ../requirements.txt
RUN python executor.py
