# 톤스튜디오 디스코그래피 크롤러

양하정이 참여한 모든 곡을 톤스튜디오 웹사이트에서 크롤링하는 스크립트입니다.

## 설치

```bash
pip install -r requirements.txt
```

또는 개별 설치:

```bash
pip install requests beautifulsoup4 lxml
```

## 사용 방법

### 1. 기본 사용 (단일 페이지)

```bash
python crawler.py
```

실행 후 URL을 입력하거나 엔터를 눌러 기본 URL(2024년)을 사용합니다.

### 2. 여러 연도 크롤링

스크립트 실행 후 "여러 연도를 크롤링하시겠습니까?" 질문에 `y`를 입력하면
2010년부터 2025년까지 모든 연도 페이지를 자동으로 크롤링합니다.

## 기능

- **양하정 포함 검색**: "Mixed by 양하정"뿐만 아니라 "양하정"이 포함된 모든 텍스트를 찾습니다
- **작업 역할 추출**: REC, MIX, MA 등 작업 역할 자동 추출
- **곡 정보 파싱**: 아티스트, 곡 제목, 앨범 정보 자동 추출
- **연도별 정리**: 연도별로 곡 목록 정리
- **JSON 저장**: 결과를 JSON 파일로 저장

## 출력 형식

```
[2024년] - 10곡
--------------------------------------------------------------------------------

1. 아티스트: young
   곡 제목: 겨울
   작업 역할: REC, MIX, MA
   원문: young – '겨울'[REC, MIX, MA] Mixed by 양하정...
```

## 결과 파일

크롤링 결과는 `yanghajung_songs.json` 파일로 저장됩니다.

## 예시

```python
# 직접 사용
from crawler import crawl_tonestudio_page

url = "https://tonestudio.co.kr/tone-discography/d-2024/"
songs = crawl_tonestudio_page(url)

for song in songs:
    print(f"{song['artist']} - {song['title']}")
```

## 주의사항

- 웹사이트의 robots.txt와 이용약관을 확인하세요
- 과도한 요청은 서버에 부하를 줄 수 있으니 적절한 간격을 두고 사용하세요
- 웹사이트 구조가 변경되면 파싱 로직을 수정해야 할 수 있습니다

