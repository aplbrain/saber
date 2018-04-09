Dockerized tool for image normalization.
Images should be stored in a (X,Y,Z) image stack in a numpy file

Create image with
docker build . -t saber:preprocess

This will allow it to work with the galaxy environment.

Normalization is either gamma or logarithmic, controlled by the parameters in the galaxy tool file. 