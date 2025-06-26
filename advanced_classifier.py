#!/usr/bin/env python3
"""
Advanced Music News Classifier
음악 뉴스 분류, 태깅, 5W1H 요약 시스템 (개선된 버전)
"""

import re
import logging
from typing import List, Dict, Set
from datetime import datetime
import json

# NLTK 데이터 다운로드 (필요한 경우 주석 해제 후 실행)
# import nltk
# try:
#     nltk.data.find('corpora/stopwords')
# except nltk.downloader.DownloadError:
#     nltk.download('stopwords')
# try:
#     nltk.data.find('tokenizers/punkt')
# except nltk.downloader.DownloadError:
#     nltk.download('punkt')

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedClassifier:
    def __init__(self):
        # 카테고리 분류 키워드
        self.category_keywords = {
            'NEWS': [
                'announces', 'releases', 'drops', 'unveils', 'reveals', 'confirms',
                'debuts', 'premieres', 'launches', 'shares', 'posts', 'teases',
                'breaking', 'just in', 'exclusive', 'first look', 'new song',
                'new album', 'new single', 'tour dates', 'collaboration'
            ],
            'REPORT': [
                'revenue', 'earnings', 'sales', 'chart', 'statistics', 'data',
                'market', 'industry report', 'quarterly', 'annual', 'growth',
                'decline', 'percentage', 'million', 'billion', 'streaming numbers',
                'box office', 'ticket sales', 'study shows', 'research'
            ],
            'INSIGHT': [
                'trend', 'analysis', 'future', 'prediction', 'forecast',
                'impact', 'influence', 'change', 'evolution', 'transformation',
                'why', 'how', 'what this means', 'implications', 'significance',
                'deep dive', 'explained', 'breakdown', 'behind the scenes'
            ],
            'INTERVIEW': [
                'interview', 'talks', 'speaks', 'says', 'tells', 'discusses',
                'reveals in', 'opens up', 'shares thoughts', 'exclusive chat',
                'conversation with', 'Q&A', 'sits down with', 'profile'
            ],
            'COLUMN': [
                'opinion', 'editorial', 'commentary', 'perspective', 'viewpoint',
                'think piece', 'argues', 'believes', 'suggests', 'proposes',
                'criticism', 'review', 'critique', 'analysis piece'
            ]
        }
        
        # 음악 장르 키워드 (우선순위)
        self.genre_keywords = {
            'KPOP': [
                'k-pop', 'kpop', 'korean pop', 'bts', 'blackpink', 'twice', 'stray kids',
                'itzy', 'aespa', 'newjeans', 'ive', 'le sserafim', 'seventeen',
                'txt', 'enhypen', 'ateez', 'korea', 'korean', 'seoul', 'hybe',
                'sm entertainment', 'yg entertainment', 'jyp entertainment'
            ],
            'HIPHOP': [
                'hip hop', 'hip-hop', 'hiphop', 'rap', 'rapper', 'mc', 'freestyle',
                'trap', 'drill', 'gangsta rap', 'conscious rap', 'mumble rap',
                'kendrick lamar', 'drake', 'kanye', 'jay-z', 'eminem', 'nas',
                'travis scott', 'future', 'lil', 'young', 'big', 'notorious'
            ],
            'EDM': [
                'edm', 'electronic', 'dance music', 'house', 'techno', 'trance',
                'dubstep', 'drum and bass', 'ambient', 'synthwave', 'electro',
                'calvin harris', 'david guetta', 'tiësto', 'armin van buuren',
                'deadmau5', 'skrillex', 'diplo', 'marshmello', 'dj', 'producer'
            ],
            'INDIE': [
                'indie', 'independent', 'alternative', 'alt rock', 'indie rock',
                'indie pop', 'indie folk', 'underground', 'lo-fi', 'bedroom pop',
                'arctic monkeys', 'vampire weekend', 'tame impala', 'the strokes',
                'radiohead', 'modest mouse', 'death cab', 'indie label'
            ],
            'POP': [
                'pop', 'mainstream', 'chart topper', 'billboard', 'top 40',
                'taylor swift', 'ariana grande', 'billie eilish', 'dua lipa',
                'olivia rodrigo', 'harry styles', 'the weeknd', 'bruno mars',
                'ed sheeran', 'adele', 'beyoncé', 'rihanna', 'justin bieber'
            ]
        }
        
        # 음악 업계 키워드 (우선순위)
        self.industry_keywords = {
            'LABEL': [
                'record label', 'music label', 'signs to', 'signed with', 'deal with',
                'universal music', 'sony music', 'warner music', 'atlantic records',
                'columbia records', 'rca records', 'def jam', 'interscope',
                'republic records', 'capitol records', 'label deal', 'recording contract'
            ],
            'PUBLISHING': [
                'music publishing', 'songwriter', 'publishing deal', 'royalties',
                'mechanical rights', 'performance rights', 'sync rights',
                'ascap', 'bmi', 'sesac', 'prs', 'socan', 'publishing company',
                'music publisher', 'catalog', 'composition', 'copyright'
            ],
            'STREAMING': [
                'spotify', 'apple music', 'youtube music', 'amazon music',
                'tidal', 'deezer', 'pandora', 'streaming', 'playlist',
                'streams', 'monthly listeners', 'digital sales', 'downloads',
                'streaming platform', 'music streaming', 'subscription'
            ],
            'AI-MUSIC': [
                'artificial intelligence', 'ai music', 'machine learning',
                'algorithm', 'ai-generated', 'automated', 'neural network',
                'deep learning', 'music ai', 'ai composer', 'ai producer',
                'generative music', 'music technology', 'ai tools'
            ],
            'SYNCH': [
                'sync', 'synchronization', 'film music', 'tv music', 'commercial music',
                'soundtrack', 'score', 'music supervisor', 'placement',
                'advertising music', 'brand music', 'sync licensing',
                'music for media', 'composer', 'film score'
            ],
            'A&R': [
                'a&r', 'talent scout', 'artist development', 'artist relations',
                'repertoire', 'scouting', 'artist discovery', 'talent acquisition',
                'music executive', 'artist manager', 'talent management'
            ],
            'RIGHTS': [
                'music rights', 'copyright', 'licensing', 'legal', 'lawsuit',
                'settlement', 'infringement', 'plagiarism', 'royalty dispute',
                'music law', 'intellectual property', 'rights management',
                'legal battle', 'court case', 'music litigation'
            ],
            'STARTUP': [
                'startup', 'music tech', 'fintech', 'investment', 'funding',
                'venture capital', 'series a', 'series b', 'ipo', 'acquisition',
                'merger', 'music technology', 'innovation', 'disrupt',
                'entrepreneur', 'music business', 'new platform'
            ]
        }
        
        # 지역 키워드 (장르/업계 태그가 없을 때만 사용)
        self.region_keywords = {
            'USA': ['usa', 'america', 'american', 'us', 'united states', 'new york', 'los angeles', 'nashville', 'atlanta'],
            'UK': ['uk', 'britain', 'british', 'england', 'london', 'manchester', 'liverpool'],
            'KOREA': ['korea', 'korean', 'seoul', 'busan', 'k-pop', 'kpop'],
            'JAPAN': ['japan', 'japanese', 'tokyo', 'osaka', 'j-pop', 'jpop'],
            'EUROPE': ['europe', 'european', 'germany', 'france', 'italy', 'spain', 'netherlands'],
            'GLOBAL': ['global', 'worldwide', 'international', 'world', 'universal']
        }
    
    def classify_category(self, title: str, description: str) -> str:
        """카테고리 분류"""
        text = f"{title} {description}".lower()
        
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return 'NEWS'  # 기본값
    
    def extract_tags(self, title: str, description: str, url: str) -> Dict[str, List[str]]: # link -> url
        """태그 추출 (장르/업계 우선, 없으면 지역)"""
        text = f"{title} {description} {url}".lower() # link -> url
        
        # 장르 태그 추출
        genre_tags = []
        for genre, keywords in self.genre_keywords.items():
            if any(keyword.lower() in text for keyword in keywords):
                genre_tags.append(genre)
        
        # 업계 태그 추출
        industry_tags = []
        for industry, keywords in self.industry_keywords.items():
            if any(keyword.lower() in text for keyword in keywords):
                industry_tags.append(industry)
        
        # 지역 태그 (장르나 업계 태그가 없을 때만)
        region_tags = []
        if not genre_tags and not industry_tags:
            for region, keywords in self.region_keywords.items():
                if any(keyword.lower() in text for keyword in keywords):
                    region_tags.append(region)
        
        return {
            'genre': genre_tags,
            'industry': industry_tags,
            'region': region_tags
        }
    
    def generate_5w1h_summary(self, title: str, description: str, url: str) -> str: # link -> url
        """5W1H 기반 상세 요약 생성"""
        try:
            # 기본 정보 추출
            text = f"{title} {description}".lower()
            
            # Who 추출 (아티스트, 인물명)
            who_patterns = [
                r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',  # 이름 패턴 (두 단어)
                r'\b([A-Z][a-z]+)\b(?=\s+(?:announces|releases|says|reveals|signs|drops))',  # 동작 앞의 이름 (한 단어)
            ]
            
            who_matches = []
            for pattern in who_patterns:
                matches = re.findall(pattern, title + " " + description)
                who_matches.extend(matches)
            
            # 중복 제거 및 정리
            who_list = list(set([name for name in who_matches if len(name) > 2]))[:3]
            who_text = ", ".join(who_list) if who_list else "Music industry figures"
            
            # What 추출 (주요 행동/사건)
            what_keywords = {
                'announced or released a new album': ['album', 'new album', 'debut album', 'studio album'],
                'announced or released a new single': ['single', 'new song', 'track', 'new single'],
                'announced or is planning a tour': ['tour', 'concert', 'live show', 'performance'],
                'entered into a collaboration': ['collaboration', 'featuring', 'duet', 'team up'],
                'signed a business deal': ['signs', 'deal', 'contract', 'agreement'],
                'involved in a legal issue': ['lawsuit', 'legal', 'court', 'settlement'],
                'made significant industry news': ['industry', 'market', 'business', 'company', 'report', 'analysis']
            }
            
            what_text = "made an announcement"
            for action, keywords in what_keywords.items():
                if any(keyword in text for keyword in keywords):
                    what_text = action
                    break
            
            # When 추출
            when_patterns = [
                r'\b(today|yesterday|this week|next week|this month|next month|recently)\b',
                r'\b(202[0-9])\b', # 2020년대 연도
                r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b'
            ]
            
            when_matches = []
            for pattern in when_patterns:
                matches = re.findall(pattern, text)
                when_matches.extend(matches)
            
            when_text = when_matches[0] if when_matches else "recently"
            
            # Where 추출
            where_keywords = {
                'USA': ['america', 'us', 'united states', 'new york', 'los angeles', 'nashville'],
                'UK': ['britain', 'uk', 'london', 'england'],
                'South Korea': ['korea', 'seoul', 'k-pop'],
                'Japan': ['japan', 'tokyo'],
                'Europe': ['europe', 'germany', 'france'],
                'globally': ['worldwide', 'global', 'international']
            }
            
            where_text = "in the music industry"
            for location, keywords in where_keywords.items():
                if any(keyword in text for keyword in keywords):
                    where_text = f"in {location}"
                    break
            
            # Why/How 추출 (맥락)
            context_keywords = {
                'new music releases': ['new music', 'creative', 'artistic', 'song', 'album', 'single'],
                'business developments': ['business', 'commercial', 'financial', 'deal', 'investment'],
                'touring and live events': ['tour', 'concert', 'festival', 'performance'],
                'industry changes': ['industry', 'market', 'trend', 'innovation', 'technology']
            }
            
            context_text = "related to their music career"
            for context, keywords in context_keywords.items():
                if any(keyword in text for keyword in keywords):
                    context_text = f"related to {context}"
                    break
            
            # 완전한 문장으로 조합
            summary = f"{who_text} {what_text} {when_text}. The event occurred {where_text}, {context_text}."
            
            # 문장 정리
            summary = re.sub(r'\s+', ' ', summary).strip()
            
            return summary
            
        except Exception as e:
            logger.error(f"5W1H 요약 생성 오류: {e}")
            return f"Music industry news about {title.split()[0] if title else 'various artists'} and their recent activities."
    
    def calculate_importance_score(self, title: str, description: str, tags: Dict) -> float:
        """중요도 점수 계산"""
        score = 0.5  # 기본 점수
        
        text = f"{title} {description}".lower()
        
        # 고중요도 키워드
        high_importance = ['breaking', 'exclusive', 'major', 'significant', 'historic', 'record-breaking']
        score += sum(0.1 for keyword in high_importance if keyword in text)
        
        # 아티스트 인지도 (간접 추정)
        famous_artists = ['taylor swift', 'drake', 'bts', 'blackpink', 'ariana grande', 'ed sheeran', 'billie eilish', 'the weeknd']
        score += sum(0.2 for artist in famous_artists if artist in text)
        
        # 태그 다양성
        total_tags = len(tags.get('genre', [])) + len(tags.get('industry', [])) + len(tags.get('region', []))
        score += min(total_tags * 0.1, 0.3) # 최대 0.3점 추가
        
        return min(score, 1.0) # 점수는 1.0을 넘지 않도록
    
    def process_news_list(self, news_list: List[Dict]) -> List[Dict]:
        """뉴스 리스트 처리"""
        processed_news = []
        
        for news in news_list:
            try:
                title = news.get('title', '')
                description = news.get('description', '')
                url = news.get('url', '') # <--- news.get('link', '') -> news.get('url', '')
                
                # 카테고리 분류
                category = self.classify_category(title, description)
                
                # 태그 추출
                tags = self.extract_tags(title, description, url) # url 전달
                
                # 5W1H 요약 생성
                summary = self.generate_5w1h_summary(title, description, url) # url 전달
                
                # 중요도 점수 계산
                importance_score = self.calculate_importance_score(title, description, tags)
                
                # 처리된 뉴스 항목 생성
                processed_item = {
                    **news,  # 기존 정보 유지
                    'category': category,
                    'tags': tags,
                    'summary': summary, # <--- summary 필드에 요약 저장
                    'importance_score': importance_score
                }
                
                processed_news.append(processed_item)
                
            except Exception as e:
                logger.error(f"뉴스 처리 오류: {e} - 뉴스: {news.get('title', '제목 없음')}")
                # 오류 발생 시 기본값으로 처리
                processed_news.append({
                    **news,
                    'category': 'NEWS',
                    'tags': {'genre': [], 'industry': [], 'region': []},
                    'summary': '뉴스 처리 중 오류가 발생했습니다. 자세한 내용을 확인해주세요.',
                    'importance_score': 0.5
                })
        
        logger.info(f"{len(processed_news)}개 뉴스 처리 완료")
        return processed_news
    
    def select_top_news_by_category(self, news_list: List[Dict], max_per_category: int = 4) -> List[Dict]:
        """카테고리별 상위 뉴스 선별"""
        
        # 카테고리별로 그룹화
        categorized_news = {}
        for news in news_list:
            category = news.get('category', 'NEWS')
            if category not in categorized_news:
                categorized_news[category] = []
            categorized_news[category].append(news)
        
        selected_news = []
        
        # 각 카테고리에서 상위 뉴스 선별
        for category, news_items in categorized_news.items():
            # 중요도 점수로 정렬
            sorted_news = sorted(news_items, key=lambda x: x.get('importance_score', 0), reverse=True)
            
            # 상위 N개 선택
            top_news = sorted_news[:max_per_category]
            selected_news.extend(top_news)
            
            logger.info(f"{category} 카테고리: {len(news_items)}개 중 {len(top_news)}개 선별}")
        
        logger.info(f"총 {len(selected_news)}개 뉴스 선별 완료")
        return selected_news

if __name__ == "__main__":
    # 테스트용 샘플 뉴스
    sample_news = [
        {
            'title': 'Taylor Swift Announces New Album "Midnight Stories"',
            'description': 'Pop superstar Taylor Swift revealed her upcoming album during a surprise announcement, featuring collaborations with indie artists.',
            'url': 'https://example.com/taylor-swift-album', # link -> url
            'source': 'billboard.com',
            'published_date': '2025-06-26 10:00:00' # 날짜 형식 일치
        },
        {
            'title': 'BTS Signs Major Publishing Deal with Universal Music',
            'description': 'The K-pop group BTS has signed a groundbreaking publishing agreement with Universal Music Group, expanding their global reach.',
            'url': 'https://example.com/bts-deal', # link -> url
            'source': 'variety.com',
            'published_date': '2025-06-26 11:30:00' # 날짜 형식 일치
        },
        {
            'title': 'New AI Music Startup Raises $10M in Seed Funding',
            'description': 'A new AI-powered music creation platform secured significant investment to develop its generative music algorithms.',
            'url': 'https://example.com/ai-startup',
            'source': 'techcrunch.com',
            'published_date': '2025-06-25 15:00:00'
        },
        {
            'title': 'Indie Artist "The Lumineers" Announce Fall Tour Dates',
            'description': 'Folk-rock band The Lumineers will embark on a North American tour this fall, with tickets going on sale next week.',
            'url': 'https://example.com/lumineers-tour',
            'source': 'consequence.net',
            'published_date': '2025-06-24 09:00:00'
        }
    ]
    
    # 분류기 테스트
    classifier = AdvancedClassifier( )
    processed = classifier.process_news_list(sample_news)
    
    print("=== 처리된 뉴스 결과 ===")
    for i, news in enumerate(processed, 1):
        print(f"\n{i}. {news['title']}")
        print(f"   카테고리: {news['category']}")
        print(f"   태그: {news['tags']}")
        print(f"   요약: {news['summary']}") # <--- summary 필드 출력
        print(f"   중요도: {news['importance_score']:.2f}")

    # 상위 뉴스 선별 테스트
    selected = classifier.select_top_news_by_category(processed, max_per_category=2)
    print("\n=== 선별된 상위 뉴스 ===")
    for i, news in enumerate(selected, 1):
        print(f"\n{i}. {news['title']}")
        print(f"   카테고리: {news['category']}")
        print(f"   요약: {news['summary']}")
        print(f"   중요도: {news['importance_score']:.2f}")
