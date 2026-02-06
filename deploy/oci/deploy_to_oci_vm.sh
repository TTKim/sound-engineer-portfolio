#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

VM_IP="${OCI_VM_IP:-}"
SSH_USER="${OCI_SSH_USER:-ubuntu}"
SSH_KEY="${OCI_SSH_KEY:-}"
SITE_DOMAIN="${SITE_DOMAIN:-portfolio.hajungs.com}"

if [[ -z "$VM_IP" || -z "$SSH_KEY" ]]; then
  echo "Missing required environment variables."
  echo "Required: OCI_VM_IP, OCI_SSH_KEY"
  echo "Optional: OCI_SSH_USER (default: ubuntu), SITE_DOMAIN (default: portfolio.hajungs.com)"
  exit 1
fi

if [[ ! -f "$SSH_KEY" ]]; then
  echo "SSH key not found: $SSH_KEY"
  exit 1
fi

WORK_DIR="/tmp/sound-portfolio-deploy"

echo "[1/4] Preparing local deployment bundle..."
rm -rf "$ROOT_DIR/.deploy_tmp"
mkdir -p "$ROOT_DIR/.deploy_tmp"
cp "$ROOT_DIR/index.html" "$ROOT_DIR/.deploy_tmp/"
cp "$ROOT_DIR/styles.css" "$ROOT_DIR/.deploy_tmp/"
cp "$ROOT_DIR/script.js" "$ROOT_DIR/.deploy_tmp/"
cp "$ROOT_DIR/Portfolio_list.csv" "$ROOT_DIR/.deploy_tmp/"
cp "$ROOT_DIR/portfolio_media_map.json" "$ROOT_DIR/.deploy_tmp/"

echo "[2/4] Uploading files to VM ($VM_IP)..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=accept-new "${SSH_USER}@${VM_IP}" "mkdir -p ${WORK_DIR}"
scp -i "$SSH_KEY" "$ROOT_DIR/.deploy_tmp/"* "${SSH_USER}@${VM_IP}:${WORK_DIR}/"

echo "[3/4] Installing and configuring Nginx..."
ssh -i "$SSH_KEY" "${SSH_USER}@${VM_IP}" "bash -s" <<EOF
set -euo pipefail
sudo apt update
sudo apt install -y nginx
sudo mkdir -p /var/www/portfolio
sudo cp ${WORK_DIR}/index.html /var/www/portfolio/index.html
sudo cp ${WORK_DIR}/styles.css /var/www/portfolio/styles.css
sudo cp ${WORK_DIR}/script.js /var/www/portfolio/script.js
sudo cp ${WORK_DIR}/Portfolio_list.csv /var/www/portfolio/Portfolio_list.csv
sudo cp ${WORK_DIR}/portfolio_media_map.json /var/www/portfolio/portfolio_media_map.json

sudo tee /etc/nginx/sites-available/portfolio >/dev/null <<NGINX
server {
    listen 80;
    listen [::]:80;
    server_name ${SITE_DOMAIN};

    root /var/www/portfolio;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location ~* \\.(css|js|json|csv)$ {
        add_header Cache-Control "public, max-age=300";
    }
}
NGINX

sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/portfolio /etc/nginx/sites-enabled/portfolio
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx
EOF

echo "[4/4] Verifying HTTP service..."
curl -I "http://${VM_IP}" | sed -n '1,8p'

rm -rf "$ROOT_DIR/.deploy_tmp"

echo
echo "Deployment complete."
echo "Check: http://${SITE_DOMAIN}"
echo "Next recommended step: enable HTTPS with certbot."

