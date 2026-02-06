# OCI Always Free 배포 가이드 (`portfolio.hajungs.com`)

이 가이드는 **Oracle Cloud Always Free VM + Nginx**로 포트폴리오를 고정 배포합니다.

## 1) OCI 콘솔에서 VM 1개 생성

- Shape: `VM.Standard.E2.1.Micro` (Always Free)
- OS: Ubuntu 22.04
- Public IP: 할당
- SSH 키: 로컬 공개키 등록
- 보안 규칙(Ingress):
  - TCP `22` (SSH)
  - TCP `80` (HTTP)
  - TCP `443` (HTTPS)

## 2) Cloudflare DNS 설정

Cloudflare DNS에 다음 추가:

- `A` 레코드
  - Name: `portfolio`
  - Content: `OCI VM 공인 IP`
  - Proxy: `Proxied`(오렌지 구름) 권장

도메인 전파 후 `portfolio.hajungs.com`이 VM IP를 가리켜야 합니다.

## 3) 로컬에서 자동 배포 실행

프로젝트 루트(`/Users/taewankim/sound-engineer-portfolio`)에서:

```bash
chmod +x deploy/oci/deploy_to_oci_vm.sh
OCI_VM_IP="<VM_PUBLIC_IP>" \
OCI_SSH_USER="ubuntu" \
OCI_SSH_KEY="$HOME/.ssh/<your_key>.pem" \
SITE_DOMAIN="portfolio.hajungs.com" \
./deploy/oci/deploy_to_oci_vm.sh
```

성공하면:
- Nginx 설치/설정
- 정적 파일 업로드
- `http://portfolio.hajungs.com` 서비스 시작

## 4) HTTPS 적용 (권장)

VM에 접속 후:

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d portfolio.hajungs.com --non-interactive --agree-tos -m you@example.com --redirect
```

## 배포 대상 파일

- `index.html`
- `styles.css`
- `script.js`
- `Portfolio_list.csv`
- `portfolio_media_map.json`

