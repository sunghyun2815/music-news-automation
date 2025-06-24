#!/usr/bin/env python3
"""
Advanced Classifier
카테고리 분류(NEWS/REPORT/INSIGHT/INTERVIEW/COLUMN) 및 태깅(장르/업계/지역) 모듈
"""

import re
import logging
from typing import Dict, List, Set, Tuple
from collections import Counter

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedClassifier:
    def __init__(self):
        # 카테고리 분류를 위한 키워드
        self.category_keywords = {
            'NEWS': {
                'keywords': ['breaking', 'announces', 'releases', 'debuts', 'launches', 'drops', 
                           'premieres', 'reveals', 'confirms', 'signs', 'joins', 'leaves', 
                           'cancels', 'postpones', 'reschedules', 'dies', 'passes away'],
                'patterns': [r'\b(just|now|today|yesterday|this week)\b', r'\b(new|latest|upcoming)\b']
            },
            'REPORT': {
                'keywords': ['report', 'analysis', 'study', 'research', 'data', 'statistics', 
                           'numbers', 'sales', 'charts', 'streaming', 'revenue', 'market',
                           'industry', 'trends', 'growth', 'decline'],
                'patterns': [r'\b\d+%\b', r'\bmillion|billion\b', r'\baccording to\b']
            },
            'INSIGHT': {
                'keywords': ['opinion', 'perspective', 'analysis', 'commentary', 'think piece',
                           'deep dive', 'exploration', 'examination', 'investigation', 'behind',
                           'why', 'how', 'what makes', 'understanding', 'meaning'],
                'patterns': [r'\bwhy\s+\w+', r'\bhow\s+\w+', r'\bwhat\s+(makes|is)\b']
            },
            'INTERVIEW': {
                'keywords': ['interview', 'talks', 'speaks', 'discusses', 'conversation', 
                           'chat', 'q&a', 'asks', 'tells', 'explains', 'shares', 'opens up'],
                'patterns': [r'\btalks?\s+(about|with)\b', r'\bspeaks?\s+(about|with)\b', 
                           r'\bin\s+conversation\b', r'\bsits\s+down\s+with\b']
            },
            'COLUMN': {
                'keywords': ['column', 'editorial', 'opinion piece', 'commentary', 'blog',
                           'thoughts', 'reflections', 'musings', 'take on', 'view on'],
                'patterns': [r'\bmy\s+(take|view|opinion)\b', r'\bi\s+(think|believe)\b']
            }
        }
        
        # 장르 태그
        self.genre_tags = {
            'rock', 'pop', 'hip hop', 'rap', 'jazz', 'classical', 'electronic', 'edm',
            'country', 'folk', 'blues', 'metal', 'punk', 'indie', 'alternative', 'r&b',
            'soul', 'funk', 'reggae', 'latin', 'world music', 'ambient', 'house',
            'techno', 'dubstep', 'trap', 'drill', 'afrobeat', 'k-pop', 'j-pop'
        }
        
        # 업계 태그
        self.industry_tags = {
            'streaming', 'record label', 'music industry', 'concert', 'festival', 'tour',
            'venue', 'booking', 'management', 'publishing', 'royalties', 'licensing',
            'sync', 'playlist', 'radio', 'podcast', 'vinyl', 'cd', 'digital', 'nft',
            'blockchain', 'ai music', 'music tech', 'startup', 'investment', 'merger',
            'acquisition', 'ipo', 'revenue', 'sales', 'charts', 'billboard', 'grammy',
            'award', 'nomination', 'collaboration', 'remix', 'cover', 'sample'
        }
        
        # 지역 태그
        self.region_tags = {
            'us', 'usa', 'america', 'american', 'uk', 'britain', 'british', 'europe',
            'european', 'asia', 'asian', 'korea', 'korean', 'japan', 'japanese',
            'china', 'chinese', 'india', 'indian', 'africa', 'african', 'latin america',
            'south america', 'australia', 'canadian', 'mexico', 'brazilian', 'german',
            'french', 'italian', 'spanish', 'nordic', 'scandinavian', 'global', 'worldwide'
        }
    
    def classify_category(self, title: str, description: str) -> str:
        """뉴스 카테고리 분류"""
        text = (title + " " + description).lower()
        
        category_scores = {}
        
        for category, criteria in self.category_keywords.items():
            score = 0
            
            # 키워드 매칭
            for keyword in criteria['keywords']:
                if keyword in text:
                    score += 1
            
            # 패턴 매칭
            for pattern in criteria['patterns']:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches * 0.5
            
            category_scores[category] = score
        
        # 가장 높은 점수의 카테고리 반환
        if max(category_scores.values()) > 0:
            return max(category_scores, key=category_scores.get)
        else:
            return 'NEWS'  # 기본값
    
    def extract_tags(self, title: str, description: str) -> Dict[str, List[str]]:
        """장르/업계/지역 태그 추출"""
        text = (title + " " + description).lower()
        
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
        
        return tags
    
    def generate_5w1h_summary(self, title: str, description: str) -> str:
        """5W1H 영어 요약 생성"""
        # 간단한 5W1H 요약 생성 (실제로는 더 정교한 NLP 모델 사용 가능)
        
        # Who: 주요 인물/아티스트 추출
        who_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # 대문자로 시작하는 이름
        ]
        
        who_matches = []
        for pattern in who_patterns:
            matches = re.findall(pattern, title + " " + description)
            who_matches.extend(matches[:3])  # 최대 3개
        
        # What: 주요 행동/사건
        what_keywords = ['releases', 'announces', 'performs', 'collaborates', 'signs', 'debuts']
        what_found = []
        text_lower = (title + " " + description).lower()
        
        for keyword in what_keywords:
            if keyword in text_lower:
                what_found.append(keyword)
        
        # When: 시간 정보
        when_patterns = [
            r'\b(today|yesterday|this week|next week|this month|next month|\d{4})\b',
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b'
        ]
        
        when_matches = []
        for pattern in when_patterns:
            matches = re.findall(pattern, text_lower)
            when_matches.extend(matches[:2])
        
        # Where: 장소 정보
        where_patterns = [
            r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\bat\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        ]
        
        where_matches = []
        for pattern in where_patterns:
            matches = re.findall(pattern, title + " " + description)
            where_matches.extend(matches[:2])
        
        # 요약 생성
        summary_parts = []
        
        if who_matches:
            summary_parts.append(f"Who: {', '.join(who_matches[:2])}")
        
        if what_found:
            summary_parts.append(f"What: {', '.join(what_found[:2])}")
        
        if when_matches:
            summary_parts.append(f"When: {', '.join(when_matches[:2])}")
        
        if where_matches:
            summary_parts.append(f"Where: {', '.join(where_matches[:2])}")
        
        # 기본 요약이 없으면 제목 기반으로 생성
        if not summary_parts:
            summary_parts.append(f"Summary: {title[:100]}...")
        
        return " | ".join(summary_parts)
    
    def calculate_importance_score(self, news_item: Dict) -> float:
        """뉴스 중요도 점수 계산"""
        score = 0
        
        # 기본 관련성 점수
        score += news_item.get('relevance_score', 0) * 0.3
        
        # 소스 신뢰도
        source_scores = {
            'www.billboard.com': 0.9,
            'pitchfork.com': 0.85,
            'www.rollingstone.com': 0.9,
            'www.musicbusinessworldwide.com': 0.8,
            'variety.com': 0.85,
            'www.nme.com': 0.75,
            'consequenceofsound.net': 0.7,
            'www.stereogum.com': 0.75
        }
        
        source_score = source_scores.get(news_item.get('source', ''), 0.5)
        score += source_score * 0.3
        
        # 태그 다양성 (더 많은 태그 = 더 중요)
        tags = news_item.get('tags', {})
        tag_count = sum(len(tag_list) for tag_list in tags.values())
        tag_score = min(tag_count / 5, 1.0)  # 최대 5개 태그로 정규화
        score += tag_score * 0.2
        
        # 카테고리별 가중치
        category_weights = {
            'NEWS': 1.0,
            'REPORT': 0.9,
            'INSIGHT': 0.8,
            'INTERVIEW': 0.85,
            'COLUMN': 0.7
        }
        
        category = news_item.get('category', 'NEWS')
        score += category_weights.get(category, 1.0) * 0.2
        
        return min(score, 1.0)  # 최대 1.0으로 제한
    
    def process_news_item(self, news_item: Dict) -> Dict:
        """뉴스 항목 처리 (분류, 태깅, 요약)"""
        title = news_item.get('title', '')
        description = news_item.get('description', '')
        
        # 카테고리 분류
        category = self.classify_category(title, description)
        
        # 태그 추출
        tags = self.extract_tags(title, description)
        
        # 5W1H 요약 생성
        summary = self.generate_5w1h_summary(title, description)
        
        # 처리된 뉴스 항목 생성
        processed_item = news_item.copy()
        processed_item.update({
            'category': category,
            'tags': tags,
            'summary_5w1h': summary
        })
        
        # 중요도 점수 계산
        processed_item['importance_score'] = self.calculate_importance_score(processed_item)
        
        return processed_item
    
    def process_news_list(self, news_list: List[Dict]) -> List[Dict]:
        """뉴스 목록 처리"""
        processed_news = []
        
        for news_item in news_list:
            try:
                processed_item = self.process_news_item(news_item)
                processed_news.append(processed_item)
            except Exception as e:
                logger.error(f"뉴스 처리 오류: {e}")
                continue
        
        logger.info(f"{len(processed_news)}개 뉴스 처리 완료")
        return processed_news
    
    def select_top_news_by_category(self, news_list: List[Dict], per_category: int = 4) -> List[Dict]:
        """카테고리별 상위 뉴스 선별"""
        # 카테고리별로 그룹화
        categorized_news = {}
        for news in news_list:
            category = news.get('category', 'NEWS')
            if category not in categorized_news:
                categorized_news[category] = []
            categorized_news[category].append(news)
        
        # 각 카테고리에서 중요도 순으로 정렬하고 상위 선별
        selected_news = []
        for category, news_items in categorized_news.items():
            # 중요도 점수로 정렬
            sorted_news = sorted(news_items, key=lambda x: x.get('importance_score', 0), reverse=True)
            
            # 상위 N개 선별
            top_news = sorted_news[:per_category]
            selected_news.extend(top_news)
            
            logger.info(f"{category} 카테고리: {len(news_items)}개 중 {len(top_news)}개 선별")
        
        # 전체적으로 중요도 순으로 재정렬
        selected_news.sort(key=lambda x: x.get('importance_score', 0), reverse=True)
        
        logger.info(f"총 {len(selected_news)}개 뉴스 선별 완료")
        return selected_news

if __name__ == "__main__":
    # 테스트용 샘플 뉴스
    sample_news = [
        {
            'title': 'Taylor Swift Announces New Album "Midnight Dreams"',
            'description': 'Pop superstar Taylor Swift revealed her upcoming album during a surprise livestream, featuring collaborations with indie artists.',
            'source': 'www.billboard.com',
            'relevance_score': 0.9
        },
        {
            'title': 'Streaming Revenue Hits Record High in 2024',
            'description': 'According to new industry data, music streaming platforms generated $15 billion in revenue this year, marking a 12% increase.',
            'source': 'www.musicbusinessworldwide.com',
            'relevance_score': 0.8
        }
    ]
    
    classifier = AdvancedClassifier()
    processed_news = classifier.process_news_list(sample_news)
    
    for news in processed_news:
        print(f"제목: {news['title']}")
        print(f"카테고리: {news['category']}")
        print(f"태그: {news['tags']}")
        print(f"요약: {news['summary_5w1h']}")
        print(f"중요도: {news['importance_score']:.2f}")
        print("-" * 50)

