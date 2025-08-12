#!/usr/bin/env python3
"""
Enhanced Advanced News Collector - FIXED VERSION
강화된 중복 제거 기능이 포함된 RSS 피드 수집 모듈 (수정된 버전)
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
        
        # 중복 제거 설정 - 더 엄격하게 조정
        self.duplicate_threshold = 0.75  # 0.85 → 0.75로 낮춤
        self.collected_news = []
        
        # 중복 검사용 캐시
        self.url_cache = set()
        self.title_cache = set()
        self.content_hashes = set()
        
        # 인기 아티스트별 더 엄격한 중복 검사
        self.popular_artists = [
            'taylor swift', 'bts', 'blackpink', 'drake', 'ariana grande', 
            'billie eilish', 'dua lipa', 'olivia rodrigo', 'travis scott', 'kendrick lamar'
        ]
    
    def normalize_url(self, url: str) -> str:
        """URL 정규화 - 개선된 버전"""
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
            
            # 정규화된 URL 생성 (도메인 + 경로만)
            normalized = f"{parsed.netloc}{parsed.path}"
            
            # 슬래시 정리
            normalized = re.sub(r'/+$', '', normalized)  # 끝의 슬래시 제거
            normalized = re.sub(r'/+', '/', normalized)  # 연속 슬래시 정리
            
            return normalized
            
        except Exception as e:
            logger.warning(f"URL 정규화 실패: {url} - {e}")
            return url.lower()
    
    def normalize_title(self, title: str) -> str:
        """제목 정규화 - 개선된 버전"""
        # 소문자 변환
        normalized = title.lower().strip()
        
        # 특수문자 정리 (따옴표는 보존)
        normalized = re.sub(r'[^\w\s\'\"''""]', ' ', normalized)
        
        # 연속된 공백을 하나로
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # 일반적인 접두사 제거 (더 포괄적으로)
        prefixes_to_remove = [
            'exclusive', 'breaking', 'watch', 'listen', 'new', 'stream',
            'premiere', 'first look', 'video', 'audio', 'live', 'official'
        ]
        
        for prefix in prefixes_to_remove:
            pattern = f'^{prefix}\\s+'
            normalized = re.sub(pattern, '', normalized)
        
        # 끝의 불필요한 단어들 제거
        suffixes_to_remove = ['watch', 'listen', 'video', 'audio', 'stream']
        for suffix in suffixes_to_remove:
            pattern = f'\\s+{suffix}$'
            normalized = re.sub(pattern, '', normalized)
        
        return normalized.strip()
    
    def extract_core_keywords(self, title: str, description: str) -> Set[str]:
        """핵심 키워드 추출 - 새로운 메소드"""
        text = f"{title} {description}".lower()
        
        # 아티스트명 추출
        artist_names = set()
        for artist in self.popular_artists:
            if artist in text:
                artist_names.add(artist)
        
        # 다른 잠재적 아티스트명 추출 (대문자로 시작하는 단어들)
        artist_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        matches = re.findall(artist_pattern, f"{title} {description}")
        for match in matches:
            if len(match.split()) <= 3 and len(match) > 2:  # 3단어 이하, 2글자 이상
                artist_names.add(match.lower())
        
        # 핵심 행동 키워드
        action_keywords = set()
        actions = ['announces', 'releases', 'debuts', 'shares', 'drops', 'reveals', 'teases']
        for action in actions:
            if action in text:
                action_keywords.add(action)
        
        # 음악 관련 키워드
        music_keywords = set()
        music_terms = ['album', 'song', 'tour', 'concert', 'single', 'ep', 'collaboration']
        for term in music_terms:
            if term in text:
                music_keywords.add(term)
        
        return artist_names | action_keywords | music_keywords
    
    def generate_content_hash(self, title: str, description: str) -> str:
        """내용 기반 해시 생성 - 개선된 버전"""
        # 핵심 키워드 추출
        core_keywords = self.extract_core_keywords(title, description)
        
        # 제목에서 핵심 단어들만 추출
        title_words = set(self.normalize_title(title).split())
        desc_words = set(re.sub(r'[^\w\s]', '', description.lower()).split())
        
        # 길이가 3글자 이상인 의미있는 단어들만 선택
        meaningful_words = []
        for word in (title_words | desc_words):
            if len(word) >= 3 and word not in ['the', 'and', 'for', 'with', 'from', 'new', 'has']:
                meaningful_words.append(word)
        
        # 핵심 키워드와 의미있는 단어들을 합쳐서 해시 생성
        all_keywords = core_keywords | set(meaningful_words[:10])
        content = ' '.join(sorted(all_keywords))
        
        return hashlib.md5(content.encode()).hexdigest()
    
    def calculate_title_similarity(self, title1: str, title2: str) -> float:
        """제목 유사도 계산 - 개선된 버전"""
        norm1 = set(self.normalize_title(title1).split())
        norm2 = set(self.normalize_title(title2).split())
        
        if not norm1 or not norm2:
            return 0.0
        
        # Jaccard 유사도 계산
        intersection = len(norm1.intersection(norm2))
        union = len(norm1.union(norm2))
        
        jaccard_similarity = intersection / union if union > 0 else 0.0
        
        # 추가: 핵심 키워드 매칭 점수
        keywords1 = self.extract_core_keywords(title1, "")
        keywords2 = self.extract_core_keywords(title2, "")
        
        if keywords1 and keywords2:
            keyword_intersection = len(keywords1.intersection(keywords2))
            keyword_union = len(keywords1.union(keywords2))
            keyword_similarity = keyword_intersection / keyword_union if keyword_union > 0 else 0.0
        else:
            keyword_similarity = 0.0
        
        # 가중 평균 (제목 단어 70%, 핵심 키워드 30%)
        final_similarity = (jaccard_similarity * 0.7) + (keyword_similarity * 0.3)
        
        return final_similarity
    
    def check_popular_artist_duplicate(self, news1: Dict, news2: Dict) -> bool:
        """인기 아티스트에 대한 더 엄격한 중복 검사"""
        text1 = f"{news1.get('title', '')} {news1.get('description', '')}".lower()
        text2 = f"{news2.get('title', '')} {news2.get('description', '')}".lower()
        
        # 같은 인기 아티스트가 포함된 경우
        for artist in self.popular_artists:
            if artist in text1 and artist in text2:
                # 제목 유사도가 60% 이상이면 중복으로 판단
                similarity = self.calculate_title_similarity(
                    news1.get('title', ''), 
                    news2.get('title', '')
                )
                if similarity >= 0.6:  # 인기 아티스트는 더 엄격하게
                    logger.debug(f"인기 아티스트 '{artist}' 중복 발견: {similarity:.2f}")
                    return True
        
        return False
    
    def is_duplicate_advanced(self, news1: Dict, news2: Dict) -> bool:
        """강화된 중복 검사"""
        
        # 1. URL 기반 검사 (강화)
        url1 = self.normalize_url(news1.get('link', ''))
        url2 = self.normalize_url(news2.get('link', ''))
        
        if url1 and url2 and url1 == url2:
            logger.debug(f"URL 중복 발견: {url1}")
            return True
        
        # 2. 인기 아티스트에 대한 특별 검사
        if self.check_popular_artist_duplicate(news1, news2):
            return True
        
        # 3. 제목 유사도 검사 (임계값 낮춤)
        title1 = news1.get('title', '')
        title2 = news2.get('title', '')
        
        title_similarity = self.calculate_title_similarity(title1, title2)
        
        # 제목이 80% 이상 유사하면 중복 (기존 90%에서 낮춤)
        if title_similarity >= 0.8:
            logger.debug(f"제목 유사도 중복: {title_similarity:.2f}")
            return True
        
        # 4. 내용 해시 기반 검사
        hash1 = self.generate_content_hash(title1, news1.get('description', ''))
        hash2 = self.generate_content_hash(title2, news2.get('description', ''))
        
        if hash1 == hash2:
            logger.debug(f"내용 해시 중복: {hash1}")
            return True
        
        # 5. 핵심 키워드 중복도가 높은 경우
        if title_similarity >= 0.65:  # 중간 정도 유사한 경우
            keywords1 = self.extract_core_keywords(title1, news1.get('description', ''))
            keywords2 = self.extract_core_keywords(title2, news2.get('description', ''))
            
            if keywords1 and keywords2:
                keyword_overlap = len(keywords1.intersection(keywords2))
                keyword_total = len(keywords1.union(keywords2))
                
                if keyword_total > 0:
                    keyword_similarity = keyword_overlap / keyword_total
                    combined_score = (title_similarity * 0.6) + (keyword_similarity * 0.4)
                    
                    if combined_score >= 0.75:  # 종합 점수 75% 이상이면 중복
                        logger.debug(f"키워드+제목 종합 중복: {combined_score:.2f}")
                        return True
        
        # 6. 같은 소스에서 같은 시간대의 유사한 뉴스
        source1 = news1.get('source', '')
        source2 = news2.get('source', '')
        
        if (source1 == source2 and title_similarity >= 0.5):
            time1 = news1.get('published_date', '')
            time2 = news2.get('published_date', '')
            
            if time1 and time2:
                try:
                    dt1 = datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
                    dt2 = datetime.strptime(time2, '%Y-%m-%d %H:%M:%S')
                    time_diff = abs((dt1 - dt2).total_seconds())
                    
                    if time_diff <= 7200:  # 2시간 (기존 1시간에서 확장)
                        logger.debug(f"시간+소스 기반 중복")
                        return True
                        
                except ValueError:
                    pass
        
        return False
    
    def remove_duplicates_enhanced(self, news_list: List[Dict]) -> List[Dict]:
        """강화된 중복 제거"""
        logger.info(f"강화된 중복 제거 시작: {len(news_list)}개 뉴스")
        
        unique_news = []
        removed_count = 0
        url_cache = set()
        
        # 먼저 발행시간 순으로 정렬 (최신순)
        try:
            sorted_news = sorted(news_list, key=lambda x: x.get('published_date', ''), reverse=True)
        except:
            sorted_news = news_list
        
        for news in sorted_news:
            is_duplicate = False
            
            # 빠른 URL 검사
            normalized_url = self.normalize_url(news.get('link', ''))
            if normalized_url in url_cache:
                is_duplicate = True
                removed_count += 1
                logger.debug(f"URL 캐시 중복 제거: {news.get('title', '')[:50]}...")
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
                            logger.debug(f"더 나은 뉴스로 교체: {news.get('title', '')[:50]}...")
                        else:
                            logger.debug(f"중복 제거: {news.get('title', '')[:50]}...")
                        
                        break
            
            # 중복이 아니면 추가
            if not is_duplicate:
                unique_news.append(news)
        
        logger.info(f"중복 제거 완료: {len(news_list)} -> {len(unique_news)}개 (제거: {removed_count}개)")
        
        # 중복 제거 통계 출력
        if removed_count > 0:
            removal_rate = (removed_count / len(news_list)) * 100
            logger.info(f"중복 제거율: {removal_rate:.1f}%")
            
            # 중복이 많이 제거되었다면 상세 분석
            if removal_rate > 15:
                self.analyze_duplicate_patterns(news_list, unique_news)
        
        return unique_news
    
    def should_replace_news(self, existing: Dict, new: Dict) -> bool:
        """두 중복 뉴스 중 어느 것을 선택할지 결정 - 개선된 버전"""
        
        # 1. 소스 신뢰도 비교 (가중치 증가)
        source_priority = {
            'billboard.com': 10,
            'rollingstone.com': 9,
            'pitchfork.com': 8,
            'variety.com': 7,
            'musicbusinessworldwide.com': 6,
            'consequence.net': 5,
            'nme.com': 4,
            'stereogum.com': 3
        }
        
        existing_priority = source_priority.get(existing.get('source', ''), 1)
        new_priority = source_priority.get(new.get('source', ''), 1)
        
        # 소스 우선순위 차이가 2 이상이면 결정적
        if new_priority - existing_priority >= 2:
            return True
        elif existing_priority - new_priority >= 2:
            return False
        
        # 2. 제목 품질 비교 (길이와 정보량)
        existing_title_quality = len(existing.get('title', '')) + existing.get('title', '').count(' ')
        new_title_quality = len(new.get('title', '')) + new.get('title', '').count(' ')
        
        # 3. 내용 길이 비교
        existing_content_length = len(existing.get('description', ''))
        new_content_length = len(new.get('description', ''))
        
        # 4. 발행 시간 비교 (최신성)
        try:
            existing_time = datetime.strptime(existing.get('published_date', ''), '%Y-%m-%d %H:%M:%S')
            new_time = datetime.strptime(new.get('published_date', ''), '%Y-%m-%d %H:%M:%S')
            
            # 새 뉴스가 1시간 이상 최신이면 선호
            time_diff = (new_time - existing_time).total_seconds()
            if time_diff > 3600:  # 1시간
                return True
            elif time_diff < -3600:
                return False
        except ValueError:
            pass
        
        # 5. 종합 점수 계산
        existing_score = (existing_priority * 3) + (existing_title_quality * 0.1) + (existing_content_length * 0.01)
        new_score = (new_priority * 3) + (new_title_quality * 0.1) + (new_content_length * 0.01)
        
        return new_score > existing_score
    
    def analyze_duplicate_patterns(self, original_list: List[Dict], unique_list: List[Dict]):
        """중복 패턴 분석 - 개선된 버전"""
        
        # 아티스트별 중복 통계
        artist_duplicates = {}
        
        for news in original_list:
            title = news.get('title', '').lower()
            for artist in self.popular_artists:
                if artist in title:
                    artist_duplicates[artist] = artist_duplicates.get(artist, 0) + 1
        
        # 중복이 많은 아티스트들 출력
        high_duplicate_artists = [(artist, count) for artist, count in artist_duplicates.items() if count > 1]
        high_duplicate_artists.sort(key=lambda x: x[1], reverse=True)
        
        if high_duplicate_artists:
            logger.info("아티스트별 중복 뉴스:")
            for artist, count in high_duplicate_artists[:5]:
                logger.info(f"  {artist.title()}: {count}개")
        
        # 소스별 중복 통계
        source_counts = {}
        for news in original_list:
            source = news.get('source', '')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        logger.info("소스별 뉴스 수:")
        for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            logger.info(f"  {source}: {count}개")
    
    def fetch_rss_feed(self, url: str) -> List[Dict]:
        """RSS 피드에서 뉴스 수집 - 기존 코드 유지"""
        try:
            logger.info(f"RSS 피드 수집 중: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            news_items = []
            
            # 최근 7일 이내 뉴스만 수집
            cutoff_time = datetime.now() - timedelta(days=7)
            
            for entry in feed.entries[:20]:
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
                    if relevance < 0.2:
                        continue
                    
                    # 고유 ID 생성
                    news_id = hashlib.md5(link.encode()).hexdigest()[:12]
                    
                    news_item = {
                        'id': news_id,
                        'title': title,
                        'description': description,
                        'link': link,
                        'url': link,
                        'source': urlparse(url).netloc,
                        'published': entry.get('published', ''),
                        'published_date': pub_time.strftime('%Y-%m-%d %H:%M:%S') if pub_time else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'relevance_score': relevance,
                        'entities': list(self.extract_core_keywords(title, description)),
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
        
        keyword_matches = sum(1 for keyword in self.music_keywords if keyword in text)
        keyword_score = min(keyword_matches / 5, 1.0)
        
        domain_score = 0.8
        
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
    
    # 실제 뉴스 수집 테스트
    print("=== 실제 뉴스 수집 및 중복 제거 테스트 ===")
    news_items = collector.collect_all_news()
    
    print(f"최종 수집된 뉴스: {len(news_items)}개")
    
    # 상위 10개 뉴스 미리보기
    print("\n상위 10개 뉴스:")
    for i, news in enumerate(news_items[:10]):
        title = news['title'][:60] + "..." if len(news['title']) > 60 else news['title']
        print(f"{i+1}. {title} ({news['source']})")
    
    # Taylor Swift 관련 뉴스 개수 확인
    taylor_count = sum(1 for news in news_items if 'taylor swift' in news['title'].lower())
    print(f"\nTaylor Swift 관련 뉴스: {taylor_count}개")
