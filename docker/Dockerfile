FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-devel AS builder
ENV DEBIAN_FRONTEND noninteractive

# https://github.com/NVIDIA/nvidia-docker/issues/1632#issuecomment-1112667716
RUN rm /etc/apt/sources.list.d/cuda.list
RUN rm /etc/apt/sources.list.d/nvidia-ml.list

RUN apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*

RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-ubuntu1804.pin
RUN mv cuda-ubuntu1804.pin /etc/apt/preferences.d/cuda-repository-pin-600
RUN wget https://developer.download.nvidia.com/compute/cuda/11.7.0/local_installers/cuda-repo-ubuntu1804-11-7-local_11.7.0-515.43.04-1_amd64.deb
RUN dpkg -i cuda-repo-ubuntu1804-11-7-local_11.7.0-515.43.04-1_amd64.deb
RUN cp /var/cuda-repo-ubuntu1804-11-7-local/cuda-*-keyring.gpg /usr/share/keyrings/
RUN apt-get update
RUN apt-get -y install cuda

RUN apt-get install -y ca-certificates python3-dev git wget sudo ninja-build

RUN ln -sv /usr/bin/python3 /usr/bin/python

# create a non-root user
ARG USER_ID=1000
RUN useradd -m --no-log-init --system  --uid ${USER_ID} appuser -g sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER appuser
WORKDIR /home/appuser

ENV PATH="/home/appuser/.local/bin:${PATH}"
RUN wget https://bootstrap.pypa.io/pip/get-pip.py && \
	python3 get-pip.py --user && \
	rm get-pip.py

RUN pip3 install --user cmake   # cmake from apt-get is too old

RUN pip3 install --user 'git+https://github.com/facebookresearch/fvcore'
# install detectron2
RUN git clone https://github.com/facebookresearch/detectron2 detectron2_repo
# set FORCE_CUDA because during `docker build` cuda is not accessible
ENV FORCE_CUDA="1"
# This will by default build detectron2 for all common cuda architectures and take a lot more time,
# because inside `docker build`, there is no way to tell which architecture will be used.
ARG TORCH_CUDA_ARCH_LIST="Kepler;Kepler+Tesla;Maxwell;Maxwell+Tegra;Pascal;Volta;Turing"
ENV TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST}"

#install intern
RUN pip3 install --user -e detectron2_repo
RUN pip3 install intern
RUN pip3 install fiftyone
RUN pip3 install cloud-volume
RUN pip3 install opencv-python

# Set a fixed model cache directory.
ENV FVCORE_CACHE="/tmp"
WORKDIR /home/appuser/detectron2_repo