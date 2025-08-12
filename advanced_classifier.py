#!/usr/bin/env python3
"""
Advanced Music News Classifier
음악 뉴스 분류, 태깅, 요약, 중요도 계산 시스템
"""

import re
import logging
from datetime import datetime
from typing import List, Dict

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedClassifier:
    def __init__(self, use_ai_summary: bool = False, use_claude_summary: bool = False):
        """분류기 초기화"""
        self.use_ai_summary = use_ai_summary
        self.use_claude_summary = use_claude_summary
        self.ai_summarizer = None
        self.claude_summarizer = None
        
        # Claude 요약기 초기화 (우선순위)
        if self.use_claude_summary:
            try:
                from anthropic_summarizer import AnthropicSummarizer
                self.claude_summarizer = AnthropicSummarizer()
                logger.info("Claude 요약기 초기화 완료")
            except Exception as e:
                logger.warning(f"Claude 요약기 초기화 실패: {e}")
                self.claude_summarizer = None
        
        # OpenAI 요약기 초기화 (Claude 없을 때)
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
        
        # 장르 키워드
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
            'ROCK': ['rock', 'metal', 'punk', 'alternative', 'indie rock', 'hard rock'],
            'R&B': ['r&b', 'rnb', 'soul', 'neo-soul', 'the weeknd', 'sza', 'frank ocean'],
            'ELECTRONIC': ['electronic', 'edm', 'house', 'techno', 'dubstep', 'synthpop']
        }
        
        # 산업 키워드
        self.industry_keywords = {
            'STREAMING': ['spotify', 'apple music', 'youtube music', 'streaming', 'playlist', '스트리밍', '플레이리스트'],
            'LABEL': ['record label', 'signs', 'contract', 'deal', 'universal', 'sony', 'warner', '레코드', '계약', '레이블'],
            'TOUR': ['tour', 'concert', 'live', 'venue', 'tickets', 'sold out', '투어', '콘서트', '공연', '티켓'],
            'ALBUM': ['album', 'ep', 'single', 'release', 'track', 'song', '앨범', '싱글', '곡', '발매'],
            'CHART': ['billboard', 'hot 100', 'chart', 'number one', 'top 10', '차트', '1위', '순위'],
            'AWARD': ['grammy', 'award', 'nomination', 'wins', 'ceremony', '그래미', '상', '수상', '시상식']
        }
        
        # 지역 키워드
        self.region_keywords = {
            'KOREA': ['korea', 'korean', 'seoul', 'k-pop', 'kpop', 'hallyu', '한국', '서울', '케이팝'],
            'US': ['america', 'american', 'usa', 'united states', 'billboard', 'hollywood'],
            'UK': ['britain', 'british', 'uk', 'united kingdom', 'london', 'bbc'],
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
        """태그 추출"""
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
    
    def calculate_importance_score(self, news: Dict) -> float:
        """중요도 점수 계산"""
        title = news.get('title', '').lower()
        description = news.get('description', '').lower()
        source = news.get('source', '')
        published_date = news.get('published_date', '')
        
        text_combined = f"{title} {description}"
        
        # 1. 소스 신뢰도 (25%)
        source_score = self.calculate_source_credibility(source)
        
        # 2. 키워드 중요도 (20%)
        high_impact_keywords = [
            'breaking', 'exclusive', 'first', 'debuts', 'announces', 'record-breaking',
            '신곡', '발매', '콘서트', '첫', '독점', '화제', '데뷔', '컴백'
        ]
        
        keyword_score = 0
        for keyword in high_impact_keywords:
            if keyword in text_combined:
                keyword_score += 0.1
        keyword_score = min(keyword_score, 0.8)
        
        # 3. 아티스트 영향력 (25%)
        artist_influence = self.calculate_artist_influence_dynamic(text_combined)
        
        # 4. 산업 임팩트 (15%)
        industry_impact_weights = {
            'album': 0.8, 'tour': 0.7, 'collaboration': 0.6, 
            'chart': 0.9, 'award': 0.9, 'debut': 0.7,
            'streaming': 0.5, 'label': 0.6
        }
        
        industry_score = 0
        for keyword, weight in industry_impact_weights.items():
            if keyword in text_combined:
                industry_score = max(industry_score, weight)
        
        # 5. 시간 요소 (10%)
        recency_score = self.calculate_recency_simple(published_date)
        
        # 6. 소셜 반응 (5%)
        social_score = self.estimate_social_impact(text_combined)
        
        # 가중 평균
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
            'billboard.com': 0.95,
            'variety.com': 0.90,
            'rollingstone.com': 0.88,
            'pitchfork.com': 0.85,
            'musicbusinessworldwide.com': 0.85,
            'consequence.net': 0.80,
            'nme.com': 0.75,
            'stereogum.com': 0.75,
            'allkpop.com': 0.70,
            'soompi.com': 0.70
        }
        
        source_lower = source.lower()
        
        for domain, weight in source_weights.items():
            if domain in source_lower:
                return weight
        
        if any(trusted in source_lower for trusted in ['billboard', 'variety', 'rolling']):
            return 0.8
        elif any(music in source_lower for music in ['music', 'sound']):
            return 0.6
        else:
            return 0.5
    
    def calculate_artist_influence_dynamic(self, text: str) -> float:
        """동적 아티스트 영향력 계산"""
        major_artists = [
            'taylor swift', 'bts', 'blackpink', 'drake', 'billie eilish',
            'newjeans', 'stray kids', 'ive', 'aespa', 'seventeen', 'twice',
            'ariana grande', 'the weeknd', 'dua lipa', 'olivia rodrigo'
        ]
        
        if any(artist in text for artist in major_artists):
            return 1.0
        elif any(pattern in text for pattern in ['grammy', 'billboard', 'platinum', 'million']):
            return 0.8
        elif any(genre in text for genre in ['k-pop', 'pop', 'hip-hop']):
            return 0.6
        else:
            return 0.4
    
    def calculate_recency_simple(self, published_date: str) -> float:
        """간단한 최신성 계산"""
        if not published_date:
            return 0.5
        
        try:
            formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%a, %d %b %Y %H:%M:%S %Z']
            
            pub_date = None
            for fmt in formats:
                try:
                    pub_date = datetime.strptime(published_date.replace('Z', ''), fmt.replace('%Z', ''))
                    break
                except ValueError:
                    continue
            
            if not pub_date:
                return 0.5
            
            hours_diff = (datetime.now() - pub_date).total_seconds() / 3600
            
            if hours_diff <= 6:
                return 1.0
            elif hours_diff <= 24:
                return 0.8
            elif hours_diff <= 72:
                return 0.6
            else:
                return 0.3
                
        except:
            return 0.5
    
    def estimate_social_impact(self, text: str) -> float:
        """소셜 임팩트 간단 추정"""
        social_keywords = ['viral', 'trending', 'buzz', 'social media', '화제', '트렌드']
        
        impact = 0.3
        for keyword in social_keywords:
            if keyword in text:
                impact += 0.1
        
        return min(impact, 1.0)
    
    def generate_korean_summary(self, title: str, description: str, url: str = "") -> str:
        """한글 규칙 기반 요약 생성"""
        try:
            text = f"{title} {description}".lower()
            
            # Who 추출
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
            
            # 요약 생성
            summary = f"{who}가 {when} 음악 관련 소식을 전했습니다."
            
            # 추가 컨텍스트
            if 'album' in text or '앨범' in text:
                summary = f"{who}가 {when} 새 앨범 관련 소식을 발표했습니다."
            elif 'tour' in text or '투어' in text:
                summary = f"{who}가 {when} 투어 관련 소식을 발표했습니다."
            elif 'chart' in text or '차트' in text:
                summary = f"{who}가 {when} 차트에서 좋은 성과를 거두었습니다."
            
            return summary
            
        except Exception as e:
            logger.error(f"한글 요약 생성 오류: {e}")
            return f"음악 업계 소식: {title[:50]}..." if len(title) > 50 else title
    
    def extract_artists_from_text(self, text: str) -> List[str]:
        """텍스트에서 아티스트명 추출"""
        artists = []
        
        patterns = [
            r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',
            r'\b([A-Z]{2,})\b',
            r'"([^"]+)"',
            r"'([^']+)'",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            artists.extend(matches)
        
        unique_artists = list(set(artists))
        stopwords = {'Music', 'Video', 'News', 'Album', 'Song', 'Tour', 'Concert'}
        filtered_artists = [artist for artist in unique_artists if artist not in stopwords]
        
        return filtered_artists[:5]
    
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
                
                # 임시 항목 생성
                temp_item = {
                    **news,
                    'category': category,
                    'tags': tags
                }
                
                # 중요도 점수 계산
                importance_score = self.calculate_importance_score(temp_item)
                
                # 최종 처리된 뉴스 항목
                processed_item = {
                    **news,
                    'category': category,
                    'tags': tags,
                    'importance_score': importance_score
                }
                
                processed_news.append(processed_item)
                
            except Exception as e:
                logger.error(f"뉴스 처리 오류: {e} - 뉴스: {news.get('title', '제목 없음')}")
                processed_news.append({
                    **news,
                    'category': 'NEWS',
                    'tags': {'genre': [], 'industry': [], 'region': []},
                    'importance_score': 0.5
                })
        
        # 요약 처리
        if self.use_claude_summary and self.claude_summarizer:
            # Claude 요약 사용
            try:
                logger.info("Claude 요약 시작...")
                sorted_news = sorted(processed_news, key=lambda x: x.get('importance_score', 0), reverse=True)
                claude_processed = self.claude_summarizer.batch_summarize(sorted_news[:10], max_items=10)
                
                final_news = []
                for i, news in enumerate(sorted_news):
                    if i < len(claude_processed) and 'claude_summary' in claude_processed[i]:
                        news['summary'] = claude_processed[i]['claude_summary']
                        news['summary_type'] = 'claude_generated'
                    else:
                        news['summary'] = self.generate_korean_summary(
                            news.get('title', ''), 
                            news.get('description', ''), 
                            news.get('url', '')
                        )
                        news['summary_type'] = 'rule_based'
                    final_news.append(news)
                
                processed_news = final_news
                
            except Exception as e:
                logger.error(f"Claude 요약 오류: {e}")
                for news in processed_news:
                    if 'summary' not in news:
                        news['summary'] = self.generate_korean_summary(
                            news.get('title', ''), 
                            news.get('description', ''), 
                            news.get('url', '')
                        )
                        news['summary_type'] = 'rule_based'
        
        elif self.use_ai_summary and self.ai_summarizer:
            # OpenAI 요약 사용
            try:
                sorted_news = sorted(processed_news, key=lambda x: x.get('importance_score', 0), reverse=True)
                ai_processed = self.ai_summarizer.batch_summarize(sorted_news[:10], max_items=10)
                
                final_news = []
                for i, news in enumerate(sorted_news):
                    if i < len(ai_processed) and 'ai_summary' in ai_processed[i]:
                        news['summary'] = ai_processed[i]['ai_summary']
                        news['summary_type'] = 'ai_generated'
                    else:
                        news['summary'] = self.generate_korean_summary(
                            news.get('title', ''), 
                            news.get('description', ''), 
                            news.get('url', '')
                        )
                        news['summary_type'] = 'rule_based'
                    final_news.append(news)
                
                processed_news = final_news
                        
            except Exception as e:
                logger.error(f"AI 요약 오류: {e}")
                for news in processed_news:
                    if 'summary' not in news:
                        news['summary'] = self.generate_korean_summary(
                            news.get('title', ''), 
                            news.get('description', ''), 
                            news.get('url', '')
                        )
                        news['summary_type'] = 'rule_based'
        else:
            # 규칙 기반 요약만 사용
            for news in processed_news:
                news['summary'] = self.generate_korean_summary(
                    news.get('title', ''), 
                    news.get('description', ''), 
                    news.get('url', '')
                )
                news['summary_type'] = 'rule_based'
        
        logger.info(f"{len(processed_news)}개 뉴스 처리 완료")
        return processed_news
    
    def select_top_news_by_importance(self, news_list: List[Dict], max_total: int = 30) -> List[Dict]:
        """중요도 순으로 상위 뉴스 선별"""
        logger.info(f"중요도 기반 뉴스 선별: 전체 {len(news_list)}개 중 상위 {max_total}개 선별")
        
        # 중요도 점수로 정렬
        sorted_news = sorted(
            news_list, 
            key=lambda x: x.get('importance_score', 0), 
            reverse=True
        )
        
        # 상위 N개 선택
        selected_news = sorted_news[:max_total]
        
        # 통계 로깅
        category_count = {}
        for news in selected_news:
            category = news.get('category', 'NEWS')
            category_count[category] = category_count.get(category, 0) + 1
        
        logger.info(f"선별된 {len(selected_news)}개 뉴스의 카테고리 분포:")
        for category, count in sorted(category_count.items()):
            logger.info(f"  {category}: {count}개")
        
        if selected_news:
            highest_score = selected_news[0].get('importance_score', 0)
            lowest_score = selected_news[-1].get('importance_score', 0)
            logger.info(f"중요도 점수 범위: {lowest_score:.3f} ~ {highest_score:.3f}")
        
        return selected_news
    
    def select_trending_news(self, news_list: List[Dict], max_total: int = 30) -> List[Dict]:
        """트렌딩 뉴스 선별"""
        logger.info(f"트렌딩 뉴스 선별: 전체 {len(news_list)}개 중 상위 {max_total}개 선별")
        
        # 트렌딩 점수 계산
        for news in news_list:
            importance = news.get('importance_score', 0)
            
            # 최신성 보너스
            recency_bonus = self.calculate_recency_bonus(news.get('published_date', ''))
            
            # 화제성 보너스
            trending_bonus = self.calculate_trending_bonus(news)
            
            # 아티스트 인기도 보너스
            artist_bonus = self.calculate_artist_popularity_bonus(news)
            
            # 트렌딩 점수 계산
            trending_score = (
                importance * 0.70 + 
                recency_bonus * 0.15 + 
                trending_bonus * 0.10 + 
                artist_bonus * 0.05
            )
            
            news['trending_score'] = min(trending_score, 1.0)
        
        # 트렌딩 점수로 정렬
        sorted_news = sorted(
            news_list, 
            key=lambda x: x.get('trending_score', 0), 
            reverse=True
        )
        
        # 상위 N개 선택
        selected_news = sorted_news[:max_total]
        
        # 통계 로깅
        if selected_news:
            highest_trending = selected_news[0].get('trending_score', 0)
            lowest_trending = selected_news[-1].get('trending_score', 0)
            logger.info(f"트렌딩 점수 범위: {lowest_trending:.3f} ~ {highest_trending:.3f}")
        
        return selected_news
    
    def calculate_recency_bonus(self, published_date: str) -> float:
        """최신성 보너스 계산"""
        if not published_date:
            return 0.3
        
        try:
            formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%a, %d %b %Y %H:%M:%S %Z']
            
            pub_date = None
            for fmt in formats:
                try:
                    pub_date = datetime.strptime(published_date.replace('Z', ''), fmt.replace('%Z', ''))
                    break
                except ValueError:
                    continue
            
            if not pub_date:
                return 0.3
            
            hours_diff = (datetime.now() - pub_date).total_seconds() / 3600
            
            if hours_diff <= 3:
                return 1.0
            elif hours_diff <= 12:
                return 0.8
            elif hours_diff <= 24:
                return 0.6
            elif hours_diff <= 72:
                return 0.4
            else:
                return 0.2
                
        except:
            return 0.3
    
    def calculate_trending_bonus(self, news: Dict) -> float:
        """화제성 보너스 계산"""
        title = news.get('title', '').lower()
        description = news.get('description', '').lower()
        text = f"{title} {description}"
        
        trending_keywords = {
            'viral': 0.3, 'trending': 0.3, 'buzz': 0.2, 'hot': 0.2,
            'controversy': 0.25, 'scandal': 0.25, 'drama': 0.2,
            'record-breaking': 0.3, 'milestone': 0.25, 'historic': 0.25,
            'surprising': 0.2, 'unexpected': 0.2, 'shocking': 0.25,
            'comeback': 0.3, 'debut': 0.25, 'collaboration': 0.2,
            '화제': 0.3, '트렌드': 0.3, '논란': 0.25, '컴백': 0.3,
            '데뷔': 0.25, '기록': 0.3, '돌풍': 0.3, '센세이션': 0.3
        }
        
        bonus = 0.0
        for keyword, score in trending_keywords.items():
            if keyword in text:
                bonus += score
        
        return min(bonus, 1.0)
    
    def calculate_artist_popularity_bonus(self, news: Dict) -> float:
        """아티스트 인기도 보너스 계산"""
        title = news.get('title', '').lower()
        description = news.get('description', '').lower()
        text = f"{title} {description}"
        
        # 현재 인기 아티스트들
        mega_stars = [
            'taylor swift', 'bts', 'blackpink', 'drake', 'billie eilish',
            'newjeans', 'stray kids', 'ive', 'aespa', 'seventeen'
        ]
        
        popular_artists = [
            'twice', 'itzy', 'le sserafim', 'nmixx', 'gidle', 'red velvet',
            'txt', 'enhypen', 'nct', 'riize', 'kiss of life',
            'ariana grande', 'dua lipa', 'olivia rodrigo', 'sabrina carpenter'
        ]
        
        rising_artists = [
            'illit', 'babymonster', 'zerobaseone', 'fifty fifty',
            'tyla', 'chappell roan', 'pinkpantheress', 'ice spice'
        ]
        
        # 보너스 계산
        if any(artist in text for artist in mega_stars):
            return 1.0
        elif any(artist in text for artist in popular_artists):
            return 0.7
        elif any(artist in text for artist in rising_artists):
            return 0.5
        else:
            return 0.2


# 테스트 코드
if __name__ == "__main__":
    sample_news = [
        {
            'title': 'BTS Announces World Stadium Tour 2025',
            'description': 'Global K-pop sensation BTS has announced their biggest world tour yet.',
            'url': 'https://example.com/bts-tour',
            'source': 'billboard.com',
            'published_date': '2025-08-12 10:00:00'
        }
    ]
    
    print("=== Advanced Classifier 테스트 ===")
    classifier = AdvancedClassifier(use_ai_summary=False)
    processed_news = classifier.process_news_list(sample_news)
    selected_news = classifier.select_trending_news(processed_news, max_total=30)
    
    print(f"처리된 뉴스: {len(processed_news)}개")
    print(f"선별된 뉴스: {len(selected_news)}개")
    print("✅ 테스트 완료!")
