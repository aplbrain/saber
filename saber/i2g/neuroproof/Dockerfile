FROM conda/miniconda3
RUN apt-get -qq update && apt-get install -qq -y \
    git \
    libgl1-mesa-dev \
    libsm6 \
    libglib2.0-0 \
    libxrender1 \
    libxss1 \
    libxft2 \
    libxt6
RUN git clone https://github.com/janelia-flyem/neuroproof_examples.git
ENV PATH=$PATH:"/usr/local/envs/saber_neuroproof/bin"
