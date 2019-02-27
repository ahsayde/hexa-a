# HEXA-A
Opensource platform allows educators to create groups, distribute coding assignments and review students submissions.

![assignment page](/docs/imgs/sh1.png)

## Deployment
1- Build checker image
```
docker build -t checker:latest checker/
```

2- Create important directories
```
mkdir -p /root/.caddy
mkdir -p /data/minio/storage
mkdir -p /data/minio/config
```

3- Generate secrets
```
export JWT_SECRET=<secret value>
export SESSION_SECRET=<secret value>
export MINIO_ACCESS_KEY=<secret value>
export MINIO_SECRET_KEY=<secret value>
```

4- Edit ```Caddyfile``` and put your **domain** and **email**

4- Deploy using ```docker-compose```
```
docker-compose config --quiet
docker-compose up -d
```

