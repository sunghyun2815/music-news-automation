#!/usr/bin/env python3
"""
Fixed Advanced Music News Classifier - FIXED VERSION
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
        
        # 정확한 아티스트명 매핑 (소문자 -> 정확한 표기)
        self.known_artists = {
            'taylor swift': 'Taylor Swift',
            'ariana grande': 'Ariana Grande', 
            'billie eilish': 'Billie Eilish',
            'dua lipa': 'Dua Lipa',
            'olivia rodrigo': 'Olivia Rodrigo',
            'drake': 'Drake',
            'travis scott': 'Travis Scott',
            'kid cudi': 'Kid Cudi',
            'kendrick lamar': 'Kendrick Lamar',
            'bts': 'BTS',
            'blackpink': 'BLACKPINK',
            'twice': 'TWICE',
            'stray kids': 'Stray Kids',
            'newjeans': 'NewJeans',
            'ive': 'IVE',
            'aespa': 'aespa',
            'metallica': 'Metallica',
            'my chemical romance': 'My Chemical Romance',
            'mayday parade': 'Mayday Parade',
            'mother love bone': 'Mother Love Bone',
            'kaytranada': 'Kaytranada',
            'ethel cain': 'Ethel Cain',
            'wet leg': 'Wet Leg',
            'chappell roan': 'Chappell Roan',
            'doechii': 'Doechii',
            'remble': 'Remble',
            'naeem': 'Naeem',
            'chance the rapper': 'Chance the Rapper',
            'casey dienel': 'Casey Dienel',
            'sombr': 'Sombr',
            'bobby whitlock': 'Bobby Whitlock',
            'charli xcx': 'Charli XCX',
            'yung lean': 'Yung Lean',
            'spank rock': 'Spank Rock',
            'florence welch': 'Florence Welch',
            'deftones': 'Deftones',
            'dijon': 'Dijon',
            'open mike eagle': 'Open Mike Eagle',
            'snail mail': 'Snail Mail',
            'wolf alice': 'Wolf Alice',
            'travis kelce': 'Travis Kelce',
            'ozzy osbourne': 'Ozzy Osbourne',
            'robert trujillo': 'Robert Trujillo'
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
                'sabrina carpenter', 'chappell roan', 'pop music', 'mainstream pop', 'charli xcx'
            ],
            'HIP-HOP': [
                'drake', 'kendrick lamar', 'travis scott', 'kid cudi', 'cardi b', 'migos',
                'doechii', 'remble', 'hip-hop', 'rap', 'rapper', 'chance the rapper'
            ],
            'ROCK': [
                'metallica', 'my chemical romance', 'mother love bone', 'mayday parade',
                'rock', 'metal', 'punk', 'alternative', 'indie rock', 'deftones', 'wet leg'
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
    
    def extract_artists_from_text(self, text: str) -> List[str]:
        """개선된 아티스트명 추출"""
        text_lower = text.lower()
        found_artists = []
        
        # 1. 알려진 아티스트명 직접 매칭 (우선순위)
        for artist_key, artist_name in self.known_artists.items():
            if artist_key in text_lower:
                found_artists.append(artist_name)
        
        # 2. 중복 제거 및 길이순 정렬 (긴 이름 우선)
        found_artists = list(set(found_artists))
        found_artists.sort(key=len, reverse=True)
        
        # 3. 알려진 아티스트가 없으면 패턴 기반 추출
        if not found_artists:
            patterns = [
                r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',  # 두 단어 조합
                r'\b([A-Z]{2,})\b',  # 대문자만 (예: BTS, IVE)
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    # 필터링: 일반적인 단어들 제외
                    exclude_words = [
                        'Music Video', 'New Album', 'Live From', 'Very Imminent', 
                        'Is Ready', 'New Heights', 'Special Guest', 'Album The',
                        'Takes Over', 'You Should', 'Could This', 'Did Dijon',
                        'Open Mike', 'Snail Mail', 'Think Something'
                    ]
                    
                    if (len(match) > 2 and 
                        match not in exclude_words and
                        not any(word in match.lower() for word in ['new', 'first', 'live', 'from', 'very', 'is', 'the'])):
                        found_artists.append(match)
        
        return found_artists[:2]  # 최대 2개만 반환
    
    def extract_tags(self, title: str, description: str, url: str = "") -> Dict:
        """수정된 태그 추출 (더 정확한 장르 분류)"""
        text = f"{title} {description}".lower()
        
        # 장르 태그 (정확한 아티스트 기반 우선)
        genre_tags = []
        
        # 아티스트 기반 장르 분류
        artists = self.extract_artists_from_text(f"{title} {description}")
        
        for artist in artists:
            artist_lower = artist.lower()
            
            # 직접 매핑
            if artist_lower in ['taylor swift', 'ariana grande', 'billie eilish', 'dua lipa', 'olivia rodrigo', 'charli xcx']:
                genre_tags.append('POP')
            elif artist_lower in ['drake', 'travis scott', 'kendrick lamar', 'kid cudi', 'chance the rapper', 'remble', 'doechii']:
                genre_tags.append('HIP-HOP')
            elif artist_lower in ['bts', 'blackpink', 'twice', 'stray kids', 'newjeans', 'ive', 'aespa']:
                genre_tags.append('K-POP')
            elif artist_lower in ['metallica', 'my chemical romance', 'mayday parade', 'deftones', 'wet leg']:
                genre_tags.append('ROCK')
            elif artist_lower in ['kaytranada']:
                genre_tags.append('ELECTRONIC')
        
        # 아티스트 매칭이 없으면 키워드 기반
        if not genre_tags:
            for genre, keywords in self.genre_keywords.items():
                if any(keyword.lower() in text for keyword in keywords):
                    genre_tags.append(genre)
                    break  # 첫 번째 매치만 사용
        
        # 산업 태그
        industry_tags = []
        for industry, keywords in self.industry_keywords.items():
            if any(keyword.lower() in text for keyword in keywords):
                industry_tags.append(industry)
        
        # 지역 태그
        region_tags = []
        
        # K-POP이면 자동으로 KOREA 추가
        if 'K-POP' in genre_tags:
            region_tags.append('KOREA')
        
        # 다른 지역 키워드 체크
        for region, keywords in self.region_keywords.items():
            if region != 'KOREA' and any(keyword.lower() in text for keyword in keywords):
                region_tags.append(region)
        
        return {
            'genre': list(set(genre_tags))[:2],
            'industry': list(set(industry_tags))[:3],
            'region': list(set(region_tags))[:2]
        }
    
    def generate_korean_summary(self, title: str, description: str, url: str = "") -> str:
        """개선된 한국어 요약 생성 - 더 구체적이고 정보가 풍부함"""
        try:
            # 정확한 아티스트명 추출
            artist = self.extract_artist_with_context(title, description)
            
            # 앨범명, 곡명 추출
            album_title = self.extract_album_title_improved(title, description)
            song_title = self.extract_song_title(title, description)
            
            # 텍스트 분석
            title_lower = title.lower()
            desc_lower = description.lower()
            combined_text = f"{title_lower} {desc_lower}"
            
            # 1. 앨범 발표
            if 'announce' in combined_text and 'album' in combined_text:
                if album_title:
                    base_summary = f"{artist}가 새 앨범 '{album_title}'을 발표했다."
                else:
                    base_summary = f"{artist}가 새 앨범 발표 소식을 전했다."
                
                # 추가 정보
                additional_info = []
                
                if song_title:
                    additional_info.append(f"리드 싱글 '{song_title}'을 공개했다")
                
                if 'september' in desc_lower or '9월' in desc_lower:
                    additional_info.append("9월 발매 예정이다")
                elif 'october' in desc_lower or '10월' in desc_lower:
                    additional_info.append("10월 발매 예정이다")
                elif 'next month' in desc_lower or '내월' in desc_lower:
                    additional_info.append("다음 달 발매 예정이다")
                
                if 'producer' in combined_text:
                    additional_info.append("프로듀서 정보도 함께 공개했다")
                
                if 'tour' in combined_text:
                    additional_info.append("투어 중 녹음된 것으로 알려졌다")
                
                if additional_info:
                    return f"{base_summary} {' '.join(additional_info)}."
                else:
                    return base_summary
            
            # 2. 싱글/곡 공개
            elif any(word in combined_text for word in ['shares', 'hear', 'listen']) and any(word in combined_text for word in ['song', 'single', 'track']):
                if song_title:
                    base_summary = f"{artist}가 새 싱글 '{song_title}'을 공개했다."
                else:
                    base_summary = f"{artist}가 새 싱글을 발표했다."
                
                if album_title:
                    return f"{base_summary} 이 곡은 앨범 '{album_title}'에 수록될 예정이다."
                elif 'upcoming' in combined_text or '예정' in combined_text:
                    return f"{base_summary} 향후 발매될 앨범의 선공개 싱글로 보인다."
                else:
                    return base_summary
            
            # 3. 투어/콘서트
            elif 'tour' in combined_text or 'concert' in combined_text:
                if 'announce' in combined_text:
                    return f"{artist}가 새로운 투어 계획을 발표했다. 티켓 예매 및 공연 일정 정보가 공개되었다."
                elif 'expand' in combined_text:
                    return f"{artist}가 기존 투어 일정을 확장한다고 발표했다. 추가 공연 도시와 날짜가 확정되었다."
                elif 'recorded' in combined_text:
                    return f"{artist}가 투어 중 새 앨범을 녹음했다는 소식이 전해졌다."
                else:
                    return f"{artist}의 라이브 공연 관련 소식이 전해졌다."
            
            # 4. 리이슈/재발매
            elif 'reissue' in combined_text or 'deluxe' in combined_text:
                if album_title:
                    base_summary = f"{artist}의 앨범 '{album_title}' 디럭스 에디션이 발표되었다."
                else:
                    base_summary = f"{artist}의 과거 앨범이 재발매된다."
                
                additional_content = []
                if 'demo' in combined_text:
                    additional_content.append("데모 버전")
                if 'live' in combined_text:
                    additional_content.append("라이브 녹음")
                if 'unreleased' in combined_text:
                    additional_content.append("미발표 곡들")
                
                if additional_content:
                    return f"{base_summary} {', '.join(additional_content)} 등의 추가 콘텐츠가 포함되어 있다."
                else:
                    return base_summary
            
            # 5. 법적 분쟁
            elif any(word in combined_text for word in ['sued', 'lawsuit', 'legal', 'court']):
                if 'million' in combined_text:
                    amount_match = re.search(r'\$(\d+)\s*million', combined_text)
                    if amount_match:
                        amount = amount_match.group(1)
                        return f"{artist}가 {amount}00만 달러 규모의 법적 분쟁에 휘말렸다. 관련 소송이 진행 중인 것으로 알려졌다."
                
                return f"{artist}와 관련된 법적 분쟁 소식이 전해졌다."
            
            # 6. 앨범 리뷰/평가
            elif 'album of the week' in combined_text or 'review' in combined_text:
                if album_title:
                    return f"{artist}의 앨범 '{album_title}'이 주목받고 있다. 음악 평론가들로부터 긍정적인 반응을 얻고 있으며, 실험적인 사운드로 평가받고 있다."
                else:
                    return f"{artist}의 새 음반이 음악계에서 화제가 되고 있다."
            
            # 7. 협업/피처링
            elif 'feature' in combined_text or 'collaboration' in combined_text:
                # 다른 아티스트명 찾기
                other_artists = []
                for known_artist in self.known_artists.values():
                    if known_artist.lower() in combined_text and known_artist != artist:
                        other_artists.append(known_artist)
                
                if other_artists:
                    return f"{artist}가 {', '.join(other_artists)}와의 협업 소식을 전했다. 두 아티스트의 만남이 팬들 사이에서 큰 화제가 되고 있다."
                else:
                    return f"{artist}의 새로운 협업 프로젝트 소식이 공개되었다."
            
            # 8. 차트/성과
            elif any(word in combined_text for word in ['chart', 'number', '#1', 'top']):
                return f"{artist}가 최근 음악 차트에서 좋은 성과를 거두었다. 팬들과 업계의 관심이 집중되고 있다."
            
            # 9. 확인/컨펌
            elif 'confirm' in combined_text:
                if album_title:
                    return f"{artist}가 앨범 '{album_title}'의 발매일과 세부 정보를 확정했다."
                else:
                    return f"{artist}가 새로운 프로젝트의 구체적인 계획을 확정 발표했다."
            
            # 10. 부고/사망
            elif any(word in combined_text for word in ['dies', 'death', 'funeral', 'obituary', '부고']):
                return f"음악계 인사의 부고 관련 소식이 전해졌다."
            
            # 11. 기본 케이스 - 더 구체적으로
            else:
                if album_title and song_title:
                    return f"{artist}가 앨범 '{album_title}'의 수록곡 '{song_title}' 관련 소식을 전했다."
                elif album_title:
                    return f"{artist}가 앨범 '{album_title}' 관련 활동 소식을 공개했다."
                elif song_title:
                    return f"{artist}가 신곡 '{song_title}' 관련 소식을 발표했다."
                else:
                    return f"{artist}의 최신 음악 활동 소식이 업데이트되었다."
        
        except Exception as e:
            logger.error(f"한국어 요약 생성 오류: {e}")
            return f"음악 업계 소식: {title[:50]}..." if len(title) > 50 else title
    
    def extract_artist_with_context(self, title: str, description: str) -> str:
        """문맥을 고려한 정확한 아티스트명 추출"""
        text = f"{title} {description}".lower()
        
        # 1. 알려진 아티스트 직접 매칭 (가장 긴 이름부터)
        sorted_artists = sorted(self.known_artists.items(), key=lambda x: len(x[0]), reverse=True)
        for artist_key, artist_name in sorted_artists:
            if artist_key in text:
                return artist_name
        
        # 2. 제목에서 첫 번째 부분 추출
        title_words = title.split()
        if title_words:
            # "Artist Name Announces..." 패턴
            if len(title_words) >= 2:
                first_two = ' '.join(title_words[:2])
                if not any(word.lower() in ['new', 'the', 'a', 'an', 'album', 'song'] for word in title_words[:2]):
                    return first_two
            
            # 단일 단어 아티스트명
            if title_words[0] not in ['New', 'The', 'A', 'An', 'Album', 'Song']:
                return title_words[0]
        
        return "음악 아티스트"
    
    def extract_song_title(self, title: str, description: str) -> str:
        """곡 제목 추출"""
        text = f"{title} {description}"
        
        song_patterns = [
            r'hear\s+["\']([^"\']+)["\']',
            r'single\s+["\']([^"\']+)["\']',
            r'song\s+["\']([^"\']+)["\']',
            r'track\s+["\']([^"\']+)["\']',
            r'["\']([^"\']+)["\'].*single',
            r':\s*hear\s+["\']([^"\']+)["\']',
            r':\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in song_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if 2 <= len(match) <= 40 and not any(word in match.lower() for word in ['album', 'new', 'the', 'a']):
                    return match
        
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
    def process_news_list(self, news_list: List[Dict]) -> List[Dict]:
        """뉴스 리스트 처리 (중요도 점수 포함)"""
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
    
    def select_top_news_by_importance(self, news_list: List[Dict], max_total: int = 20) -> List[Dict]:
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
    
    def select_trending_news(self, news_list: List[Dict], max_total: int = 20) -> List[Dict]:
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
        },
        {
            'title': 'Remble Drops New Album Juco',
            'description': 'Hip-hop artist Remble has released his latest album.',
            'url': 'https://example.com/test2',
            'source': 'pitchfork.com'
        },
        {
            'title': 'Bobby Whitlock, Derek & the Dominos Co-Founder, Dies at 77',
            'description': 'The legendary musician has passed away.',
            'url': 'https://example.com/test3',
            'source': 'rollingstone.com'
        }
    ]
    
    classifier = AdvancedClassifier()
    processed = classifier.process_news_list_simplified(sample_news)
    
    print("=== 테스트 결과 ===")
    for news in processed:
        print(f"제목: {news['title']}")
        
        # 아티스트 추출 테스트
        artists = classifier.extract_artists_from_text(news['title'])
        print(f"추출된 아티스트: {artists}")
        
        print(f"장르: {news['tags']['genre']}")
        print(f"요약: {news['summary']}")
        print("---")
    
    def calculate_artist_influence_dynamic(self, text: str) -> float:
        """아티스트 영향력 계산"""
        # 메가 스타들
        mega_stars = ['taylor swift', 'bts', 'blackpink', 'drake', 'billie eilish']
        if any(artist in text for artist in mega_stars):
            return 1.0
        
        # 주요 아티스트들
        major_artists = ['ariana grande', 'dua lipa', 'travis scott', 'kendrick lamar', 'metallica']
        if any(artist in text for artist in major_artists):
            return 0.9
        
        # 기타 유명 아티스트들
        known_artists = list(self.known_artists.keys())
        if any(artist in text for artist in known_artists):
            return 0.7
        
        # 업계 키워드
        if any(pattern in text for pattern in ['grammy', 'billboard', 'platinum', 'chart']):
            return 0.8
        
        return 0.5
    
    def extract_album_title_improved(self, title: str, description: str) -> str:
        """개선된 앨범 제목 추출"""
        text = f"{title} {description}"
        
        # 다양한 따옴표 패턴
        quote_patterns = [
            r"'([^']+)'",
            r'"([^"]+)"', 
            r"'([^']+)'",
            r'"([^"]+)"'
        ]
        
        for pattern in quote_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # 앨범 제목 같은 것들 필터링
                if (3 <= len(match) <= 50 and 
                    not match.lower() in ['new heights', 'ts12', 'very beautiful'] and
                    not any(word in match.lower() for word in ['very', 'new', 'first', 'live', 'from'])):
                    return match
        
        return Nonetitle, description)
                if album_title:
                    return f"{who}가 새 앨범 '{album_title}'을 발표했습니다."
                else:
                    return f"{who}가 새 앨범 발매 소식을 전했습니다."
            
            # 5. 투어 관련
            if any(word in text for word in ['tour', 'concert']) and any(word in text for word in ['announces', 'expand', 'adds']):
                return f"{who}가 새로운 투어 계획을 발표했습니다."
            
            # 6. 차트 성과
            if any(word in text for word in ['chart', '#1', 'number one', 'top']):
                return f"{who}가 음악 차트에서 좋은 성과를 거두었습니다."
            
            # 7. 새 곡/싱글 공개
            if any(word in text for word in ['shares', 'releases', 'drops']) and any(word in text for word in ['song', 'single', 'track']):
                return f"{who}가 새로운 곡을 공개했습니다."
            
            # 8. 라이브 공연/커버
            if any(word in text for word in ['live', 'cover', 'perform']):
                return f"{who}가 라이브 공연에서 특별한 무대를 선보였습니다."
            
            # 9. 법적 분쟁
            if any(word in text for word in ['lawsuit', 'sue', 'court', 'legal']):
                return f"음악 업계에서 법적 분쟁 관련 소식이 전해졌습니다."
            
            # 10. 비디오/뮤직비디오
            if any(word in text for word in ['video', 'watch', 'visual']):
                return f"{who}가 새로운 비디오 콘텐츠를 공개했습니다."
            
            # 11. 기본 케이스
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
            r'"([^"]+)"'
        ]
        
        for pattern in quote_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # 앨범 제목 같은 것들 필터링
                if (3 <= len(match) <= 50 and 
                    not match.lower() in ['new heights', 'ts12', 'very beautiful', 'the life of a showgirl'] and
                    not any(word in match.lower() for word in ['very', 'new', 'first', 'live', 'from'])):
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
        # 메가 스타들
        mega_stars = ['taylor swift', 'bts', 'blackpink', 'drake', 'billie eilish']
        if any(artist in text for artist in mega_stars):
            return 1.0
        
        # 주요 아티스트들
        major_artists = ['ariana grande', 'dua lipa', 'travis scott', 'kendrick lamar', 'metallica']
        if any(artist in text for artist in major_artists):
            return 0.9
        
        # 기타 유명 아티스트들
        known_artists = list(self.known_artists.keys())
        if any(artist in text for artist in known_artists):
            return 0.7
        
        # 업계 키워드
        if any(pattern in text for pattern in ['grammy', 'billboard', 'platinum', 'chart']):
            return 0.8
        
        return 0.5
    
    def process_news_list_simplified(self, news_list: List[Dict]) -> List[Dict]:
        """뉴스 리스트 처리 - 단순화된 버전 (중요도 점수 제외)"""
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
                
                # 요약 생성
                summary = self.generate_korean_summary(title, description, url)
                
                # 최종 처리된 뉴스 항목 (중요도 점수 없음)
                processed_item = {
                    **news,
                    'category': category,
                    'tags': tags,
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
                    'summary': f"음악 업계 소식: {news.get('title', '')[:50]}...",
                    'summary_type': 'fallback'
                })
        
        logger.info(f"{len(processed_news)}개 뉴스 처리 완료 (단순화된 버전)")
        return processed_news
    
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
    
    def select_top_news_by_importance(self, news_list: List[Dict], max_total: int = 20) -> List[Dict]:
        """중요도 순으로 상위 뉴스 선별 - 개수 줄임"""
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
    
    def select_trending_news(self, news_list: List[Dict], max_total: int = 20) -> List[Dict]:
        """트렌딩 뉴스 선별 - 개수 줄임"""
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
        },
        {
            'title': 'Remble Drops New Album Juco',
            'description': 'Hip-hop artist Remble has released his latest album.',
            'url': 'https://example.com/test2',
            'source': 'pitchfork.com'
        },
        {
            'title': 'Bobby Whitlock, Derek & the Dominos Co-Founder, Dies at 77',
            'description': 'The legendary musician has passed away.',
            'url': 'https://example.com/test3',
            'source': 'rollingstone.com'
        }
    ]
    
    classifier = AdvancedClassifier()
    processed = classifier.process_news_list(sample_news)
    
    print("=== 테스트 결과 ===")
    for news in processed:
        print(f"제목: {news['title']}")
        
        # 아티스트 추출 테스트
        artists = classifier.extract_artists_from_text(news['title'])
        print(f"추출된 아티스트: {artists}")
        
        print(f"장르: {news['tags']['genre']}")
        print(f"요약: {news['summary']}")
        print(f"중요도: {news['importance_score']:.3f}")
        print("---")
