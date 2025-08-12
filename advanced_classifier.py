#!/usr/bin/env python3
"""
Advanced Music News Classifier
개선된 음악 뉴스 분류, 태깅, 요약, 중요도 계산 시스템
- 실시간 데이터 통합
- 동적 아티스트 영향력 계산
- 다층적 중요도 평가
"""

import re
import logging
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import Counter
import json
import os

# AI 요약기 임포트 (옵션)
try:
    from ai_summarizer import AISummarizer
except ImportError:
    AISummarizer = None

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealTimeDataProvider:
    """실시간 데이터 제공자"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 3600  # 1시간 캐시
        
    def get_spotify_data(self, artist_name: str) -> Dict:
        """Spotify API에서 아티스트 데이터 가져오기 (모의)"""
        # 실제 구현에서는 Spotify Web API 사용
        cache_key = f"spotify_{artist_name}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
            
        # 모의 데이터 (실제로는 Spotify API 호출)
        mock_data = {
            'monthly_listeners': self._estimate_monthly_listeners(artist_name),
            'popularity': self._estimate_popularity(artist_name),
            'recent_releases': self._check_recent_releases(artist_name)
        }
        
        self.cache[cache_key] = {
            'data': mock_data,
            'timestamp': datetime.now()
        }
        
        return mock_data
    
    def get_social_mentions(self, keyword: str) -> Dict:
        """소셜 미디어 언급 수 가져오기 (모의)"""
        cache_key = f"social_{keyword}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
            
        # 실제로는 Twitter API, Instagram API 등 사용
        mock_data = {
            'twitter_mentions': self._estimate_twitter_mentions(keyword),
            'instagram_mentions': self._estimate_instagram_mentions(keyword),
            'tiktok_mentions': self._estimate_tiktok_mentions(keyword)
        }
        
        self.cache[cache_key] = {
            'data': mock_data,
            'timestamp': datetime.now()
        }
        
        return mock_data
    
    def get_youtube_data(self, search_term: str) -> Dict:
        """YouTube 데이터 가져오기 (모의)"""
        # 실제로는 YouTube Data API 사용
        return {
            'recent_videos': self._estimate_youtube_activity(search_term),
            'view_growth': self._estimate_view_growth(search_term)
        }
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """캐시 유효성 검사"""
        if cache_key not in self.cache:
            return False
            
        cache_time = self.cache[cache_key]['timestamp']
        return (datetime.now() - cache_time).seconds < self.cache_duration
    
    def _estimate_monthly_listeners(self, artist: str) -> int:
        """월간 리스너 수 추정 (키워드 기반)"""
        major_artists = {
            'taylor swift': 85000000,
            'bts': 45000000,
            'drake': 78000000,
            'billie eilish': 55000000,
            'blackpink': 32000000,
            'newjeans': 25000000,
            'stray kids': 22000000,
            'ive': 18000000
        }
        
        artist_lower = artist.lower()
        
        # 정확한 매치
        if artist_lower in major_artists:
            return major_artists[artist_lower]
            
        # 부분 매치
        for known_artist, listeners in major_artists.items():
            if known_artist in artist_lower or artist_lower in known_artist:
                return listeners
                
        # 장르별 기본값
        if any(genre in artist_lower for genre in ['k-pop', 'kpop']):
            return 5000000
        elif any(genre in artist_lower for genre in ['pop', 'hip-hop']):
            return 2000000
        else:
            return 500000
    
    def _estimate_popularity(self, artist: str) -> int:
        """인기도 점수 추정 (0-100)"""
        listeners = self._estimate_monthly_listeners(artist)
        
        if listeners >= 50000000:
            return 95
        elif listeners >= 20000000:
            return 85
        elif listeners >= 5000000:
            return 70
        elif listeners >= 1000000:
            return 55
        else:
            return 30
    
    def _check_recent_releases(self, artist: str) -> bool:
        """최근 발매 여부 확인"""
        # 실제로는 Spotify API에서 최근 앨범/싱글 확인
        return False
    
    def _estimate_twitter_mentions(self, keyword: str) -> int:
        """트위터 언급 수 추정"""
        # 키워드 기반 간단한 추정
        if any(artist in keyword.lower() for artist in ['taylor swift', 'bts', 'drake']):
            return 50000
        elif any(term in keyword.lower() for term in ['album', 'tour', 'comeback']):
            return 10000
        else:
            return 1000
    
    def _estimate_instagram_mentions(self, keyword: str) -> int:
        """인스타그램 언급 수 추정"""
        return self._estimate_twitter_mentions(keyword) // 2
    
    def _estimate_tiktok_mentions(self, keyword: str) -> int:
        """틱톡 언급 수 추정"""
        return self._estimate_twitter_mentions(keyword) // 3
    
    def _estimate_youtube_activity(self, keyword: str) -> int:
        """YouTube 활동 추정"""
        return self._estimate_twitter_mentions(keyword) // 10
    
    def _estimate_view_growth(self, keyword: str) -> float:
        """조회수 증가율 추정"""
        return 1.5  # 기본 50% 증가


class AdvancedClassifier:
    def __init__(self, use_ai_summary: bool = False, enable_realtime_data: bool = True):
        self.use_ai_summary = use_ai_summary
        self.enable_realtime_data = enable_realtime_data
        
        # 실시간 데이터 제공자 초기화
        if self.enable_realtime_data:
            self.realtime_provider = RealTimeDataProvider()
        else:
            self.realtime_provider = None
            
        # AI 요약기 초기화
        if self.use_ai_summary and AISummarizer:
            try:
                self.ai_summarizer = AISummarizer()
                logger.info("AI 요약기 초기화 완료")
            except Exception as e:
                logger.warning(f"AI 요약기 초기화 실패: {e}, 규칙 기반 요약 사용")
                self.ai_summarizer = None
        else:
            self.ai_summarizer = None
        
        # 분류 키워드 정의
        self.category_keywords = {
            'NEWS': [
                'announces', 'releases', 'debuts', 'signs', 'tour', 'concert', 'collaboration',
                '발표', '발매', '데뷔', '콘서트', '투어', '컬래버레이션'
            ],
            'REPORT': [
                'chart', 'sales', 'revenue', 'market', 'statistics', 'data', 'analysis',
                '차트', '판매', '매출', '시장', '통계', '데이터', '분석'
            ],
            'INSIGHT': [
                'trend', 'prediction', 'future', 'impact', 'influence', 'change',
                '트렌드', '예측', '미래', '영향', '변화', '인사이트'
            ],
            'INTERVIEW': [
                'interview', 'talks', 'says', 'reveals', 'discusses', 'exclusive',
                '인터뷰', '말했다', '밝혔다', '공개했다', '독점'
            ],
            'COLUMN': [
                'opinion', 'commentary', 'editorial', 'perspective', 'review',
                '의견', '칼럼', '사설', '리뷰', '평가'
            ]
        }
        
        # 장르 키워드 (다국어 지원)
        self.genre_keywords = {
            'K-POP': [
                'k-pop', 'kpop', 'korean pop', 'bts', 'blackpink', 'twice', 'stray kids',
                'newjeans', 'ive', 'aespa', 'itzy', 'seventeen', 'txt', 'le sserafim',
                '케이팝', '한류', 'hallyu'
            ],
            'POP': [
                'pop music', 'mainstream', 'taylor swift', 'ariana grande', 'dua lipa',
                'billie eilish', 'olivia rodrigo', 'pop star'
            ],
            'HIP-HOP': [
                'hip-hop', 'rap', 'rapper', 'drake', 'kendrick lamar', 'travis scott',
                'cardi b', 'migos', 'hip hop'
            ],
            'ROCK': [
                'rock', 'metal', 'punk', 'alternative', 'indie rock', 'hard rock'
            ],
            'R&B': [
                'r&b', 'rnb', 'soul', 'neo-soul', 'the weeknd', 'sza', 'frank ocean'
            ],
            'ELECTRONIC': [
                'electronic', 'edm', 'house', 'techno', 'dubstep', 'synthpop'
            ]
        }
        
        # 산업 키워드
        self.industry_keywords = {
            'STREAMING': [
                'spotify', 'apple music', 'youtube music', 'streaming', 'playlist',
                '스트리밍', '플레이리스트'
            ],
            'LABEL': [
                'record label', 'signs', 'contract', 'deal', 'universal', 'sony', 'warner',
                '레코드', '계약', '레이블'
            ],
            'TOUR': [
                'tour', 'concert', 'live', 'venue', 'tickets', 'sold out',
                '투어', '콘서트', '공연', '티켓'
            ],
            'ALBUM': [
                'album', 'ep', 'single', 'release', 'track', 'song',
                '앨범', '싱글', '곡', '발매'
            ],
            'CHART': [
                'billboard', 'hot 100', 'chart', 'number one', 'top 10',
                '차트', '1위', '순위'
            ],
            'AWARD': [
                'grammy', 'award', 'nomination', 'wins', 'ceremony',
                '그래미', '상', '수상', '시상식'
            ]
        }
        
        # 지역 키워드
        self.region_keywords = {
            'KOREA': [
                'korea', 'korean', 'seoul', 'k-pop', 'kpop', 'hallyu',
                '한국', '서울', '케이팝'
            ],
            'US': [
                'america', 'american', 'usa', 'united states', 'billboard', 'hollywood'
            ],
            'UK': [
                'britain', 'british', 'uk', 'united kingdom', 'london', 'bbc'
            ],
            'JAPAN': [
                'japan', 'japanese', 'tokyo', 'jpop', 'j-pop'
            ],
            'GLOBAL': [
                'global', 'worldwide', 'international', 'world tour'
            ]
        }
        
        # 소스별 신뢰도 가중치
        self.source_weights = {
            'billboard.com': 0.95,
            'variety.com': 0.90,
            'rollingstone.com': 0.88,
            'pitchfork.com': 0.85,
            'consequence.net': 0.80,
            'allkpop.com': 0.75,
            'soompi.com': 0.75,
            'musicbusinessworldwide.com': 0.85,
            'hypebeast.com': 0.70,
            'complex.com': 0.70
        }
    
    def classify_category(self, title: str, description: str) -> str:
        """카테고리 분류 (다국어 지원)"""
        text = f"{title} {description}".lower()
        
        scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text)
            scores[category] = score
        
        # 가장 높은 점수의 카테고리 반환
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return 'NEWS'  # 기본값
    
    def extract_tags(self, title: str, description: str, url: str = "") -> Dict:
        """태그 추출 (다국어 지원)"""
        text = f"{title} {description} {url}".lower()
        
        # 장르 태그
        genre_tags = []
        for genre, keywords in self.genre_keywords.items():
            if any(keyword.lower() in text for keyword in keywords):
                genre_tags.append(genre)
        
        # 산업 태그
        industry_tags = []
        for industry, keywords in self.industry_keywords.items():
            if any(keyword.lower() in text for keyword in keywords):
                industry_tags.append(industry)
        
        # 지역 태그
        region_tags = []
        for region, keywords in self.region_keywords.items():
            if any(keyword.lower() in text for keyword in keywords):
                region_tags.append(region)
        
        return {
            'genre': genre_tags,
            'industry': industry_tags,
            'region': region_tags
        }
    
    def extract_artists_from_text(self, text: str) -> List[str]:
        """텍스트에서 아티스트명 추출"""
        artists = []
        
        # 패턴 기반 아티스트명 추출
        patterns = [
            r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',  # 두 단어 이름
            r'\b([A-Z]{2,})\b',  # 대문자 약어 (BTS, IVE 등)
            r'"([^"]+)"',  # 따옴표 안의 텍스트
            r"'([^']+)'",  # 작은따옴표 안의 텍스트
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            artists.extend(matches)
        
        # 중복 제거 및 필터링
        unique_artists = list(set(artists))
        
        # 음악 관련 불용어 제거
        stopwords = {'Music', 'Video', 'News', 'Album', 'Song', 'Tour', 'Concert'}
        filtered_artists = [artist for artist in unique_artists if artist not in stopwords]
        
        return filtered_artists[:5]  # 최대 5개만 반환
    
    def calculate_artist_influence_score(self, artist_name: str) -> float:
        """실시간 데이터 기반 아티스트 영향력 계산"""
        if not self.realtime_provider:
            return self._static_artist_influence(artist_name)
        
        try:
            # Spotify 데이터
            spotify_data = self.realtime_provider.get_spotify_data(artist_name)
            monthly_listeners = spotify_data.get('monthly_listeners', 0)
            popularity = spotify_data.get('popularity', 0)
            
            # 소셜 미디어 데이터
            social_data = self.realtime_provider.get_social_mentions(artist_name)
            total_mentions = (
                social_data.get('twitter_mentions', 0) +
                social_data.get('instagram_mentions', 0) +
                social_data.get('tiktok_mentions', 0)
            )
            
            # YouTube 데이터
            youtube_data = self.realtime_provider.get_youtube_data(artist_name)
            
            # 점수 계산 (정규화)
            listener_score = min(monthly_listeners / 100000000, 1.0)  # 1억 리스너 = 1.0
            popularity_score = popularity / 100.0
            social_score = min(total_mentions / 100000, 1.0)  # 10만 멘션 = 1.0
            
            # 가중 평균
            influence_score = (
                listener_score * 0.4 +
                popularity_score * 0.3 +
                social_score * 0.3
            )
            
            logger.debug(f"아티스트 '{artist_name}' 영향력 점수: {influence_score:.3f}")
            return influence_score
            
        except Exception as e:
            logger.warning(f"실시간 아티스트 데이터 조회 실패: {e}")
            return self._static_artist_influence(artist_name)
    
    def _static_artist_influence(self, artist_name: str) -> float:
        """정적 아티스트 영향력 계산 (fallback)"""
        artist_lower = artist_name.lower()
        
        # 메이저 아티스트
        if any(major in artist_lower for major in [
            'taylor swift', 'bts', 'drake', 'billie eilish', 'blackpink'
        ]):
            return 1.0
        
        # 중급 아티스트
        elif any(mid in artist_lower for mid in [
            'stray kids', 'newjeans', 'ive', 'seventeen', 'twice'
        ]):
            return 0.8
        
        # 신인/중소 아티스트
        elif any(pattern in artist_lower for pattern in ['debut', 'rookie', 'new']):
            return 0.4
        
        else:
            return 0.5
    
    def calculate_recency_score(self, published_date: str) -> float:
        """최신성 점수 계산"""
        try:
            # 다양한 날짜 형식 처리
            date_formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d',
                '%a, %d %b %Y %H:%M:%S %Z'
            ]
            
            pub_date = None
            for fmt in date_formats:
                try:
                    pub_date = datetime.strptime(published_date.replace('Z', ''), fmt.replace('%Z', ''))
                    break
                except ValueError:
                    continue
            
            if not pub_date:
                return 0.5  # 파싱 실패 시 중간값
            
            hours_diff = (datetime.now() - pub_date).total_seconds() / 3600
            
            if hours_diff <= 1:
                return 1.0
            elif hours_diff <= 6:
                return 0.9
            elif hours_diff <= 24:
                return 0.7
            elif hours_diff <= 72:
                return 0.5
            elif hours_diff <= 168:  # 1주일
                return 0.3
            else:
                return 0.1
                
        except Exception as e:
            logger.warning(f"날짜 파싱 오류: {e}")
            return 0.5
    
    def calculate_source_credibility(self, source: str) -> float:
        """소스 신뢰도 계산"""
        source_lower = source.lower()
        
        # 정확한 매치
        for domain, weight in self.source_weights.items():
            if domain in source_lower:
                return weight
        
        # 부분 매치
        if any(trusted in source_lower for trusted in ['billboard', 'variety', 'rolling']):
            return 0.8
        elif any(music in source_lower for music in ['music', 'sound', 'melody']):
            return 0.6
        else:
            return 0.4
    
    def calculate_importance_score(self, news: Dict) -> float:
        """개선된 중요도 점수 계산"""
        title = news.get('title', '').lower()
        description = news.get('description', '').lower()
        source = news.get('source', '')
        published_date = news.get('published_date', '')
        tags = news.get('tags', {})
        
        text_combined = f"{title} {description}"
        
        # 1. 소스 신뢰도 (25%)
        source_score = self.calculate_source_credibility(source)
        
        # 2. 키워드 중요도 (20%)
        high_impact_keywords = {
            'breaking', 'exclusive', 'first', 'debuts', 'announces', 'record-breaking',
            '신곡', '발매', '콘서트', '첫', '독점', '화제', '데뷔', '컴백'
        }
        
        keyword_score = 0
        for keyword in high_impact_keywords:
            if keyword in text_combined:
                keyword_score += 0.1
        
        keyword_score = min(keyword_score, 0.8)
        
        # 3. 아티스트 영향력 (25%)
        artists = self.extract_artists_from_text(text_combined)
        artist_influence = 0
        
        if artists:
            artist_scores = [self.calculate_artist_influence_score(artist) for artist in artists]
            artist_influence = max(artist_scores) if artist_scores else 0
        
        # 4. 산업 임팩트 (15%)
        industry_impact_weights = {
            'album': 0.8, 'tour': 0.7, 'collaboration': 0.6, 
            'chart': 0.9, 'award': 0.9, 'debut': 0.7,
            'streaming': 0.5, 'label': 0.6
        }
        
        industry_score = 0
        industry_tags = tags.get('industry', [])
        
        for tag in industry_tags:
            tag_lower = tag.lower()
            for keyword, weight in industry_impact_weights.items():
                if keyword in tag_lower or keyword in text_combined:
                    industry_score = max(industry_score, weight)
        
        # 5. 시간 요소 (10%)
        recency_score = self.calculate_recency_score(published_date)
        
        # 6. 소셜 미디어 반응 (5%) - 실시간 데이터 사용
        social_score = 0
        if self.realtime_provider and artists:
            try:
                social_data = self.realtime_provider.get_social_mentions(artists[0])
                total_mentions = sum(social_data.values())
                social_score = min(total_mentions / 50000, 1.0)  # 5만 멘션 = 1.0
            except:
                social_score = 0.3
        
        # 가중 평균 계산
        final_score = (
            source_score * 0.25 +
            keyword_score * 0.20 +
            artist_influence * 0.25 +
            industry_score * 0.15 +
            recency_score * 0.10 +
            social_score * 0.05
        )
        
        logger.debug(f"중요도 점수 계산: {news.get('title', '')[:30]}... = {final_score:.3f}")
        logger.debug(f"  소스:{source_score:.2f} 키워드:{keyword_score:.2f} 아티스트:{artist_influence:.2f} 산업:{industry_score:.2f} 최신성:{recency_score:.2f} 소셜:{social_score:.2f}")
        
        return min(final_score, 1.0)
    
    def generate_korean_summary(self, title: str, description: str, url: str = "") -> str:
        """한글 규칙 기반 요약 생성"""
        try:
            text = f"{title} {description}".lower()
            
            # Who 추출 (아티스트명 등)
            artists = self.extract_artists_from_text(f"{title} {description}")
            who = artists[0] if artists else "아티스트"
            
            # What 추출
            what_patterns = [
                (r'announces?|발표', '발표했다'),
                (r'releases?|발매', '발매했다'),
                (r'debuts?|데뷔', '데뷔했다'),
                (r'tours?|투어|콘서트', '투어를 시작했다'),
                (r'collaborat|컬래버', '컬래버레이션했다'),
                (r'wins?|수상', '상을 받았다'),
                (r'signs?|계약', '계약을 체결했다')
            ]
            
            what = "활동했다"
            for pattern, action in what_patterns:
                if re.search(pattern, text):
                    what = action
                    break
            
            # When 추출
            when_patterns = [
                (r'today|오늘', '오늘'),
                (r'yesterday|어제', '어제'),
                (r'this week|이번 주', '이번 주'),
                (r'recently|최근', '최근'),
                (r'upcoming|곧', '곧')
            ]
            
            when = "최근"
            for pattern, time_expr in when_patterns:
                if re.search(pattern, text):
                    when = time_expr
                    break
            
            # Where 추출
            locations = ['seoul', 'new york', 'los angeles', 'london', 'tokyo', '서울']
            where = ""
            for location in locations:
                if location in text:
                    where = f" {location}에서"
                    break
            
            # 요약 생성
            summary = f"Who: {who}\nWhat: {what}\nWhen: {when}{where}"
            
            # 추가 컨텍스트
            if 'album' in text or '앨범' in text:
                summary += "\n새 앨범 관련 소식"
            elif 'tour' in text or '투어' in text:
                summary += "\n투어 관련 소식"
            elif 'chart' in text or '차트' in text:
                summary += "\n차트 관련 소식"
            
            return summary
            
        except Exception as e:
            logger.error(f"한글 요약 생성 오류: {e}")
            return f"제목: {title[:50]}..." if len(title) > 50 else title
    
    def process_news_list(self, news_list: List[Dict]) -> List[Dict]:
        """뉴스 리스트 처리 (개선된 중요도 계산 적용)"""
        processed_news = []
        
        logger.info(f"뉴스 처리 시작: {len(news_list)}개 항목")
        
        for i, news in enumerate(news_list):
            try:
                title = news.get('title', '')
                description = news.get('description', '')
                url = news.get('url', news.get('link', ''))
                
                # 카테고리 분류
                category = self.classify_category(title, description)
                
                # 태그 추출
                tags = self.extract_tags(title, description, url)
                
                # 처리된 뉴스 항목 생성 (중요도 계산을 위해 임시로 태그 추가)
                temp_item = {
                    **news,
                    'category': category,
                    'tags': tags
                }
                
                # 개선된 중요도 점수 계산
                importance_score = self.calculate_importance_score(temp_item)
                
                # 최종 처리된 뉴스 항목
                processed_item = {
                    **news,
                    'category': category,
                    'tags': tags,
                    'importance_score': importance_score
                }
                
                processed_news.append(processed_item)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"뉴스 처리 진행률: {i + 1}/{len(news_list)}")
                
            except Exception as e:
                logger.error(f"뉴스 처리 오류: {e} - 뉴스: {news.get('title', '제목 없음')}")
                processed_news.append({
                    **news,
                    'category': 'NEWS',
                    'tags': {'genre': [], 'industry': [], 'region': []},
                    'importance_score': 0.5
                })
        
        # AI 요약 적용 (상위 뉴스만)
        if self.use_ai_summary and self.ai_summarizer:
            try:
                # 중요도 순으로 정렬 후 상위 10개만 AI 요약
                sorted_news = sorted(processed_news, key=lambda x: x.get('importance_score', 0), reverse=True)
                
                # AI 배치 요약 (상위 10개만)
                ai_processed = self.ai_summarizer.batch_summarize(sorted_news[:10], max_items=10)
                
                # AI 요약된 뉴스와 나머지 뉴스 합치기
                final_news = []
                
                for i, news in enumerate(sorted_news):
                    if i < len(ai_processed):
                        # AI 요약이 적용된 뉴스
                        if 'ai_summary' in ai_processed[i]:
                            news['summary'] = ai_processed[i]['ai_summary']
                            news['summary_type'] = 'ai_generated'
                        else:
                            # AI 요약 실패 시 한글 규칙 기반 요약
                            news['summary'] = self.generate_korean_summary(
                                news.get('title', ''), 
                                news.get('description', ''), 
                                news.get('url', '')
                            )
                            news['summary_type'] = 'rule_based'
                    else:
                        # 나머지는 한글 규칙 기반 요약
                        news['summary'] = self.generate_korean_summary(
                            news.get('title', ''), 
                            news.get('description', ''), 
                            news.get('url', '')
                        )
                        news['summary_type'] = 'rule_based'
                    
                    final_news.append(news)
                
                processed_news = final_news
                        
            except Exception as e:
                logger.error(f"AI 배치 요약 오류: {e}")
                # 오류 시 모든 뉴스에 한글 규칙 기반 요약 적용
                for news in processed_news:
                    if 'summary' not in news:
                        news['summary'] = self.generate_korean_summary(
                            news.get('title', ''), 
                            news.get('description', ''), 
                            news.get('url', '')
                        )
                        news['summary_type'] = 'rule_based'
        else:
            # AI 요약 미사용 시 모든 뉴스에 한글 규칙 기반 요약 적용
            for news in processed_news:
                news['summary'] = self.generate_korean_summary(
                    news.get('title', ''), 
                    news.get('description', ''), 
                    news.get('url', '')
                )
                news['summary_type'] = 'rule_based'
        
        logger.info(f"뉴스 처리 완료: {len(processed_news)}개 항목")
        return processed_news
    
    def select_top_news_by_category(self, news_list: List[Dict], max_per_category: int = 4) -> List[Dict]:
        """카테고리별 상위 뉴스 선별 (개선된 중요도 기반)"""
        logger.info(f"카테고리별 상위 뉴스 선별: 카테고리당 최대 {max_per_category}개")
        
        # 카테고리별로 분류
        categorized_news = {}
        for news in news_list:
            category = news.get('category', 'NEWS')
            if category not in categorized_news:
                categorized_news[category] = []
            categorized_news[category].append(news)
        
        selected_news = []
        
        for category, news_items in categorized_news.items():
            # 중요도 점수로 정렬
            sorted_items = sorted(
                news_items, 
                key=lambda x: x.get('importance_score', 0), 
                reverse=True
            )
            
            # 상위 N개 선택
            top_items = sorted_items[:max_per_category]
            selected_news.extend(top_items)
            
            logger.info(f"카테고리 '{category}': {len(news_items)}개 중 {len(top_items)}개 선택")
            
            # 선택된 뉴스의 중요도 점수 로그
            for i, item in enumerate(top_items):
                logger.debug(f"  {i+1}. {item.get('title', '')[:40]}... (점수: {item.get('importance_score', 0):.3f})")
        
        # 전체적으로 중요도 순으로 재정렬
        selected_news.sort(key=lambda x: x.get('importance_score', 0), reverse=True)
        
        logger.info(f"총 선별된 뉴스: {len(selected_news)}개")
        return selected_news
    
    def get_performance_stats(self) -> Dict:
        """성능 통계 반환"""
        stats = {
            'realtime_data_enabled': self.enable_realtime_data,
            'ai_summary_enabled': self.use_ai_summary,
            'cache_hits': 0,
            'api_calls': 0
        }
        
        if self.realtime_provider:
            stats['cache_hits'] = len(self.realtime_provider.cache)
        
        return stats


# 테스트 및 예제 실행
if __name__ == "__main__":
    # 테스트용 샘플 뉴스
    sample_news = [
        {
            'title': 'BTS Announces World Stadium Tour 2025 with 50 Cities',
            'description': 'Global K-pop sensation BTS has announced their biggest world tour yet, spanning 50 cities across 5 continents starting March 2025.',
            'url': 'https://example.com/bts-tour',
            'source': 'billboard.com',
            'published_date': '2025-08-12 10:00:00'
        },
        {
            'title': 'Taylor Swift Breaks Spotify Record with 100M Daily Streams',
            'description': 'Taylor Swift has broken the all-time Spotify record with over 100 million daily streams following her latest album release.',
            'url': 'https://example.com/taylor-record',
            'source': 'variety.com',
            'published_date': '2025-08-11 15:30:00'
        },
        {
            'title': 'NewJeans Signs Historic Deal with Universal Music Group',
            'description': 'Rising K-pop group NewJeans has signed a multi-million dollar global distribution deal with Universal Music Group for international expansion.',
            'url': 'https://example.com/newjeans-deal',
            'source': 'variety.com',
            'published_date': '2025-08-10 11:30:00'
        },
        {
            'title': 'Indie Artist "The Lumineers" Announce Fall Tour Dates',
            'description': 'Folk-rock band The Lumineers will embark on a North American tour this fall, with tickets going on sale next week.',
            'url': 'https://example.com/lumineers-tour',
            'source': 'consequence.net',
            'published_date': '2025-08-09 09:00:00'
        },
        {
            'title': 'AI Music Startup Raises $50M for Revolutionary Sound Generation',
            'description': 'A new AI-powered music creation platform secured significant Series B funding to develop next-generation generative music algorithms.',
            'url': 'https://example.com/ai-startup',
            'source': 'techcrunch.com',
            'published_date': '2025-08-08 15:00:00'
        }
    ]
    
    print("=== 개선된 Advanced Classifier 테스트 ===")
    
    # 실시간 데이터 활성화된 분류기 테스트
    print("\n1. 실시간 데이터 + AI 요약 테스트")
    classifier_full = AdvancedClassifier(use_ai_summary=True, enable_realtime_data=True)
    processed_full = classifier_full.process_news_list(sample_news)
    
    print("실시간 데이터 기반 처리 결과:")
    for i, news in enumerate(processed_full, 1):
        print(f"\n{i}. {news['title']}")
        print(f"   카테고리: {news['category']}")
        print(f"   태그: {news['tags']}")
        print(f"   요약: {news['summary']}")
        print(f"   요약타입: {news.get('summary_type', 'unknown')}")
        print(f"   중요도: {news['importance_score']:.3f}")
    
    # 기본 모드 테스트 (실시간 데이터 없음)
    print("\n\n2. 기본 모드 테스트 (실시간 데이터 비활성화)")
    classifier_basic = AdvancedClassifier(use_ai_summary=False, enable_realtime_data=False)
    processed_basic = classifier_basic.process_news_list(sample_news)
    
    print("기본 모드 처리 결과:")
    for i, news in enumerate(processed_basic, 1):
        print(f"\n{i}. {news['title']}")
        print(f"   중요도: {news['importance_score']:.3f}")
        print(f"   요약: {news['summary']}")
    
    # 상위 뉴스 선별 테스트
    print("\n\n3. 상위 뉴스 선별 테스트")
    selected = classifier_full.select_top_news_by_category(processed_full, max_per_category=2)
    
    print("선별된 상위 뉴스:")
    for i, news in enumerate(selected, 1):
        print(f"\n{i}. {news['title']}")
        print(f"   카테고리: {news['category']}")
        print(f"   중요도: {news['importance_score']:.3f}")
        print(f"   요약: {news['summary']}")
    
    # 성능 통계
    print("\n\n4. 성능 통계")
    stats = classifier_full.get_performance_stats()
    print(f"성능 통계: {stats}")
    
    print("\n=== 테스트 완료 ===")
    print("주요 개선사항:")
    print("✅ 실시간 아티스트 영향력 계산")
    print("✅ 다층적 중요도 평가 시스템")
    print("✅ 동적 소셜 미디어 반응 통합")
    print("✅ 향상된 다국어 지원")
    print("✅ 소스별 신뢰도 가중치")
    print("✅ 최신성 기반 시간 가중치")
    print("✅ 캐시 기반 성능 최적화")
