#!/usr/bin/env python3
"""
Fixed Advanced Music News Classifier - AI 요약 기능 활성화
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
        
        # AI 요약기 초기화 (Claude 우선)
        if self.use_claude_summary or self.use_ai_summary:
            try:
                from ai_summarizer import AISummarizer
                self.ai_summarizer = AISummarizer()
                logger.info("✅ Claude AI 요약기 초기화 완료")
            except Exception as e:
                logger.warning(f"⚠️ AI 요약기 초기화 실패: {e}")
                logger.warning("🔄 규칙 기반 요약으로 대체됩니다.")
                self.ai_summarizer = None
        
        # 분류 키워드 정의
        self.category_keywords = {
            'NEWS': [
                'announces', 'releases', 'debuts', 'signs', 'tour', 'concert', 'collaboration',
                'drops', 'unveils', 'shares', 'confirms', 'premieres'
            ],
            'REPORT': [
                'chart', 'sales', 'revenue', 'market', 'statistics', 'data', 'analysis',
                'earnings', 'profits', 'streaming', 'numbers'
            ],
            'INSIGHT': [
                'trend', 'prediction', 'future', 'impact', 'influence', 'change',
                'analysis', 'perspective', 'opinion', 'commentary'
            ],
            'INTERVIEW': [
                'interview', 'talks', 'discusses', 'reveals', 'opens up', 'speaks',
                'conversation', 'chat', 'Q&A'
            ],
            'COLUMN': [
                'opinion', 'column', 'editorial', 'commentary', 'essay', 'perspective',
                'review', 'critique', 'think piece'
            ]
        }
        
        # 태그 키워드
        self.tag_keywords = {
            'genre': {
                'pop': ['pop', 'mainstream', 'chart-topping'],
                'rock': ['rock', 'alternative', 'indie', 'punk'],
                'hip-hop': ['hip-hop', 'rap', 'trap', 'hip hop'],
                'electronic': ['electronic', 'edm', 'dance', 'techno'],
                'country': ['country', 'folk', 'americana'],
                'r&b': ['r&b', 'soul', 'rnb', 'rhythm'],
                'classical': ['classical', 'orchestra', 'symphony'],
                'jazz': ['jazz', 'blues', 'swing'],
                'k-pop': ['k-pop', 'kpop', 'korean pop', 'bts', 'blackpink']
            },
            'industry': {
                'album': ['album', 'lp', 'record', 'ep'],
                'single': ['single', 'track', 'song'],
                'tour': ['tour', 'concert', 'live', 'show', 'performance'],
                'streaming': ['spotify', 'apple music', 'streaming', 'playlist'],
                'award': ['grammy', 'award', 'nomination', 'winner'],
                'collaboration': ['collaboration', 'featuring', 'duet', 'feat'],
                'label': ['label', 'record deal', 'signing', 'contract']
            },
            'region': {
                'us': ['america', 'united states', 'us', 'usa', 'american'],
                'uk': ['britain', 'british', 'uk', 'england', 'london'],
                'korea': ['korea', 'korean', 'seoul', 'k-pop'],
                'japan': ['japan', 'japanese', 'tokyo', 'j-pop'],
                'global': ['global', 'worldwide', 'international', 'world']
            }
        }

    def classify_category(self, title: str, description: str) -> str:
        """카테고리 분류"""
        text = f"{title} {description}".lower()
        
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        return 'NEWS'

    def extract_tags(self, title: str, description: str, url: str = "") -> Dict:
        """태그 추출"""
        text = f"{title} {description} {url}".lower()
        
        tags = {'genre': [], 'industry': [], 'region': []}
        
        for tag_type, categories in self.tag_keywords.items():
            for tag_name, keywords in categories.items():
                if any(keyword in text for keyword in keywords):
                    if tag_name not in tags[tag_type]:
                        tags[tag_type].append(tag_name)
        
        return tags

    def process_news_list_simplified(self, news_list: List[Dict]) -> List[Dict]:
        """뉴스 리스트 처리 - AI 요약 포함된 버전"""
        processed_news = []
        
        # 1단계: 기본 처리 (카테고리, 태그)
        logger.info(f"🏷️ 1단계: 기본 분류 및 태깅 처리 중...")
        for news in news_list:
            try:
                title = news.get('title', '')
                description = news.get('description', '')
                url = news.get('url', news.get('link', ''))
                
                # 카테고리 분류
                category = self.classify_category(title, description)
                
                # 태그 추출
                tags = self.extract_tags(title, description, url)
                
                # 기본 처리된 뉴스 항목
                processed_item = {
                    **news,
                    'category': category,
                    'tags': tags,
                    'summary': '',  # 나중에 추가
                    'summary_type': 'pending'
                }
                
                processed_news.append(processed_item)
                
            except Exception as e:
                logger.error(f"뉴스 기본 처리 오류: {e}")
                processed_news.append({
                    **news,
                    'category': 'NEWS',
                    'tags': {'genre': [], 'industry': [], 'region': []},
                    'summary': f"음악 업계 소식: {news.get('title', '')[:50]}...",
                    'summary_type': 'fallback'
                })
        
        # 2단계: AI 요약 처리
        if (self.use_ai_summary or self.use_claude_summary) and self.ai_summarizer:
            logger.info(f"🤖 2단계: AI 요약 생성 중... (상위 10개 뉴스)")
            try:
                # 상위 10개 뉴스에 대해 AI 요약 적용
                ai_processed = self.ai_summarizer.batch_summarize(processed_news[:10], max_items=10)
                
                # AI 요약 결과 병합
                for i, news in enumerate(processed_news):
                    if i < len(ai_processed):
                        news['summary'] = ai_processed[i].get('summary', self._generate_fallback_summary(news.get('title', ''), news.get('description', '')))
                        news['summary_type'] = ai_processed[i].get('summary_type', 'ai_generated')
                    else:
                        # 나머지는 규칙 기반 요약
                        news['summary'] = self._generate_fallback_summary(news.get('title', ''), news.get('description', ''))
                        news['summary_type'] = 'rule_based'
                
                logger.info(f"✅ AI 요약 완료: 상위 10개는 AI, 나머지는 규칙 기반")
                
            except Exception as e:
                logger.error(f"❌ AI 요약 처리 오류: {e}")
                # AI 실패 시 모든 뉴스에 규칙 기반 요약 적용
                for news in processed_news:
                    news['summary'] = self._generate_fallback_summary(news.get('title', ''), news.get('description', ''))
                    news['summary_type'] = 'rule_based'
                
                logger.warning("🔄 AI 요약 실패로 규칙 기반 요약으로 대체됨")
        
        else:
            # 3단계: 규칙 기반 요약만 사용
            logger.info(f"📝 AI 요약 비활성화 - 규칙 기반 요약 적용 중...")
            for news in processed_news:
                news['summary'] = self._generate_fallback_summary(news.get('title', ''), news.get('description', ''))
                news['summary_type'] = 'rule_based'
        
        # 요약 통계 출력
        summary_stats = {}
        for news in processed_news:
            summary_type = news.get('summary_type', 'unknown')
            summary_stats[summary_type] = summary_stats.get(summary_type, 0) + 1
        
        logger.info(f"📊 요약 생성 통계: {dict(summary_stats)}")
        logger.info(f"✅ 총 {len(processed_news)}개 뉴스 처리 완료")
        
        return processed_news

    def _generate_fallback_summary(self, title: str, description: str) -> str:
        """개선된 규칙 기반 요약 생성"""
        if not title:
            return "음악 업계 소식이 전해졌다."
        
        # 제목에서 아티스트명 추출
        title_lower = title.lower()
        artist_name = title.split()[0] if title else "음악 아티스트"
        
        # 키워드 기반 구체적 요약
        if any(word in title_lower for word in ['announces', 'reveals', 'unveils']):
            if 'album' in title_lower:
                return f"{artist_name}가 새 앨범 발매 소식을 공개했다. 팬들과 업계의 큰 관심을 받고 있다."
            elif 'tour' in title_lower:
                return f"{artist_name}가 새로운 투어 계획을 발표했다. 콘서트 일정이 곧 공개될 예정이다."
            else:
                return f"{artist_name}가 중요한 음악 관련 발표를 했다. 이번 소식은 팬들의 주목을 받고 있다."
        
        elif any(word in title_lower for word in ['releases', 'drops', 'premieres']):
            if 'single' in title_lower:
                return f"{artist_name}가 새로운 싱글을 발표했다. 새 곡은 음악적 진화를 보여주는 작품으로 평가받는다."
            elif 'album' in title_lower:
                return f"{artist_name}가 새 앨범을 발매했다. 이번 릴리스는 아티스트의 대표작이 될 것으로 기대된다."
            else:
                return f"{artist_name}가 새로운 음악을 공개했다. 팬들과 비평가들의 긍정적 반응을 얻고 있다."
        
        elif any(word in title_lower for word in ['tour', 'concert', 'live']):
            return f"{artist_name}의 라이브 공연 관련 소식이 전해졌다. 콘서트 티켓과 일정 정보가 업데이트되었다."
        
        elif any(word in title_lower for word in ['chart', 'number', 'top']):
            return f"{artist_name}가 음악 차트에서 주목할 만한 성과를 기록했다. 상업적 성공을 입증하는 결과다."
        
        elif any(word in title_lower for word in ['collaboration', 'featuring', 'feat']):
            return f"{artist_name}의 새로운 협업 프로젝트 소식이 공개되었다. 음악 팬들의 기대감이 높아지고 있다."
        
        else:
            # 기본 케이스 - 더 구체적으로
            return f"{artist_name}와 관련된 주요 음악 업계 소식이 전해졌다. {title[:60]}{'...' if len(title) > 60 else ''}"


# 테스트 코드
if __name__ == "__main__":
    sample_news = [
        {
            'title': 'The Temper Trap Unveil "Lucky Dimes," First New Single in Nine Years',
            'description': 'Australian band The Temper Trap has released their first new single.',
            'url': 'https://example.com/test',
            'source': 'billboard.com'
        }
    ]
    
    # AI 요약 활성화로 테스트
    classifier = AdvancedClassifier(use_claude_summary=True)
    processed = classifier.process_news_list_simplified(sample_news)
    
    print("=== 테스트 결과 ===")
    for news in processed:
        print(f"제목: {news['title']}")
        print(f"요약: {news['summary']}")
        print(f"요약 타입: {news['summary_type']}")
        print("---")
