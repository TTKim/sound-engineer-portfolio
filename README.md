# BigSummer Portfolio

BigSummer 사운드 엔지니어 포트폴리오 웹사이트입니다. YouTube 음악을 카드 형태로 표시하고, 호버 및 클릭 시 상세 정보를 볼 수 있습니다.

## 기능

- 🎵 음악 카드 그리드 레이아웃
- 🖱️ 마우스 호버 시 카드 확대 효과
- 📱 반응형 디자인 (모바일 지원)
- 🎬 YouTube 음악 미리보기
- 💫 모던한 UI/UX 디자인

## 파일 구조

```
sound-engineer-portfolio/
├── index.html      # 메인 HTML 파일
├── styles.css      # 스타일시트
├── script.js       # JavaScript 로직
└── README.md       # 이 파일
```

## 로컬에서 실행하기

1. 프로젝트 폴더로 이동:
```bash
cd ~/sound-engineer-portfolio
```

2. 간단한 HTTP 서버 실행 (Python 3):
```bash
python3 -m http.server 8000
```

또는 Node.js가 설치되어 있다면:
```bash
npx http-server -p 8000
```

3. 브라우저에서 접속:
```
http://localhost:8000
```

## Oracle Cloud Infrastructure (OCI) 배포 가이드

**리전**: Canada Southeast (Montreal) - `ca-montreal-1`  
**계정 유형**: 무료 계정 (Always Free Tier)

### 방법 1: OCI Object Storage를 사용한 정적 웹사이트 호스팅 (권장 - 무료)

이 방법은 가장 간단하고 비용 효율적입니다. OCI Always Free Tier에서는 Object Storage를 무료로 사용할 수 있습니다 (10GB까지).

#### 1단계: OCI Object Storage 버킷 생성

1. OCI 콘솔에 로그인
2. 우측 상단에서 **리전을 Canada Southeast (Montreal)** 로 변경
3. **Object Storage & Archive Storage** > **Buckets** 메뉴로 이동
4. **Create Bucket** 클릭
5. 버킷 이름 입력 (예: `bigsummer-portfolio`)
6. **Compartment**: Root compartment 또는 원하는 컴파트먼트 선택
7. **Visibility Type**: Public 선택 (웹사이트 공개용)
8. **Storage Tier**: Standard 선택 (무료 티어)
9. **Create** 클릭

#### 2단계: 정적 웹사이트 호스팅 활성화

1. 생성한 버킷 클릭
2. **Edit Visibility** 클릭
3. **Public** 선택하고 저장
4. 버킷 세부 정보에서 **Edit** 클릭
5. **Enable Object Events** 체크 (선택사항)

#### 3단계: 파일 업로드

OCI CLI를 사용하거나 콘솔에서 직접 업로드할 수 있습니다.

**콘솔에서 업로드:**
1. 버킷 내부에서 **Upload** 클릭
2. `index.html`, `styles.css`, `script.js` 파일 선택
3. 업로드 완료

**OCI CLI 사용 (터미널):**
```bash
# OCI CLI 설치 (아직 설치하지 않은 경우)
# macOS: brew install oci-cli

# 설정 (처음 한 번만)
oci setup config
# - User OCID 입력
# - Tenancy OCID 입력
# - 리전: ca-montreal-1 입력
# - API 키 생성 및 경로 입력

# 리전 설정 확인
oci iam region list

# 파일 업로드 (리전 명시)
oci os object put \
  --bucket-name bigsummer-portfolio \
  --file index.html \
  --content-type text/html \
  --region ca-montreal-1

oci os object put \
  --bucket-name bigsummer-portfolio \
  --file styles.css \
  --content-type text/css \
  --region ca-montreal-1

oci os object put \
  --bucket-name bigsummer-portfolio \
  --file script.js \
  --content-type application/javascript \
  --region ca-montreal-1
```

#### 4단계: 정적 웹사이트 엔드포인트 확인

1. 버킷 세부 정보에서 **Object Storage Hostname** 확인
2. 웹사이트 URL 형식 (Montreal 리전):
   ```
   https://[namespace].objectstorage.ca-montreal-1.oraclecloud.com/n/[namespace]/b/[bucket-name]/o/index.html
   ```
3. 예시:
   ```
   https://axxxxxxxxxx.objectstorage.ca-montreal-1.oraclecloud.com/n/axxxxxxxxxx/b/bigsummer-portfolio/o/index.html
   ```

#### 5단계: 커스텀 도메인 설정

무료 도메인을 사용하여 커스텀 도메인을 설정할 수 있습니다.

**방법 A: OCI DNS Zone 사용 (무료)**

1. **Networking** > **DNS Management** > **Zones** 메뉴로 이동
2. **Create Zone** 클릭
3. Zone Type: **Primary** 선택
4. Zone Name: 구매한 도메인 입력 (예: `bigsummer.xyz`)
5. **Create** 클릭
6. Zone 세부 정보에서 **Nameservers** 확인
7. 도메인 등록업체에서 Nameservers를 OCI Nameservers로 변경
8. Zone 내에서 **Records** 추가:
   - Type: **CNAME**
   - Name: `@` 또는 `www`
   - Target: Object Storage 호스트네임 (예: `[namespace].objectstorage.ca-montreal-1.oraclecloud.com`)
   - TTL: 3600

**방법 B: 외부 DNS 제공업체 사용**

1. 도메인 등록업체의 DNS 설정으로 이동
2. CNAME 레코드 추가:
   - Name: `@` 또는 `www`
   - Value: Object Storage 호스트네임
   - TTL: 3600

**참고**: Object Storage는 직접적인 CNAME을 지원하지 않으므로, Cloudflare 같은 CDN을 사용하거나 OCI API Gateway를 통해 리다이렉트를 설정해야 할 수 있습니다.

### 방법 2: OCI Compute Instance 사용 (무료 티어)

OCI Always Free Tier에서는 다음을 무료로 사용할 수 있습니다:
- 2개의 VM.Standard.E2.1.Micro 인스턴스 (각 1 OCPU, 1GB RAM)
- 또는 1개의 VM.Standard.A1.Flex 인스턴스 (4 OCPU, 24GB RAM)

#### 1단계: Compute Instance 생성

1. **Compute** > **Instances** 메뉴로 이동
2. **Create Instance** 클릭
3. **Name**: `bigsummer-portfolio` 입력
4. **Image**: **Canonical Ubuntu 22.04** 선택 (무료)
5. **Shape**: **VM.Standard.A1.Flex** 선택 (무료 티어)
   - OCPU: 2개 (무료 티어는 최대 4개까지 가능)
   - Memory: 12GB (무료 티어는 최대 24GB까지 가능)
6. **Networking**: 기본 VCN 사용 또는 새로 생성
7. **Add SSH Keys**: 공개 SSH 키 추가
8. **Create** 클릭

#### 2단계: 웹 서버 설치 및 설정

SSH로 인스턴스에 연결:
```bash
ssh -i [your-key].pem ubuntu@[instance-public-ip]
```

Nginx 설치:
```bash
sudo apt update
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

Nginx 설정 파일 수정:
```bash
sudo nano /etc/nginx/sites-available/default
```

다음 내용으로 수정:
```nginx
server {
    listen 80;
    server_name _;
    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

설정 적용:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

#### 3단계: 파일 업로드

SCP를 사용하여 파일 전송:
```bash
scp -i [your-key].pem -r ~/sound-engineer-portfolio/* ubuntu@[instance-ip]:/var/www/html/
```

또는 Git 사용:
```bash
# 인스턴스에서
cd /var/www/html
git clone [your-repo-url] .
```

#### 4단계: 방화벽 설정

OCI 콘솔에서:
1. **Networking** > **Virtual Cloud Networks** 선택
2. 사용 중인 VCN 클릭
3. **Security Lists** 메뉴 선택
4. Default Security List 클릭
5. **Ingress Rules** 섹션에서 **Add Ingress Rules** 클릭
6. 다음 규칙 추가:
   - **Source Type**: CIDR
   - **Source CIDR**: 0.0.0.0/0
   - **IP Protocol**: TCP
   - **Destination Port Range**: 80
   - **Description**: HTTP access
7. HTTPS를 위한 규칙도 추가 (포트 443)
8. **Add Ingress Rules** 클릭

또는 인스턴스에서 직접 방화벽 설정:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### 5단계: SSL 인증서 설정 (HTTPS)

Let's Encrypt 사용 (무료):
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

자동 갱신 설정:
```bash
sudo certbot renew --dry-run
```

Nginx SSL 설정이 자동으로 업데이트됩니다.

**참고**: 무료 도메인을 사용하는 경우, 일부 도메인 제공업체는 Let's Encrypt를 지원하지 않을 수 있습니다. 이 경우 Cloudflare를 사용하여 무료 SSL을 활성화할 수 있습니다.

## 필요한 OCI 정보

배포를 진행하기 위해 다음 정보가 필요합니다:

1. **OCI Tenancy OCID**: 테넌시 식별자
   - **Profile** > **Tenancy** 메뉴에서 확인
2. **Compartment OCID**: 리소스를 배치할 컴파트먼트
   - **Identity & Security** > **Compartments** 메뉴에서 확인
   - 기본적으로 Root compartment 사용 가능
3. **Region**: **Canada Southeast (Montreal)** - `ca-montreal-1`
4. **User OCID**: 사용자 식별자
   - **Profile** > **User Settings** 메뉴에서 확인
5. **API Key**: CLI 사용 시 필요
   - **Profile** > **API Keys** 메뉴에서 생성

## 무료 계정 리소스 제한

OCI Always Free Tier 제한사항:
- **Object Storage**: 10GB 저장 공간
- **Compute**: 
  - VM.Standard.A1.Flex: 최대 4 OCPU, 24GB RAM
  - 또는 VM.Standard.E2.1.Micro: 2개 인스턴스 (각 1 OCPU, 1GB RAM)
- **Bandwidth**: 월 10TB 아웃바운드 트래픽
- **VCN**: 2개까지 생성 가능

이 포트폴리오 웹사이트는 정적 파일만 사용하므로 Object Storage 방법이 가장 적합하며, 무료 티어로 충분합니다.

## 음악 데이터 수정하기

`script.js` 파일의 `musicData` 배열을 수정하여 실제 음악 정보를 추가할 수 있습니다:

```javascript
{
    id: 1,
    title: "음악 제목",
    artist: "아티스트명",
    genre: "장르",
    year: 2024,
    description: "음악 설명",
    youtubeId: "YouTube 비디오 ID",
    thumbnail: "썸네일 이미지 URL"
}
```

YouTube 비디오 ID는 URL에서 가져올 수 있습니다:
- URL: `https://www.youtube.com/watch?v=VIDEO_ID`
- ID: `VIDEO_ID` 부분

## 문제 해결

### YouTube 임베드가 표시되지 않는 경우
- YouTube 비디오가 공개되어 있는지 확인
- 비디오 ID가 올바른지 확인
- 브라우저 콘솔에서 오류 메시지 확인

### OCI Object Storage 접근 문제
- 버킷이 Public으로 설정되어 있는지 확인
- 올바른 URL 형식을 사용하고 있는지 확인
- Content-Type이 올바르게 설정되어 있는지 확인

## 라이선스

이 프로젝트는 개인 포트폴리오 용도로 자유롭게 사용할 수 있습니다.

