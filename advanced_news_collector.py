#!/usr/bin/env python3
"""
Enhanced Advanced News Collector
강화된 중복 제거 기능이 포함된 RSS 피드 수집 모듈
"""

import feedparser
import requests
import re
import time
import hashlib
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
from typing import List, Dict, Set, Tuple
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedNewsCollector:
    def __init__(self):
        # 음악 업계 RSS 피드 목록
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
            'ep', 'lp', 'vinyl', 'digital', 'radio', 'playlist'
        }
        
        # 중복 제거 설정
        self.duplicate_threshold = 0.85  # 85% 유사도 기준
        self.collected_news = []
        
        # 중복 검사용 캐시
        self.url_cache = set()
        self.title_cache = set()
        self.content_hashes = set()
    
    def normalize_url(self, url: str) -> str:
        """URL 정규화 (쿼리 파라미터 제거, 프로토콜 통일)"""
        try:
            parsed = urlparse(url.lower())
            
            # 쿼리 파라미터에서 중요하지 않은 것들 제거
            important_params = ['id', 'p', 'article_id', 'post_id']
            query_dict = parse_qs(parsed.query)
            
            # 중요한 파라미터만 유지
            filtered_query = {}
            for param in important_params:
                if param in query_dict:
                    filtered_query[param] = query_dict[param]
            
            # 정규화된 URL 생성
            normalized = f"{parsed.netloc}{parsed.path}"
            
            # 중요한 쿼리 파라미터가 있으면 추가
            if filtered_query:
                query_str = '&'.join([f"{k}={v[0]}" for k, v in filtered_query.items()])
                normalized += f"?{query_str}"
                
            return normalized
            
        except Exception as e:
            logger.warning(f"URL 정규화 실패: {url} - {e}")
            return url.lower()
    
    def normalize_title(self, title: str) -> str:
        """제목 정규화 (특수문자, 공백 정리)"""
        # 소문자 변환
        normalized = title.lower().strip()
        
        # 특수문자 정리
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # 연속된 공백을 하나로
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # 일반적인 접두사/접미사 제거
        prefixes_to_remove = ['exclusive', 'breaking', 'watch', 'listen', 'new']
        for prefix in prefixes_to_remove:
            if normalized.startswith(prefix + ' '):
                normalized = normalized[len(prefix + ' '):]
        
        return normalized.strip()
    
    def generate_content_hash(self, title: str, description: str) -> str:
        """내용 기반 해시 생성"""
        # 제목과 설명을 정규화
        norm_title = self.normalize_title(title)
        norm_desc = re.sub(r'[^\w\s]', '', description.lower())
        
        # 핵심 단어만 추출 (짧은 단어 제외)
        words = []
        for text in [norm_title, norm_desc]:
            text_words = [w for w in text.split() if len(w) > 3]
            words.extend(text_words[:10])  # 각각에서 최대 10개 단어
        
        # 해시 생성
        content = ' '.join(sorted(set(words)))
        return hashlib.md5(content.encode()).hexdigest()
    
    def calculate_title_similarity(self, title1: str, title2: str) -> float:
        """제목 유사도 계산 (Jaccard 유사도 기반)"""
        norm1 = set(self.normalize_title(title1).split())
        norm2 = set(self.normalize_title(title2).split())
        
        if not norm1 or not norm2:
            return 0.0
        
        intersection = len(norm1.intersection(norm2))
        union = len(norm1.union(norm2))
        
        return intersection / union if union > 0 else 0.0
    
    def extract_key_entities(self, title: str, description: str) -> Set[str]:
        """핵심 엔티티 추출 (아티스트명, 앨범명 등)"""
        entities = set()
        text = f"{title} {description}"
        
        # 따옴표 안의 텍스트 (앨범명, 곡명)
        quote_patterns = [r'"([^"]+)"', r"'([^']+)'", r"'([^']+)'", r""([^"]+)""]
        for pattern in quote_patterns:
            matches = re.findall(pattern, text)
            entities.update(match.lower() for match in matches if len(match) > 2)
        
        # 대문자로 시작하는 단어들 (아티스트명)
        artist_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        matches = re.findall(artist_pattern, text)
        
        # 알려진 아티스트/밴드명 필터링
        known_artists = {
            'taylor swift', 'billie eilish', 'ariana grande', 'drake', 'metallica',
            'bts', 'blackpink', 'twice', 'stray kids', 'newjeans', 'ive',
            'my chemical romance', 'mayday parade', 'mother love bone'
        }
        
        for match in matches:
            if (match.lower() in known_artists or 
                len(match.split()) >= 2 and 
                match not in ['New Album', 'Live From', 'Very Imminent']):
                entities.add(match.lower())
        
        return entities
    
    def is_duplicate_advanced(self, news1: Dict, news2: Dict) -> bool:
        """강화된 중복 검사"""
        
        # 1. URL 기반 검사 (가장 확실한 방법)
        url1 = self.normalize_url(news1.get('link', ''))
        url2 = self.normalize_url(news2.get('link', ''))
        
        if url1 and url2 and url1 == url2:
            logger.debug(f"URL 중복 발견: {url1}")
            return True
        
        # 2. 제목 유사도 검사
        title1 = news1.get('title', '')
        title2 = news2.get('title', '')
        
        title_similarity = self.calculate_title_similarity(title1, title2)
        
        # 제목이 90% 이상 유사하면 중복
        if title_similarity >= 0.9:
            logger.debug(f"제목 유사도 중복: {title_similarity:.2f} - '{title1[:30]}...' vs '{title2[:30]}...'")
            return True
        
        # 3. 내용 해시 기반 검사
        hash1 = self.generate_content_hash(title1, news1.get('description', ''))
        hash2 = self.generate_content_hash(title2, news2.get('description', ''))
        
        if hash1 == hash2:
            logger.debug(f"내용 해시 중복: {hash1}")
            return True
        
        # 4. 엔티티 기반 검사 (높은 유사도 + 엔티티 일치)
        if title_similarity >= 0.7:  # 70% 이상 유사한 경우만
            entities1 = self.extract_key_entities(title1, news1.get('description', ''))
            entities2 = self.extract_key_entities(title2, news2.get('description', ''))
            
            if entities1 and entities2:
                entity_overlap = len(entities1.intersection(entities2))
                entity_union = len(entities1.union(entities2))
                
                if entity_union > 0:
                    entity_similarity = entity_overlap / entity_union
                    
                    # 제목 유사도 + 엔티티 유사도가 높으면 중복
                    combined_similarity = (title_similarity * 0.6) + (entity_similarity * 0.4)
                    
                    if combined_similarity >= 0.8:
                        logger.debug(f"엔티티 기반 중복: 제목={title_similarity:.2f}, 엔티티={entity_similarity:.2f}")
                        return True
        
        # 5. 같은 소스에서 같은 시간대의 유사한 뉴스
        source1 = news1.get('source', '')
        source2 = news2.get('source', '')
        
        if (source1 == source2 and title_similarity >= 0.6):
            time1 = news1.get('published_date', '')
            time2 = news2.get('published_date', '')
            
            if time1 and time2:
                try:
                    # 시간 차이 계산
                    dt1 = datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
                    dt2 = datetime.strptime(time2, '%Y-%m-%d %H:%M:%S')
                    time_diff = abs((dt1 - dt2).total_seconds())
                    
                    # 같은 소스에서 1시간 이내의 유사한 뉴스는 중복
                    if time_diff <= 3600:  # 1시간
                        logger.debug(f"시간+소스 기반 중복: {source1}, 시간차={time_diff/60:.1f}분")
                        return True
                        
                except ValueError:
                    pass
        
        return False
    
    def remove_duplicates_enhanced(self, news_list: List[Dict]) -> List[Dict]:
        """강화된 중복 제거"""
        logger.info(f"강화된 중복 제거 시작: {len(news_list)}개 뉴스")
        
        unique_news = []
        removed_count = 0
        
        # URL 캐시 초기화
        url_cache = set()
        
        for news in news_list:
            is_duplicate = False
            
            # 빠른 URL 검사
            normalized_url = self.normalize_url(news.get('link', ''))
            if normalized_url in url_cache:
                is_duplicate = True
                removed_count += 1
                logger.debug(f"URL 캐시 중복 제거: {normalized_url}")
            else:
                url_cache.add(normalized_url)
                
                # 기존 뉴스와 상세 비교
                for existing_news in unique_news:
                    if self.is_duplicate_advanced(news, existing_news):
                        is_duplicate = True
                        removed_count += 1
                        
                        # 더 나은 뉴스로 교체할지 결정
                        should_replace = self.should_replace_news(existing_news, news)
                        
                        if should_replace:
                            unique_news.remove(existing_news)
                            unique_news.append(news)
                            logger.debug(f"더 나은 뉴스로 교체: {news.get('title', '')[:30]}...")
                        
                        break
            
            # 중복이 아니면 추가
            if not is_duplicate:
                unique_news.append(news)
        
        logger.info(f"중복 제거 완료: {len(news_list)} -> {len(unique_news)}개 (제거: {removed_count}개)")
        
        # 중복 제거 통계 출력
        if removed_count > 0:
            removal_rate = (removed_count / len(news_list)) * 100
            logger.info(f"중복 제거율: {removal_rate:.1f}%")
            
            # 주요 중복 패턴 분석
            self.analyze_duplicate_patterns(news_list, unique_news)
        
        return unique_news
    
    def should_replace_news(self, existing: Dict, new: Dict) -> bool:
        """두 중복 뉴스 중 어느 것을 선택할지 결정"""
        
        # 1. 소스 신뢰도 비교
        source_priority = {
            'billboard.com': 5,
            'rollingstone.com': 4,
            'pitchfork.com': 3,
            'variety.com': 4,
            'nme.com': 2,
            'consequence.net': 2,
            'stereogum.com': 2,
            'musicbusinessworldwide.com': 3
        }
        
        existing_priority = source_priority.get(existing.get('source', ''), 1)
        new_priority = source_priority.get(new.get('source', ''), 1)
        
        if new_priority > existing_priority:
            return True
        elif new_priority < existing_priority:
            return False
        
        # 2. 내용 길이 비교 (더 자세한 것 선택)
        existing_content_length = len(existing.get('description', ''))
        new_content_length = len(new.get('description', ''))
        
        if new_content_length > existing_content_length * 1.2:  # 20% 이상 길면
            return True
        
        # 3. 발행 시간 비교 (더 최신 것 선택)
        try:
            existing_time = datetime.strptime(existing.get('published_date', ''), '%Y-%m-%d %H:%M:%S')
            new_time = datetime.strptime(new.get('published_date', ''), '%Y-%m-%d %H:%M:%S')
            
            if new_time > existing_time:
                return True
        except ValueError:
            pass
        
        return False
    
    def analyze_duplicate_patterns(self, original_list: List[Dict], unique_list: List[Dict]):
        """중복 패턴 분석 및 로깅"""
        removed_count = len(original_list) - len(unique_list)
        
        # 제목별 중복 통계
        title_counts = {}
        for news in original_list:
            normalized_title = self.normalize_title(news.get('title', ''))
            # 제목의 첫 5단어로 그룹화
            title_key = ' '.join(normalized_title.split()[:5])
            title_counts[title_key] = title_counts.get(title_key, 0) + 1
        
        # 중복이 많은 제목들 출력
        high_duplicate_titles = [(title, count) for title, count in title_counts.items() if count > 1]
        high_duplicate_titles.sort(key=lambda x: x[1], reverse=True)
        
        if high_duplicate_titles:
            logger.info("주요 중복 뉴스:")
            for title, count in high_duplicate_titles[:3]:
                logger.info(f"  '{title}...': {count}개")
    
    def fetch_rss_feed(self, url: str) -> List[Dict]:
        """RSS 피드에서 뉴스 수집"""
        try:
            logger.info(f"RSS 피드 수집 중: {url}")
            
            # User-Agent 설정
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            news_items = []
            
            # 최근 7일 이내 뉴스만 수집
            cutoff_time = datetime.now() - timedelta(days=7)
            
            for entry in feed.entries[:20]:  # 최대 20개 항목
                try:
                    # 발행 시간 확인
                    pub_time = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        try:
                            pub_time = datetime(*entry.published_parsed[:6])
                        except (ValueError, TypeError):
                            pass
                    
                    # 날짜 필터링
                    if pub_time and pub_time < cutoff_time:
                        continue
                    
                    title = entry.get('title', '').strip()
                    description = entry.get('description', '').strip()
                    link = entry.get('link', '')
                    
                    if not title or not description:
                        continue
                    
                    # HTML 태그 제거
                    description = re.sub(r'<[^>]+>', '', description)
                    description = re.sub(r'\s+', ' ', description).strip()
                    
                    # 음악 관련성 검사
                    relevance = self.calculate_music_relevance(title, description)
                    if relevance < 0.2:  # 20% 미만은 제외
                        continue
                    
                    # 고유 ID 생성
                    news_id = hashlib.md5(link.encode()).hexdigest()[:12]
                    
                    news_item = {
                        'id': news_id,
                        'title': title,
                        'description': description,
                        'link': link,
                        'url': link,  # 호환성
                        'source': urlparse(url).netloc,
                        'published': entry.get('published', ''),
                        'published_date': pub_time.strftime('%Y-%m-%d %H:%M:%S') if pub_time else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'relevance_score': relevance,
                        'entities': list(self.extract_key_entities(title, description)),
                        'feed_url': url,
                        'collected_at': datetime.now().isoformat()
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
    
    def calculate_music_relevance(self, title: str, description: str) -> float:
        """음악 관련성 점수 계산"""
        text = (title + " " + description).lower()
        
        # 음악 키워드 매칭
        keyword_matches = sum(1 for keyword in self.music_keywords if keyword in text)
        keyword_score = min(keyword_matches / 5, 1.0)
        
        # 도메인 기반 점수
        domain_score = 0.8  # RSS 피드가 이미 음악 관련
        
        return (keyword_score * 0.6) + (domain_score * 0.4)
    
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
        
        if success_rate < 95:
            logger.warning(f"수집 성공률이 목표(95%) 미달: {success_rate:.1f}%")
        
        # 강화된 중복 제거
        unique_news = self.remove_duplicates_enhanced(all_news)
        
        # 관련성 점수로 정렬
        unique_news.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        self.collected_news = unique_news
        logger.info(f"최종 수집된 뉴스: {len(unique_news)}개")
        
        return unique_news


# 테스트 코드
if __name__ == "__main__":
    collector = AdvancedNewsCollector()
    
    # 중복 제거 테스트
    test_news = [
        {
            'title': 'Taylor Swift Announces New Album',
            'description': 'Pop star announces new music',
            'link': 'https://billboard.com/news/taylor-swift-album',
            'source': 'billboard.com',
            'published_date': '2025-08-12 10:00:00'
        },
        {
            'title': 'Taylor Swift Announces New Album, The Life of a Showgirl',
            'description': 'Taylor Swift has announced her upcoming album',
            'link': 'https://rollingstone.com/music/taylor-swift-new-album',
            'source': 'rollingstone.com', 
            'published_date': '2025-08-12 10:30:00'
        }
    ]
    
    print("=== 중복 제거 테스트 ===")
    unique = collector.remove_duplicates_enhanced(test_news)
    print(f"원본: {len(test_news)}개 -> 결과: {len(unique)}개")
    
    for news in unique:
        print(f"- {news['title'][:50]}... ({news['source']})")
