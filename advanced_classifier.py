#!/usr/bin/env python3
"""
Fixed Advanced Music News Classifier
문제점들이 해결된 음악 뉴스 분류 시스템
"""

import re
import logging
from datetime import datetime
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedClassifier:
    def __init__(self, use_ai_summary: bool = False, use_claude_summary: bool = False):
        """분류기 초기화"""
        self.use_ai_summary = use_ai_summary
        self.use_claude_summary = use_claude_summary
        self.ai_summarizer = None
        self.claude_summarizer = None
        
        # Claude 요약기 초기화
        if self.use_claude_summary:
            try:
                from anthropic_summarizer import AnthropicSummarizer
                self.claude_summarizer = AnthropicSummarizer()
                logger.info("Claude 요약기 초기화 완료")
            except Exception as e:
                logger.warning(f"Claude 요약기 초기화 실패: {e}")
                self.claude_summarizer = None
        
        # OpenAI 요약기 초기화
        elif self.use_ai_summary:
            try:
                from ai_summarizer import AISummarizer
                self.ai_summarizer = AISummarizer()
                logger.info("OpenAI 요약기 초기화 완료")
            except Exception as e:
                logger.warning(f"OpenAI 요약기 초기화 실패: {e}")
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
        
        # 수정된 장르 키워드 (더 정확한 분류)
        self.genre_keywords = {
            'K-POP': [
                'k-pop', 'kpop', 'korean pop', 'bts', 'blackpink', 'twice', 'stray kids',
                'newjeans', 'ive', 'aespa', 'itzy', 'seventeen', 'txt', 'le sserafim',
                'nmixx', 'gidle', 'red velvet', 'enhypen', 'nct', 'riize',
                '케이팝', '한류', 'hallyu'
            ],
            'POP': [
                'taylor swift', 'ariana grande', 'dua lipa', 'billie eilish', 'olivia rodrigo',
                'sabrina carpenter', 'chappell roan', 'pop music', 'mainstream pop'
            ],
            'HIP-HOP': [
                'drake', 'kendrick lamar', 'travis scott', 'kid cudi', 'cardi b', 'migos',
                'doechii', 'remble', 'hip-hop', 'rap', 'rapper'
            ],
            'ROCK': [
                'metallica', 'my chemical romance', 'mother love bone', 'mayday parade',
                'rock', 'metal', 'punk', 'alternative', 'indie rock'
            ],
            'R&B': ['r&b', 'rnb', 'soul', 'neo-soul', 'the weeknd', 'sza', 'frank ocean'],
            'ELECTRONIC': ['kaytranada', 'electronic', 'edm', 'house', 'techno', 'dubstep']
        }
        
        # 산업 키워드
        self.industry_keywords = {
            'STREAMING': ['spotify', 'apple music', 'youtube music', 'streaming', 'playlist'],
            'LABEL': ['record label', 'signs', 'contract', 'deal', 'universal', 'sony', 'warner'],
            'TOUR': ['tour', 'concert', 'live', 'venue', 'tickets', 'sold out'],
            'ALBUM': ['album', 'ep', 'single', 'release', 'track', 'song'],
            'CHART': ['billboard', 'hot 100', 'chart', 'number one', 'top 10'],
            'AWARD': ['grammy', 'award', 'nomination', 'wins', 'ceremony']
        }
        
        # 지역 키워드
        self.region_keywords = {
            'KOREA': ['korea', 'korean', 'seoul', 'k-pop', 'kpop', 'hallyu'],
            'US': ['america', 'american', 'usa', 'united states', 'billboard', 'hollywood'],
            'UK': ['britain', 'british', 'uk', 'united kingdom', 'london'],
            'JAPAN': ['japan', 'japanese', 'tokyo', 'jpop', 'j-pop'],
            'GLOBAL': ['global', 'worldwide', 'international', 'world tour']
        }
    
    def classify_category(self, title: str, description: str) -> str:
        """카테고리 분류"""
        text = f"{title} {description}".lower()
        
        scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text)
            scores[category] = score
        
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return 'NEWS'
    
    def extract_tags(self, title: str, description: str, url: str = "") -> Dict:
        """수정된 태그 추출 (더 정확한 장르 분류)"""
        text = f"{title} {description}".lower()
        
        # 장르 태그 (우선순위 적용)
        genre_tags = []
        
        # 특정 아티스트 기반 장르 분류 (가장 우선)
        artist_genre_map = {
            'taylor swift': 'POP',
            'ariana grande': 'POP', 
            'billie eilish': 'POP',
            'drake': 'HIP-HOP',
            'travis scott': 'HIP-HOP',
            'metallica': 'ROCK',
            'my chemical romance': 'ROCK',
            'bts': 'K-POP',
            'blackpink': 'K-POP',
            'newjeans': 'K-POP',
            'kaytranada': 'ELECTRONIC'
        }
        
        # 아티스트 기반 우선 분류
        for artist, genre in artist_genre_map.items():
            if artist in text:
                genre_tags.append(genre)
                break
        
        # 아티스트 매치가 없으면 키워드 기반 분류
        if not genre_tags:
            for genre, keywords in self.genre_keywords.items():
                if genre == 'K-POP':
                    if any(kw in text for kw in ['k-pop', 'kpop', 'korean pop', 'hallyu', '케이팝']):
                        genre_tags.append(genre)
                else:
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
            if region == 'KOREA' and 'K-POP' in genre_tags:
                region_tags.append(region)
            elif any(keyword.lower() in text for keyword in keywords):
                region_tags.append(region)
        
        return {
            'genre': list(set(genre_tags))[:2],
            'industry': list(set(industry_tags))[:3],
            'region': list(set(region_tags))[:2]
        }
    
    def extract_artists_from_text(self, text: str) -> List[str]:
        """개선된 아티스트명 추출"""
        artists = []
        
        # 알려진 아티스트명 직접 매칭
        known_artists = [
            'Taylor Swift', 'Ariana Grande', 'Billie Eilish', 'Dua Lipa', 'Olivia Rodrigo',
            'Drake', 'Travis Scott', 'Kid Cudi', 'Kendrick Lamar',
            'BTS', 'BLACKPINK', 'TWICE', 'Stray Kids', 'NewJeans', 'IVE', 'aespa',
            'Metallica', 'My Chemical Romance', 'Mayday Parade', 'Mother Love Bone',
            'Kaytranada', 'Ethel Cain', 'Wet Leg', 'Chappell Roan', 'Doechii'
        ]
        
        text_lower = text.lower()
        for artist in known_artists:
            if artist.lower() in text_lower:
                artists.append(artist)
        
        # 패턴 기반 추출 (보조)
        if not artists:
            patterns = [
                r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',
                r'\b([A-Z]{2,})\b',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    # 필터링
                    exclude_words = ['Music', 'Video', 'News', 'Album', 'Song', 'Tour', 'Concert', 
                                   'Live From', 'Very Imminent', 'Is Ready', 'New Album']
                    if (len(match) > 2 and 
                        match not in exclude_words and
                        not match.startswith('The ') and
                        not any(word in match.lower() for word in ['new', 'first', 'live', 'from'])):
                        artists.append(match)
        
        return artists[:3]
    
    def generate_korean_summary(self, title: str, description: str, url: str = "") -> str:
        """개선된 한국어 요약 생성"""
        try:
            # 아티스트명 정확히 추출
            artists = self.extract_artists_from_text(f"{title} {description}")
            who = artists[0] if artists else "음악 아티스트"
            
            # 제목과 내용 분석
            text = f"{title} {description}".lower()
            
            # 구체적인 행동 패턴 분석
            if 'podcast' in text and 'appear' in text:
                return f"{who}가 최근 팟캐스트 출연을 발표했습니다."
            elif 'countdown' in text or 'teas' in text:
                return f"{who}가 새로운 프로젝트를 예고하며 팬들의 관심을 모으고 있습니다."
            elif 'tour' in text and ('announce' in text or 'expand' in text):
                return f"{who}가 새로운 투어 계획을 발표했습니다."
            elif 'album' in text and 'announce' in text:
                album_title = self.extract_album_title_improved(title, description)
                if album_title:
                    return f"{who}가 새 앨범 '{album_title}'을 발표했습니다."
                else:
                    return f"{who}가 새 앨범 발매 소식을 전했습니다."
            elif 'chart' in text or '#1' in text or 'number' in text:
                return f"{who}가 음악 차트에서 좋은 성과를 거두었습니다."
            elif 'cover' in text and 'live' in text:
                return f"{who}가 라이브 공연에서 커버곡을 선보였습니다."
            elif 'lawsuit' in text or 'sue' in text:
                return f"음악 업계에서 법적 분쟁 관련 소식이 전해졌습니다."
            elif 'funeral' in text or 'death' in text:
                return f"음악계 인사의 부고 관련 소식이 전해졌습니다."
            elif 'reissue' in text or 'vinyl' in text:
                return f"{who}의 음반이 재발매될 예정입니다."
            else:
                return f"{who}가 최근 음악 활동 관련 소식을 전했습니다."
            
        except Exception as e:
            logger.error(f"한국어 요약 생성 오류: {e}")
            return f"음악 업계 소식: {title[:50]}..." if len(title) > 50 else title
    
    def extract_album_title_improved(self, title: str, description: str) -> str:
        """개선된 앨범 제목 추출"""
        text = f"{title} {description}"
        
        # 다양한 따옴표 패턴
        quote_patterns = [
            r"'([^']+)'",
            r'"([^"]+)"', 
            r"'([^']+)'",
            r'""([^"]+)""'
        ]
        
        for pattern in quote_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # 앨범 제목 같은 것들 필터링
                if (5 <= len(match) <= 50 and 
                    not match.lower() in ['new heights', 'ts12', 'very beautiful'] and
                    not any(word in match.lower() for word in ['very', 'new', 'first', 'live'])):
                    return match
        
        return None
    
    def calculate_importance_score(self, news: Dict) -> float:
        """중요도 점수 계산"""
        title = news.get('title', '').lower()
        description = news.get('description', '').lower()
        source = news.get('source', '')
        
        text_combined = f"{title} {description}"
        
        # 1. 소스 신뢰도 (25%)
        source_score = self.calculate_source_credibility(source)
        
        # 2. 키워드 중요도 (20%)
        high_impact_keywords = ['breaking', 'exclusive', 'first', 'debuts', 'announces', 'record-breaking']
        keyword_score = min(sum(0.1 for kw in high_impact_keywords if kw in text_combined), 0.8)
        
        # 3. 아티스트 영향력 (25%)
        artist_influence = self.calculate_artist_influence_dynamic(text_combined)
        
        # 4. 산업 임팩트 (15%)
        industry_score = 0
        if any(kw in text_combined for kw in ['album', 'chart', 'award', 'tour']):
            industry_score = 0.7
        
        # 5. 시간 요소 (10%)
        recency_score = 0.8
        
        # 6. 소셜 반응 (5%)
        social_score = 0.3
        
        final_score = (
            source_score * 0.25 +
            keyword_score * 0.20 +
            artist_influence * 0.25 +
            industry_score * 0.15 +
            recency_score * 0.10 +
            social_score * 0.05
        )
        
        return min(final_score, 1.0)
    
    def calculate_source_credibility(self, source: str) -> float:
        """소스 신뢰도 계산"""
        source_weights = {
            'billboard.com': 0.95, 'variety.com': 0.90, 'rollingstone.com': 0.88,
            'pitchfork.com': 0.85, 'musicbusinessworldwide.com': 0.85, 'consequence.net': 0.80,
            'nme.com': 0.75, 'stereogum.com': 0.75
        }
        
        source_lower = source.lower()
        for domain, weight in source_weights.items():
            if domain in source_lower:
                return weight
        return 0.5
    
    def calculate_artist_influence_dynamic(self, text: str) -> float:
        """아티스트 영향력 계산"""
        major_artists = ['taylor swift', 'bts', 'blackpink', 'drake', 'billie eilish', 'metallica']
        
        if any(artist in text for artist in major_artists):
            return 1.0
        elif any(pattern in text for pattern in ['grammy', 'billboard', 'platinum']):
            return 0.8
        elif any(genre in text for genre in ['k-pop', 'pop', 'hip-hop', 'rock']):
            return 0.6
        else:
            return 0.4
    
    def process_news_list(self, news_list: List[Dict]) -> List[Dict]:
        """뉴스 리스트 처리"""
        processed_news = []
        
        for news in news_list:
            try:
                title = news.get('title', '')
                description = news.get('description', '')
                url = news.get('url', news.get('link', ''))
                
                # 카테고리 분류
                category = self.classify_category(title, description)
                
                # 태그 추출
                tags = self.extract_tags(title, description, url)
                
                # 중요도 점수 계산
                temp_item = {**news, 'category': category, 'tags': tags}
                importance_score = self.calculate_importance_score(temp_item)
                
                # 요약 생성
                summary = self.generate_korean_summary(title, description, url)
                
                # 최종 처리된 뉴스 항목
                processed_item = {
                    **news,
                    'category': category,
                    'tags': tags,
                    'importance_score': importance_score,
                    'summary': summary,
                    'summary_type': 'rule_based'
                }
                
                processed_news.append(processed_item)
                
            except Exception as e:
                logger.error(f"뉴스 처리 오류: {e}")
                processed_news.append({
                    **news,
                    'category': 'NEWS',
                    'tags': {'genre': [], 'industry': [], 'region': []},
                    'importance_score': 0.5,
                    'summary': f"음악 업계 소식: {news.get('title', '')[:50]}...",
                    'summary_type': 'fallback'
                })
        
        logger.info(f"{len(processed_news)}개 뉴스 처리 완료")
        return processed_news
    
    def select_top_news_by_importance(self, news_list: List[Dict], max_total: int = 30) -> List[Dict]:
        """중요도 순으로 상위 뉴스 선별"""
        logger.info(f"중요도 기반 뉴스 선별: 전체 {len(news_list)}개 중 상위 {max_total}개 선별")
        
        sorted_news = sorted(news_list, key=lambda x: x.get('importance_score', 0), reverse=True)
        selected_news = sorted_news[:max_total]
        
        # 통계 로깅
        category_count = {}
        for news in selected_news:
            category = news.get('category', 'NEWS')
            category_count[category] = category_count.get(category, 0) + 1
        
        logger.info(f"선별된 {len(selected_news)}개 뉴스의 카테고리 분포:")
        for category, count in sorted(category_count.items()):
            logger.info(f"  {category}: {count}개")
        
        return selected_news
    
    def select_trending_news(self, news_list: List[Dict], max_total: int = 30) -> List[Dict]:
        """트렌딩 뉴스 선별"""
        logger.info(f"트렌딩 뉴스 선별: 전체 {len(news_list)}개 중 상위 {max_total}개 선별")
        
        # 간단한 트렌딩 점수 (중요도 기반)
        for news in news_list:
            news['trending_score'] = news.get('importance_score', 0)
        
        sorted_news = sorted(news_list, key=lambda x: x.get('trending_score', 0), reverse=True)
        selected_news = sorted_news[:max_total]
        
        return selected_news


# 테스트 코드
if __name__ == "__main__":
    # 샘플 뉴스로 테스트
    sample_news = [
        {
            'title': 'Taylor Swift Announces New Album, The Life of a Showgirl',
            'description': 'Pop superstar Taylor Swift has announced her upcoming album.',
            'url': 'https://example.com/test',
            'source': 'billboard.com'
        }
    ]
    
    classifier = AdvancedClassifier()
    processed = classifier.process_news_list(sample_news)
    
    for news in processed:
        print(f"제목: {news['title']}")
        print(f"아티스트: {classifier.extract_artists_from_text(news['title'])}")
        print(f"장르: {news['tags']['genre']}")
        print(f"요약: {news['summary']}")
        print("---")
