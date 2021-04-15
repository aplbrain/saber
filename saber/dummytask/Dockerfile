FROM nvidia/cuda:11.2.1-devel-ubuntu20.04
RUN apt-get update
RUN apt-get install -yqq python3-dev python3-pip
RUN pip3 install torch
COPY main.py /app/main.py
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh
