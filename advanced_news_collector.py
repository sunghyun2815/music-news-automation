#!/usr/bin/env python3
"""
Advanced News Collector
RSS 피드 수집 및 엔티티 기반 중복 제거 모듈
"""

import feedparser
import requests
import re
import time
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from textdistance import jaccard
import logging
from typing import List, Dict, Set, Tuple
import hashlib

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedNewsCollector:
    def __init__(self):
        # 음악 업계 RSS 피드 목록 (8개)
        self.rss_feeds = [
            "https://www.billboard.com/feed/",
            "https://pitchfork.com/rss/news/",
            "https://www.rollingstone.com/music/music-news/feed/",
            "https://www.musicbusinessworldwide.com/feed/",
            "https://variety.com/music/feed/",
            "https://www.nme.com/news/music/feed",
            "https://consequenceofsound.net/feed/",
            "https://www.stereogum.com/feed/"
        ]
        
        # 음악 관련 키워드
        self.music_keywords = {
            'artist', 'band', 'singer', 'musician', 'album', 'song', 'track', 'music', 
            'concert', 'tour', 'festival', 'record', 'label', 'streaming', 'spotify', 
            'apple music', 'youtube music', 'billboard', 'chart', 'grammy', 'award',
            'producer', 'songwriter', 'collaboration', 'release', 'debut', 'single',
            'ep', 'lp', 'vinyl', 'digital', 'radio', 'playlist', 'genre', 'rock',
            'pop', 'hip hop', 'rap', 'jazz', 'classical', 'electronic', 'country',
            'folk', 'blues', 'metal', 'punk', 'indie', 'alternative', 'r&b', 'soul'
        }
        
        # 수집된 뉴스 저장
        self.collected_news = []
        self.duplicate_threshold = 0.9  # 90% 유사도 기준
        
    def extract_entities(self, text: str) -> Set[str]:
        """텍스트에서 주요 엔티티 추출"""
        # 간단한 엔티티 추출 (대문자로 시작하는 단어들)
        entities = set()
        
        # 아티스트명, 앨범명 등을 위한 패턴
        patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # 대문자로 시작하는 단어들
            r'"([^"]+)"',  # 따옴표 안의 텍스트 (앨범명, 곡명)
            r"'([^']+)'",  # 작은따옴표 안의 텍스트
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            entities.update(matches)
            
        return entities
    
    def calculate_music_relevance(self, title: str, description: str) -> float:
        """음악 관련성 점수 계산 (0-1)"""
        text = (title + " " + description).lower()
        
        # 음악 키워드 매칭
        keyword_matches = sum(1 for keyword in self.music_keywords if keyword in text)
        keyword_score = min(keyword_matches / 5, 1.0)  # 최대 5개 키워드로 정규화
        
        # 도메인 기반 점수 (음악 전문 사이트)
        domain_score = 0.8  # RSS 피드가 이미 음악 관련이므로 기본 점수
        
        return (keyword_score * 0.6) + (domain_score * 0.4)
    
    def is_duplicate(self, news1: Dict, news2: Dict) -> bool:
        """엔티티 기반 중복 검사"""
        # 제목 유사도
        title_similarity = jaccard(news1['title'].lower(), news2['title'].lower())
        
        # 엔티티 유사도
        entities1 = self.extract_entities(news1['title'] + " " + news1['description'])
        entities2 = self.extract_entities(news2['title'] + " " + news2['description'])
        
        if entities1 and entities2:
            entity_similarity = len(entities1.intersection(entities2)) / len(entities1.union(entities2))
        else:
            entity_similarity = 0
        
        # 종합 유사도 (제목 70%, 엔티티 30%)
        overall_similarity = (title_similarity * 0.7) + (entity_similarity * 0.3)
        
        return overall_similarity >= self.duplicate_threshold
    
    def remove_duplicates(self, news_list: List[Dict]) -> List[Dict]:
        """고급 중복 제거"""
        unique_news = []
        
        for news in news_list:
            is_duplicate_found = False
            
            for existing_news in unique_news:
                if self.is_duplicate(news, existing_news):
                    # 더 신뢰할 만한 소스나 더 자세한 내용을 가진 뉴스를 선택
                    if len(news['description']) > len(existing_news['description']):
                        # 기존 뉴스를 새 뉴스로 교체
                        unique_news.remove(existing_news)
                        unique_news.append(news)
                    is_duplicate_found = True
                    break
            
            if not is_duplicate_found:
                unique_news.append(news)
        
        logger.info(f"중복 제거: {len(news_list)} -> {len(unique_news)} 개 뉴스")
        return unique_news
    
    def fetch_rss_feed(self, url: str) -> List[Dict]:
        """RSS 피드에서 뉴스 수집"""
        try:
            logger.info(f"RSS 피드 수집 중: {url}")
            
            # User-Agent 설정으로 차단 방지
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            news_items = []
            
            # 최근 7일 이내 뉴스만 수집 (2025년 6월 17일 이후)
            cutoff_time = datetime(2025, 6, 17, 0, 0, 0)  # 2025년 6월 17일 00:00:00
            current_time = datetime.now()
            
            for entry in feed.entries[:20]:  # 최대 20개 항목
                try:
                    # 발행 시간 확인 - 2025년 6월 17일 이후만 허용
                    pub_time = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        try:
                            pub_time = datetime(*entry.published_parsed[:6])
                        except (ValueError, TypeError):
                            # 날짜 파싱 실패 시 제목/설명에서 날짜 추출 시도
                            pass
                    
                    # 발행 시간이 없거나 파싱 실패 시 제목/설명에서 날짜 확인
                    if pub_time is None:
                        text_content = (entry.get('title', '') + ' ' + entry.get('description', '')).lower()
                        # 2024년 언급이 있으면 제외
                        if '2024' in text_content:
                            continue
                        # 2025년 언급이 없으면 제외 (최신 뉴스가 아닐 가능성)
                        if '2025' not in text_content:
                            continue
                    else:
                        # 발행 시간이 cutoff_time 이전이면 제외
                        if pub_time < cutoff_time:
                            continue
                        # 2025년이 아닌 뉴스 제외
                        if pub_time.year != 2025:
                            continue
                    
                    title = entry.get('title', '').strip()
                    description = entry.get('description', '').strip()
                    link = entry.get('link', '')
                    
                    if not title or not description:
                        continue
                    
                    # HTML 태그 제거
                    description = re.sub(r'<[^>]+>', '', description)
                    
                    # 음악 관련성 검사
                    relevance = self.calculate_music_relevance(title, description)
                    if relevance < 0.3:  # 30% 미만은 제외
                        continue
                    
                    news_item = {
                        'title': title,
                        'description': description,
                        'link': link,
                        'source': urlparse(url).netloc,
                        'published': entry.get('published', ''),
                        'published_date': pub_time.strftime('%Y-%m-%d %H:%M:%S') if pub_time else 'Unknown',
                        'relevance_score': relevance,
                        'entities': list(self.extract_entities(title + " " + description))
                    }
                    
                    news_items.append(news_item)
                    
                except Exception as e:
                    logger.warning(f"뉴스 항목 처리 오류: {e}")
                    continue
            
            logger.info(f"{url}에서 {len(news_items)}개 뉴스 수집 완료")
            return news_items
            
        except Exception as e:
            logger.error(f"RSS 피드 수집 실패 {url}: {e}")
            return []
    
    def collect_all_news(self) -> List[Dict]:
        """모든 RSS 피드에서 뉴스 수집"""
        all_news = []
        successful_feeds = 0
        
        for feed_url in self.rss_feeds:
            news_items = self.fetch_rss_feed(feed_url)
            if news_items:
                all_news.extend(news_items)
                successful_feeds += 1
            
            # 요청 간격 조절
            time.sleep(1)
        
        success_rate = (successful_feeds / len(self.rss_feeds)) * 100
        logger.info(f"RSS 피드 수집 완료: {successful_feeds}/{len(self.rss_feeds)} ({success_rate:.1f}%)")
        logger.info(f"날짜 필터링: 2025년 6월 17일 이후 뉴스만 수집")
        
        if success_rate < 95:
            logger.warning(f"수집 성공률이 목표(95%) 미달: {success_rate:.1f}%")
        
        # 중복 제거
        unique_news = self.remove_duplicates(all_news)
        
        # 관련성 점수로 정렬
        unique_news.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        self.collected_news = unique_news
        logger.info(f"최종 수집된 뉴스: {len(unique_news)}개")
        
        return unique_news

if __name__ == "__main__":
    collector = AdvancedNewsCollector()
    news = collector.collect_all_news()
    
    print(f"\n수집된 뉴스 {len(news)}개:")
    for i, item in enumerate(news[:5], 1):
        print(f"{i}. {item['title']}")
        print(f"   소스: {item['source']}")
        print(f"   관련성: {item['relevance_score']:.2f}")
        print()

