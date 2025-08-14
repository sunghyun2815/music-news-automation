#!/usr/bin/env python3
"""
Clean Advanced Music News Classifier
문법 오류가 해결된 깔끔한 음악 뉴스 분류 시스템
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
        
        # 정확한 아티스트명 매핑
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
            'robert trujillo': 'Robert Trujillo',
            'pickle darling': 'Pickle Darling',
            'the berries': 'The Berries',
            'the antlers': 'The Antlers',
            'devendra banhart': 'Devendra Banhart',
            'the armed': 'The Armed',
            'lucas mayo': 'Lucas Mayo',
            'matthew berry': 'Matthew Berry',
            'sabrina carpenter': 'Sabrina Carpenter',
            'priscilla presley': 'Priscilla Presley'
        }
        
        # 장르 키워드
        self.genre_keywords = {
            'K-POP': [
                'k-pop', 'kpop', 'korean pop', 'bts', 'blackpink', 'twice', 'stray kids',
                'newjeans', 'ive', 'aespa', 'itzy', 'seventeen', 'txt', 'le sserafim'
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
        """아티스트명 추출"""
        text_lower = text.lower()
        found_artists = []
        
        # 알려진 아티스트명 직접 매칭
        sorted_artists = sorted(self.known_artists.items(), key=lambda x: len(x[0]), reverse=True)
        for artist_key, artist_name in sorted_artists:
            if artist_key in text_lower:
                found_artists.append(artist_name)
        
        # 중복 제거
        found_artists = list(set(found_artists))
        return found_artists[:2]
    
    def extract_artist_with_context(self, title: str, description: str) -> str:
        """문맥을 고려한 정확한 아티스트명 추출"""
        text = f"{title} {description}".lower()
        
        # 알려진 아티스트 직접 매칭
        sorted_artists = sorted(self.known_artists.items(), key=lambda x: len(x[0]), reverse=True)
        for artist_key, artist_name in sorted_artists:
            if artist_key in text:
                return artist_name
        
        # 제목에서 첫 번째 부분 추출
        title_words = title.split()
        if title_words:
            if len(title_words) >= 2:
                first_two = ' '.join(title_words[:2])
                if not any(word.lower() in ['new', 'the', 'a', 'an', 'album', 'song'] for word in title_words[:2]):
                    return first_two
            
            if title_words[0] not in ['New', 'The', 'A', 'An', 'Album', 'Song']:
                return title_words[0]
        
        return "음악 아티스트"
    
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
                if (3 <= len(match) <= 50 and 
                    not match.lower() in ['new heights', 'ts12', 'very beautiful'] and
                    not any(word in match.lower() for word in ['very', 'new', 'first', 'live', 'from'])):
                    return match
        
        return None
    
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
        
        return None
    
    def extract_tags(self, title: str, description: str, url: str = "") -> Dict:
        """태그 추출"""
        text = f"{title} {description}".lower()
        
        # 장르 태그
        genre_tags = []
        artists = self.extract_artists_from_text(f"{title} {description}")
        
        for artist in artists:
            artist_lower = artist.lower()
            
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
                    break
        
        # 산업 태그
        industry_tags = []
        for industry, keywords in self.industry_keywords.items():
            if any(keyword.lower() in text for keyword in keywords):
                industry_tags.append(industry)
        
        # 지역 태그
        region_tags = []
        if 'K-POP' in genre_tags:
            region_tags.append('KOREA')
        
        for region, keywords in self.region_keywords.items():
            if region != 'KOREA' and any(keyword.lower() in text for keyword in keywords):
                region_tags.append(region)
        
        return {
            'genre': list(set(genre_tags))[:2],
            'industry': list(set(industry_tags))[:3],
            'region': list(set(region_tags))[:2]
        }
    
    def generate_korean_summary(self, title: str, description: str, url: str = "") -> str:
        """개선된 한국어 요약 생성"""
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
            
            # 4. 법적 분쟁
            elif any(word in combined_text for word in ['sued', 'lawsuit', 'legal', 'court']):
                if 'million' in combined_text:
                    amount_match = re.search(r'\$(\d+)\s*million', combined_text)
                    if amount_match:
                        amount = amount_match.group(1)
                        return f"{artist}가 {amount}00만 달러 규모의 법적 분쟁에 휘말렸다. 관련 소송이 진행 중인 것으로 알려졌다."
                
                return f"{artist}와 관련된 법적 분쟁 소식이 전해졌다."
            
            # 5. 협업/피처링
            elif 'feature' in combined_text or 'collaboration' in combined_text:
                other_artists = []
                for known_artist in self.known_artists.values():
                    if known_artist.lower() in combined_text and known_artist != artist:
                        other_artists.append(known_artist)
                
                if other_artists:
                    return f"{artist}가 {', '.join(other_artists)}와의 협업 소식을 전했다. 두 아티스트의 만남이 팬들 사이에서 큰 화제가 되고 있다."
                else:
                    return f"{artist}의 새로운 협업 프로젝트 소식이 공개되었다."
            
            # 6. 차트/성과
            elif any(word in combined_text for word in ['chart', 'number', '#1', 'top']):
                return f"{artist}가 최근 음악 차트에서 좋은 성과를 거두었다. 팬들과 업계의 관심이 집중되고 있다."
            
            # 7. 확인/컨펌
            elif 'confirm' in combined_text:
                if album_title:
                    return f"{artist}가 앨범 '{album_title}'의 발매일과 세부 정보를 확정했다."
                else:
                    return f"{artist}가 새로운 프로젝트의 구체적인 계획을 확정 발표했다."
            
            # 8. 부고/사망
            elif any(word in combined_text for word in ['dies', 'death', 'funeral', 'obituary', '부고']):
                return f"음악계 인사의 부고 관련 소식이 전해졌다."
            
            # 9. 기본 케이스
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
                
                # 최종 처리된 뉴스 항목
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


# 테스트 코드
if __name__ == "__main__":
    sample_news = [
        {
            'title': 'Taylor Swift Announces New Album, The Life of a Showgirl',
            'description': 'Pop superstar Taylor Swift has announced her upcoming album.',
            'url': 'https://example.com/test',
            'source': 'billboard.com'
        }
    ]
    
    classifier = AdvancedClassifier()
    processed = classifier.process_news_list_simplified(sample_news)
    
    print("=== 테스트 결과 ===")
    for news in processed:
        print(f"제목: {news['title']}")
        print(f"요약: {news['summary']}")
        print("---")
