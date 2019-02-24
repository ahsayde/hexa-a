echo "[*] Building check image .."
docker build -t checker:latest ../checker/

echo "[*] Generating secrets .."
export JWT_SECRET=$(openssl rand -hex 24)
export SESSION_SECRET=$(openssl rand -hex 24)
export MINIO_ACCESS_KEY=$(openssl rand -hex 24)
export MINIO_SECRET_KEY=$(openssl rand -hex 24)

echo "[*] Deploying apps ..."
docker-compose config --quiet
docker-compose up -d