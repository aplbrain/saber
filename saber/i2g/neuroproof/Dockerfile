FROM conda/miniconda3

#Shared Library Dependencies 
RUN apt-get -qq update && apt-get install -qq -y \
    git \
    libgl1-mesa-dev \
    libsm6 \
    libglib2.0-0 \
    libxrender1 \
    libxss1 \
    libxft2 \
    libxt6 

#Neuroproof Installation
RUN conda create -n saber_neuroproof -c flyem neuroproof
ENV PATH=$PATH:"/usr/local/envs/saber_neuroproof/bin"
RUN pip install numpy h5py

WORKDIR /app
COPY driver.py /app/driver.py
# COPY kasthuri_classifier.xml /app/kasthuri_classifier.xml
#RUN git clone https://github.com/janelia-flyem/neuroproof_examples.git
RUN wget --directory-prefix /app/kasthuri_classifier.xml https://saber-batch-dev.s3.amazonaws.com/kasthuri_classifier.xml
ENTRYPOINT ["python3", "driver.py" ]
