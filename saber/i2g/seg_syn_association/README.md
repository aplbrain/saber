docker build . -t aplbrain/i2g:assoc
docker run -v ./data:/data python /app
