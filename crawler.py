#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
톤스튜디오 디스코그래피 크롤러
양하정이 참여한 모든 곡을 연도별로 수집합니다.
"""

import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict
import json
from urllib.parse import urljoin, urlparse

def crawl_tonestudio_page(url):
    """
    톤스튜디오 디스코그래피 페이지를 크롤링하여 양하정이 참여한 곡을 찾습니다.
    
    Args:
        url: 크롤링할 웹페이지 URL
        
    Returns:
        list: 양하정이 참여한 곡들의 리스트
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 페이지에서 모든 텍스트를 가져옴
        page_text = soup.get_text()
        
        # 연도 추출 (URL이나 페이지에서)
        year = extract_year_from_url(url) or extract_year_from_page(soup)
        
        # 양하정이 포함된 모든 라인 찾기
        songs = find_yanghajung_songs(soup, year)
        
        return songs
        
    except requests.RequestException as e:
        print(f"요청 오류: {e}")
        return []
    except Exception as e:
        print(f"크롤링 오류: {e}")
        return []

def extract_year_from_url(url):
    """URL에서 연도 추출"""
    match = re.search(r'/(\d{4})/', url)
    if match:
        return match.group(1)
    return None

def extract_year_from_page(soup):
    """페이지에서 연도 추출"""
    # h1, h2 태그에서 연도 찾기
    for tag in soup.find_all(['h1', 'h2', 'h3']):
        text = tag.get_text()
        match = re.search(r'(\d{4})', text)
        if match:
            year = match.group(1)
            if 2010 <= int(year) <= 2025:
                return year
    return None

def find_yanghajung_songs(soup, year):
    """
    페이지에서 양하정이 포함된 모든 곡을 찾습니다.
    """
    songs = []
    
    # 다양한 패턴으로 양하정 찾기
    patterns = [
        r'양하정',
        r'Mixed by 양하정',
        r'Mixed by.*양하정',
        r'양하정.*Mixed',
        r'REC.*양하정',
        r'양하정.*REC',
        r'MIX.*양하정',
        r'양하정.*MIX',
        r'MA.*양하정',
        r'양하정.*MA',
    ]
    
    # 모든 텍스트 노드 찾기
    all_text_elements = soup.find_all(string=True)
    
    for text in all_text_elements:
        if '양하정' in text:
            # 부모 요소 찾기
            parent = text.parent
            if parent:
                # 전체 라인 텍스트 가져오기
                line_text = parent.get_text(strip=True)
                
                # 곡 정보 파싱
                song_info = parse_song_info(line_text, year)
                if song_info:
                    # 중복 제거
                    if not any(s['title'] == song_info['title'] and 
                              s['artist'] == song_info['artist'] 
                              for s in songs):
                        songs.append(song_info)
    
    # 리스트 항목에서도 찾기
    for li in soup.find_all(['li', 'p', 'div']):
        text = li.get_text()
        if '양하정' in text:
            song_info = parse_song_info(text, year)
            if song_info:
                if not any(s['title'] == song_info['title'] and 
                          s['artist'] == song_info['artist'] 
                          for s in songs):
                    songs.append(song_info)
    
    return songs

def parse_song_info(text, year):
    """
    텍스트에서 곡 정보를 파싱합니다.
    """
    # 양하정이 없는 경우 None 반환
    if '양하정' not in text:
        return None
    
    # 기본 정보 초기화
    artist = None
    title = None
    album = None
    roles = []
    
    # 작업 역할 추출
    if '[REC' in text or 'REC,' in text:
        roles.append('REC')
    if '[MIX' in text or 'MIX,' in text or 'Mixed by' in text:
        roles.append('MIX')
    if '[MA' in text or 'MA]' in text:
        roles.append('MA')
    
    # 곡 제목 추출 (따옴표나 작은따옴표 사이)
    title_patterns = [
        r"['""]([^'""]+)['""]",
        r"['']([^'']+)['']",
        r"–\s*['""]([^'""]+)['""]",
        r"–\s*['']([^'']+)['']",
        r"–\s*([^\[\(]+?)(?:\s*\[|$)",
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, text)
        if match:
            title = match.group(1).strip()
            break
    
    # 아티스트 추출 (곡 제목 앞 부분)
    if title:
        # 제목 앞 부분에서 아티스트 추출
        before_title = text.split(title)[0] if title in text else text
        # – 또는 - 앞의 텍스트가 아티스트일 가능성이 높음
        artist_match = re.search(r'([^–\-]+?)(?:\s*–|\s*-|\s*\[)', before_title)
        if artist_match:
            artist = artist_match.group(1).strip()
        else:
            # 첫 번째 부분을 아티스트로
            parts = before_title.split()
            if parts:
                artist = ' '.join(parts[:2]).strip()
    
    # 아티스트가 없으면 전체 라인에서 추출 시도
    if not artist:
        # 일반적인 패턴: 아티스트 – 곡제목
        match = re.match(r'^([^–\-]+?)\s*[–\-]\s*', text)
        if match:
            artist = match.group(1).strip()
    
    # 앨범 정보 추출 (Track 번호나 앨범명)
    album_match = re.search(r'Track\s*(\d+)', text, re.IGNORECASE)
    if album_match:
        album = f"Track {album_match.group(1)}"
    
    # 곡 제목이 없으면 None 반환
    if not title:
        return None
    
    return {
        'year': year or 'Unknown',
        'artist': artist or 'Unknown',
        'title': title,
        'album': album,
        'roles': roles,
        'raw_text': text.strip()
    }

def crawl_multiple_years(base_url, start_year=2010, end_year=2025):
    """
    여러 연도의 페이지를 크롤링합니다.
    
    Args:
        base_url: 기본 URL (예: https://tonestudio.co.kr/tone-discography/d-2024/)
        start_year: 시작 연도
        end_year: 종료 연도
        
    Returns:
        dict: 연도별 곡 목록
    """
    all_songs = defaultdict(list)
    
    for year in range(start_year, end_year + 1):
        # URL 패턴 시도
        url_patterns = [
            f"{base_url.replace('2024', str(year))}",
            f"https://tonestudio.co.kr/tone-discography/d-{year}/",
            f"https://tonestudio.co.kr/tone-discography/{year}/",
        ]
        
        print(f"\n[{year}년 크롤링 시작]")
        
        for url in url_patterns:
            try:
                songs = crawl_tonestudio_page(url)
                if songs:
                    all_songs[year].extend(songs)
                    print(f"  ✓ {url}: {len(songs)}곡 발견")
                    break
            except Exception as e:
                print(f"  ✗ {url}: {e}")
                continue
    
    return dict(all_songs)

def print_results(songs_by_year):
    """
    결과를 보기 좋게 출력합니다.
    """
    print("\n" + "="*80)
    print("양하정 참여 곡 목록 (연도별)")
    print("="*80)
    
    for year in sorted(songs_by_year.keys(), reverse=True):
        songs = songs_by_year[year]
        if songs:
            print(f"\n[{year}년] - {len(songs)}곡")
            print("-" * 80)
            
            for i, song in enumerate(songs, 1):
                print(f"\n{i}. 아티스트: {song['artist']}")
                print(f"   곡 제목: {song['title']}")
                if song['album']:
                    print(f"   앨범/트랙: {song['album']}")
                if song['roles']:
                    print(f"   작업 역할: {', '.join(song['roles'])}")
                print(f"   원문: {song['raw_text'][:100]}...")

def save_to_json(songs_by_year, filename='yanghajung_songs.json'):
    """
    결과를 JSON 파일로 저장합니다.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(songs_by_year, f, ensure_ascii=False, indent=2)
    print(f"\n결과가 {filename}에 저장되었습니다.")

def main():
    """
    메인 함수
    """
    print("톤스튜디오 디스코그래피 크롤러")
    print("양하정 참여 곡 수집\n")
    
    # 기본 URL
    base_url = "https://tonestudio.co.kr/tone-discography/d-2024/"
    
    # 단일 페이지 크롤링
    print("단일 페이지 크롤링 모드")
    print(f"URL: {base_url}")
    
    url = input("\n크롤링할 URL을 입력하세요 (엔터 시 기본 URL 사용): ").strip()
    if not url:
        url = base_url
    
    # 단일 페이지 크롤링
    songs = crawl_tonestudio_page(url)
    
    if songs:
        print(f"\n✓ {len(songs)}곡 발견!")
        for song in songs:
            print(f"\n- {song['artist']} – '{song['title']}'")
            if song['roles']:
                print(f"  작업: {', '.join(song['roles'])}")
    else:
        print("\n✗ 양하정이 참여한 곡을 찾을 수 없습니다.")
    
    # 여러 연도 크롤링 여부 확인
    multi_year = input("\n여러 연도를 크롤링하시겠습니까? (y/n): ").strip().lower()
    
    if multi_year == 'y':
        start_year = int(input("시작 연도 (기본: 2010): ") or "2010")
        end_year = int(input("종료 연도 (기본: 2025): ") or "2025")
        
        all_songs = crawl_multiple_years(base_url, start_year, end_year)
        
        # 결과 출력
        print_results(all_songs)
        
        # JSON 저장
        save_to_json(all_songs)

if __name__ == "__main__":
    main()

