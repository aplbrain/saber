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

# #Certificate for SSL Verification
# RUN apt-get install -qq -y ca-certificates
# COPY JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt /usr/local/share/ca-certificates/JHUAPL-MS-Root-iCA-05-21-2038-B64-text.crt
# RUN update-ca-certificates
# RUN git config --global http.sslCAInfo /usr/local/share/ca-certificates/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt

#Neuroproof Installation
RUN conda create -n saber_neuroproof -c flyem neuroproof
ENV PATH=$PATH:"/usr/local/envs/saber_neuroproof/bin"
RUN pip install numpy h5py

WORKDIR /app
COPY driver.py /app/driver.py
RUN git clone https://github.com/janelia-flyem/neuroproof_examples.git
#ENTRYPOINT ["python3", "driver.py" ]
