# GitHub Actions Secrets 설정

워크플로우 파일:
- `.github/workflows/deploy-oci-static.yml`

다음 Secrets를 GitHub 저장소에 추가하세요.

## Required

- `OCI_USER_OCID`
- `OCI_TENANCY_OCID`
- `OCI_FINGERPRINT`
- `OCI_PRIVATE_KEY_PEM`
- `OCI_CLI_PASSPHRASE`

## Optional (Cloudflare 캐시 퍼지)

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ZONE_ID`

---

## 값 확인 방법

- `OCI_USER_OCID`, `OCI_TENANCY_OCID`, `OCI_FINGERPRINT`:
  - 로컬 `~/.oci/config`에서 확인 가능
- `OCI_PRIVATE_KEY_PEM`:
  - 로컬 `~/.oci/oci_api_key.pem` 파일 전체 내용
- `OCI_CLI_PASSPHRASE`:
  - 키 생성 시 설정한 passphrase

---

## 동작 방식

- `main` 브랜치에 push 시 자동 배포
- 배포 파일:
  - `index.html`
  - `styles.css`
  - `script.js`
  - `Portfolio_list.csv`
  - `portfolio_media_map.json`

