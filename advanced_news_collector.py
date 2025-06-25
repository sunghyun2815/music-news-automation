#!/usr/bin/env python3
"""
Advanced News Classifier
카테고리 분류, 태깅, 5W1H 요약 시스템
"""

import re
import logging
from typing import List, Dict, Set
from collections import Counter

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedClassifier:
    def __init__(self):
        # 카테고리 분류 키워드
        self.category_keywords = {
            'NEWS': [
                'announced', 'reveals', 'confirms', 'breaking', 'just in', 'reports',
                'new album', 'new song', 'tour dates', 'concert', 'festival',
                'collaboration', 'featuring', 'drops', 'releases'
            ],
            'REPORT': [
                'analysis', 'study', 'research', 'data', 'statistics', 'numbers',
                'market', 'industry', 'trends', 'growth', 'decline', 'revenue',
                'streaming', 'sales', 'chart', 'billboard'
            ],
            'INSIGHT': [
                'opinion', 'perspective', 'think', 'believe', 'future', 'prediction',
                'trend', 'evolution', 'change', 'impact', 'influence', 'effect',
                'why', 'how', 'what this means', 'significance'
            ],
            'INTERVIEW': [
                'interview', 'talks', 'speaks', 'says', 'tells', 'discusses',
                'conversation', 'chat', 'Q&A', 'exclusive', 'sits down',
                'opens up', 'reveals in interview'
            ],
            'COLUMN': [
                'column', 'editorial', 'commentary', 'op-ed', 'opinion piece',
                'personal view', 'my take', 'thoughts on', 'reflection'
            ]
        }
        
        # 장르 태그
        self.genre_tags = [
            'pop', 'rock', 'hip-hop', 'rap', 'r&b', 'country', 'jazz', 'classical',
            'electronic', 'edm', 'folk', 'indie', 'alternative', 'metal', 'punk',
            'reggae', 'blues', 'soul', 'funk', 'disco', 'house', 'techno',
            'k-pop', 'latin', 'world music', 'ambient', 'experimental'
        ]
        
        # 업계 태그
        self.industry_tags = [
            'tour', 'concert', 'festival', 'album', 'single', 'EP', 'record label',
            'streaming', 'spotify', 'apple music', 'youtube', 'tiktok',
            'billboard', 'grammy', 'award', 'nomination', 'chart', 'sales',
            'collaboration', 'featuring', 'remix', 'cover', 'live performance',
            'music video', 'documentary', 'biopic', 'soundtrack'
        ]
        
        # 지역 태그
        self.region_tags = [
            'us', 'usa', 'america', 'american', 'uk', 'british', 'europe', 'european',
            'korea', 'korean', 'k-pop', 'japan', 'japanese', 'china', 'chinese',
            'canada', 'canadian', 'australia', 'australian', 'latin', 'latino',
            'africa', 'african', 'india', 'indian', 'global', 'international'
        ]
    
    def classify_category(self, news_item: Dict) -> str:
        """뉴스 카테고리 분류"""
        title = news_item.get('title', '').lower()
        description = news_item.get('description', '').lower()
        content = news_item.get('content', '').lower()
        
        text = f"{title} {description} {content}"
        
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            category_scores[category] = score
        
        # 가장 높은 점수의 카테고리 반환
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        # 기본값은 NEWS
        return 'NEWS'
    
    def extract_tags(self, news_item: Dict) -> Dict[str, List[str]]:
        """태그 추출 (장르, 업계, 지역)"""
        title = news_item.get('title', '').lower()
        description = news_item.get('description', '').lower()
        content = news_item.get('content', '').lower()
        
        text = f"{title} {description} {content}"
        
        tags = {
            'genre': [],
            'industry': [],
            'region': []
        }
        
        # 장르 태그 추출
        for genre in self.genre_tags:
            if genre in text:
                tags['genre'].append(genre)
        
        # 업계 태그 추출
        for industry in self.industry_tags:
            if industry in text:
                tags['industry'].append(industry)
        
        # 지역 태그 추출
        for region in self.region_tags:
            if region in text:
                tags['region'].append(region)
        
        # 중복 제거 및 상위 3개만 유지
        for tag_type in tags:
            tags[tag_type] = list(set(tags[tag_type]))[:3]
        
        return tags
    
    def generate_5w1h_summary(self, news_item: Dict) -> str:
        """5W1H 기반 상세 요약 생성 (스토리텔링 방식)"""
        title = news_item.get('title', '')
        description = news_item.get('description', '')
        content = news_item.get('content', '')
        
        # 전체 텍스트 결합
        full_text = f"{title}. {description}. {content}"
        text_lower = full_text.lower()
        
        # 주요 인물/아티스트 추출
        who_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:announced|released|performed|said|revealed|confirmed)',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:will|has|is|was)',
            r'(?:singer|artist|musician|band|rapper|producer)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:tour|album|song|concert)'
        ]
        
        who_found = set()
        for pattern in who_patterns:
            matches = re.findall(pattern, title + ". " + description)
            for match in matches[:3]:
                if len(match.split()) <= 3 and match not in ['The', 'A', 'An', 'This', 'That', 'New', 'Big']:
                    who_found.add(match)
        
        # 주요 사건/활동 추출
        what_keywords = {
            'tour': ['tour', 'concert', 'show', 'performance', 'live'],
            'album': ['album', 'record', 'release', 'debut', 'EP'],
            'collaboration': ['featuring', 'collaboration', 'duet', 'with'],
            'award': ['award', 'nomination', 'winner', 'grammy', 'billboard'],
            'announcement': ['announced', 'revealed', 'confirmed', 'statement'],
            'controversy': ['controversy', 'scandal', 'criticism', 'backlash'],
            'death': ['died', 'death', 'passed away', 'killed', 'tragic'],
            'business': ['deal', 'contract', 'signed', 'partnership', 'acquisition'],
            'new_music': ['new song', 'single', 'track', 'music video']
        }
        
        what_found = []
        for category, keywords in what_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    what_found.append(category)
                    break
        
        # 시간 정보 추출
        when_patterns = [
            r'\b(this\s+(?:week|month|year|summer|fall|winter|spring))\b',
            r'\b(next\s+(?:week|month|year|summer|fall|winter|spring))\b',
            r'\b(recently|today|yesterday|soon|upcoming)\b',
            r'\b(2024|2025)\b'
        ]
        
        when_found = []
        for pattern in when_patterns:
            matches = re.findall(pattern, text_lower)
            when_found.extend(matches[:2])
        
        # 장소 정보 추출
        where_patterns = [
            r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\bat\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\b(North America|South Korea|United States|UK|Europe|Asia|Australia)\b',
            r'\b([A-Z][a-z]+)\s+(?:Stadium|Arena|Theater|Hall|Festival)\b'
        ]
        
        where_found = set()
        for pattern in where_patterns:
            matches = re.findall(pattern, title + ". " + description, re.IGNORECASE)
            for match in matches[:3]:
                if isinstance(match, str) and len(match.split()) <= 3:
                    where_found.add(match)
        
        # 스토리텔링 방식의 요약 생성
        summary_parts = []
        
        # 주인물과 주요 사건 결합
        if who_found and what_found:
            main_who = list(who_found)[0]
            main_what = what_found[0]
            
            if main_what == 'tour':
                summary_parts.append(f"{main_who} announced or is planning a tour")
            elif main_what == 'album':
                summary_parts.append(f"{main_who} released or announced a new album")
            elif main_what == 'new_music':
                summary_parts.append(f"{main_who} dropped new music")
            elif main_what == 'collaboration':
                summary_parts.append(f"{main_who} collaborated with other artists")
            elif main_what == 'award':
                summary_parts.append(f"{main_who} received recognition or awards")
            elif main_what == 'controversy':
                summary_parts.append(f"{main_who} is involved in a controversial situation")
            elif main_what == 'death':
                summary_parts.append(f"Tragic news emerged about {main_who}")
            elif main_what == 'business':
                summary_parts.append(f"{main_who} made a significant business announcement")
            else:
                summary_parts.append(f"{main_who} made headlines in the music industry")
        elif who_found:
            main_who = list(who_found)[0]
            summary_parts.append(f"{main_who} is featured in music industry news")
        elif what_found:
            main_what = what_found[0]
            summary_parts.append(f"Music industry news about {main_what}")
        
        # 시간 정보 추가
        if when_found:
            time_info = when_found[0]
            if summary_parts:
                summary_parts.append(f"The event occurred or was announced {time_info}")
            else:
                summary_parts.append(f"This music news happened {time_info}")
        
        # 장소 정보 추가
        if where_found:
            location = list(where_found)[0]
            summary_parts.append(f"The event is taking place in {location}")
        
        # 추가 컨텍스트
        context_added = False
        if 'new song' in text_lower or 'single' in text_lower:
            summary_parts.append("involving new music releases")
            context_added = True
        
        if 'fan' in text_lower or 'audience' in text_lower and not context_added:
            summary_parts.append("generating significant fan interest")
        
        # 최종 요약 문장 생성
        if summary_parts:
            # 문장들을 자연스럽게 연결
            if len(summary_parts) == 1:
                final_summary = summary_parts[0] + "."
            elif len(summary_parts) == 2:
                final_summary = summary_parts[0] + ". " + summary_parts[1] + "."
            else:
                final_summary = summary_parts[0] + ". " + summary_parts[1] + ", " + " ".join(summary_parts[2:]) + "."
            
            # 첫 글자 대문자로 변경
            final_summary = final_summary[0].upper() + final_summary[1:] if final_summary else ""
            
            # 문장 정리
            final_summary = re.sub(r'\s+', ' ', final_summary)
            final_summary = re.sub(r'\.+', '.', final_summary)
            
            return final_summary
        
        # 기본 요약 (5W1H 정보가 부족한 경우)
        return f"Music industry news about {title[:100]}{'...' if len(title) > 100 else ''}."
    
    def calculate_importance_score(self, news_item: Dict) -> float:
        """뉴스 중요도 점수 계산"""
        score = 0
        
        # 기본 관련성 점수
        title = news_item.get('title', '').lower()
        description = news_item.get('description', '').lower()
        
        # 고중요도 키워드
        high_importance = ['breaking', 'exclusive', 'first', 'major', 'big', 'huge', 'massive']
        for keyword in high_importance:
            if keyword in title:
                score += 0.3
            elif keyword in description:
                score += 0.1
        
        # 아티스트 인지도 (간접 측정)
        artist_indicators = ['grammy', 'billboard', 'platinum', 'million', 'chart', 'number one']
        for indicator in artist_indicators:
            if indicator in title or indicator in description:
                score += 0.2
        
        # 활동 유형별 점수
        activity_scores = {
            'tour': 0.8, 'album': 0.9, 'collaboration': 0.7, 'award': 0.8,
            'controversy': 0.6, 'death': 1.0, 'business': 0.5
        }
        
        for activity, activity_score in activity_scores.items():
            if activity in title or activity in description:
                score += activity_score
                break
        
        # 기본 점수 보정
        score = max(0.1, min(1.0, score))
        
        return round(score, 2)
    
    def process_news_list(self, news_list: List[Dict]) -> List[Dict]:
        """뉴스 리스트 전체 처리"""
        processed_news = []
        
        for news_item in news_list:
            try:
                # 카테고리 분류
                category = self.classify_category(news_item)
                
                # 태그 추출
                tags = self.extract_tags(news_item)
                
                # 5W1H 요약 생성
                summary = self.generate_5w1h_summary(news_item)
                
                # 중요도 점수 계산
                importance_score = self.calculate_importance_score(news_item)
                
                # 결과 추가
                processed_item = news_item.copy()
                processed_item.update({
                    'category': category,
                    'tags': tags,
                    'summary': summary,
                    'importance_score': importance_score
                })
                
                processed_news.append(processed_item)
                
            except Exception as e:
                logger.error(f"뉴스 처리 중 오류: {e}")
                continue
        
        logger.info(f"{len(processed_news)}개 뉴스 처리 완료")
        return processed_news
    
    def select_top_news_by_category(self, processed_news: List[Dict], per_category: int = 4) -> List[Dict]:
        """카테고리별 상위 뉴스 선별"""
        category_news = {}
        
        # 카테고리별로 분류
        for news in processed_news:
            category = news.get('category', 'NEWS')
            if category not in category_news:
                category_news[category] = []
            category_news[category].append(news)
        
        # 각 카테고리에서 상위 뉴스 선별
        selected_news = []
        for category, news_list in category_news.items():
            # 중요도 점수로 정렬
            sorted_news = sorted(news_list, key=lambda x: x.get('importance_score', 0), reverse=True)
            
            # 상위 N개 선택
            top_news = sorted_news[:per_category]
            selected_news.extend(top_news)
            
            logger.info(f"{category} 카테고리: {len(news_list)}개 중 {len(top_news)}개 선별")
        
        return selected_news

if __name__ == "__main__":
    # 테스트 코드
    classifier = AdvancedClassifier()
    
    test_news = {
        'title': 'Taylor Swift Announces New Album Release',
        'description': 'Pop superstar Taylor Swift revealed her upcoming album during a recent interview.',
        'content': 'The Grammy-winning artist will release her new album this fall.'
    }
    
    category = classifier.classify_category(test_news)
    tags = classifier.extract_tags(test_news)
    summary = classifier.generate_5w1h_summary(test_news)
    score = classifier.calculate_importance_score(test_news)
    
    print(f"Category: {category}")
    print(f"Tags: {tags}")
    print(f"Summary: {summary}")
    print(f"Score: {score}")

