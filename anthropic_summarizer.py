#!/usr/bin/env python3
"""
Anthropic API 기반 음악 뉴스 요약 시스템
Claude를 사용하여 자연스러운 한국어 요약 생성
"""

import os
import time
import logging
from typing import List, Dict, Optional
import requests
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnthropicSummarizer:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
        
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-haiku-20240307"  # 빠르고 비용 효율적
        self.max_tokens = 200
        self.request_count = 0
        self.max_requests_per_minute = 50
        
        # 요약 프롬프트 템플릿
        self.summary_prompt = """당신은 음악 업계 뉴스 전문 에디터입니다. 주어진 뉴스를 자연스러운 한국어로 요약해주세요.

요구사항:
1. 2-3문장으로 간결하게 요약
2. 5W1H (누가, 무엇을, 언제, 어디서, 왜, 어떻게) 정보 포함
3. 자연스러운 한국어 문체 (뉴스 기사 스타일)
4. 아티스트명, 앨범명, 곡명 등은 정확히 표기
5. 불필요한 영어 단어는 한글로 번역

뉴스 제목: {title}
뉴스 내용: {description}

한국어 요약:"""

    def generate_summary(self, title: str, description: str, url: str = "") -> str:
        """Claude API를 사용한 뉴스 요약 생성"""
        try:
            # API 레이트 리미트 체크
            self._check_rate_limit()
            
            # 프롬프트 생성
            prompt = self.summary_prompt.format(
                title=title.strip(),
                description=description.strip()[:500]  # 길이 제한
            )
            
            # API 요청 데이터
            request_data = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": 0.3,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # API 호출
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=request_data,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 응답에서 요약 추출
            if 'content' in result and len(result['content']) > 0:
                summary = result['content'][0]['text'].strip()
                
                # 후처리
                summary = self._post_process_summary(summary)
                
                logger.info(f"Claude 요약 생성 완료: {len(summary)} 문자")
                self.request_count += 1
                
                return summary
            else:
                raise ValueError("API 응답에서 요약을 찾을 수 없습니다.")
            
        except Exception as e:
            logger.error(f"Claude 요약 생성 오류: {e}")
            # 실패 시 간단한 대체 요약 반환
            return self._generate_fallback_summary(title, description)
    
    def batch_summarize(self, news_list: List[Dict], max_items: int = 10) -> List[Dict]:
        """여러 뉴스를 배치로 요약 처리"""
        logger.info(f"Claude 배치 요약 시작: {len(news_list)}개 중 상위 {max_items}개 처리")
        
        processed_news = []
        
        # 중요도 순으로 정렬
        sorted_news = sorted(
            news_list, 
            key=lambda x: x.get('importance_score', 0), 
            reverse=True
        )
        
        for i, news in enumerate(sorted_news):
            try:
                # 최대 처리 개수 제한
                if i >= max_items:
                    processed_news.append(news)
                    continue
                
                # Claude 요약 생성
                claude_summary = self.generate_summary(
                    title=news.get('title', ''),
                    description=news.get('description', ''),
                    url=news.get('url', '')
                )
                
                # 뉴스 항목 업데이트
                updated_news = {
                    **news,
                    'claude_summary': claude_summary,
                    'summary': claude_summary,  # 기본 summary 필드도 업데이트
                    'summary_type': 'claude_generated'
                }
                
                processed_news.append(updated_news)
                
                # API 레이트 리미트 준수 (요청 간격 조절)
                time.sleep(1.5)  # Claude API는 더 여유롭게
                
            except Exception as e:
                logger.error(f"뉴스 처리 오류: {e} - {news.get('title', '')}")
                # 오류 시 원본 뉴스 유지
                processed_news.append({
                    **news,
                    'summary_type': 'rule_based'
                })
        
        logger.info(f"Claude 배치 요약 완료: {min(max_items, len(news_list))}개 처리됨")
        return processed_news
    
    def _check_rate_limit(self):
        """API 레이트 리미트 체크"""
        if self.request_count >= self.max_requests_per_minute:
            logger.warning("Claude API 레이트 리미트 도달, 1분 대기...")
            time.sleep(60)
            self.request_count = 0
    
    def _post_process_summary(self, summary: str) -> str:
        """Claude 요약 후처리"""
        # 불필요한 접두사 제거
        prefixes_to_remove = ["요약:", "한국어 요약:", "뉴스 요약:", "정리하면"]
        for prefix in prefixes_to_remove:
            if summary.startswith(prefix):
                summary = summary[len(prefix):].strip()
        
        # 마크다운 제거
        summary = summary.replace("**", "").replace("*", "")
        
        # 따옴표 정리
        summary = summary.strip('"').strip("'")
        
        # 길이 제한 (너무 긴 경우 문장 단위로 자르기)
        if len(summary) > 250:
            sentences = summary.split('. ')
            if len(sentences) > 1:
                # 첫 번째와 두 번째 문장만 사용
                summary = '. '.join(sentences[:2])
                if not summary.endswith('.'):
                    summary += '.'
            else:
                # 문장이 하나면 그냥 자르기
                summary = summary[:247] + "..."
        
        return summary
    
    def _generate_fallback_summary(self, title: str, description: str) -> str:
        """Claude API 실패 시 대체 요약"""
        # 간단한 규칙 기반 요약
        if '발표' in title or 'announces' in title.lower():
            return f"음악 아티스트가 새로운 소식을 발표했습니다. {title[:50]}..."
        elif '발매' in title or 'releases' in title.lower():
            return f"새로운 음악이 발매되었습니다. {title[:50]}..."
        elif '투어' in title or 'tour' in title.lower():
            return f"아티스트의 투어 관련 소식이 전해졌습니다. {title[:50]}..."
        else:
            return f"음악 업계 소식이 업데이트되었습니다. {title[:50]}..." if len(title) > 50 else title


# advanced_classifier.py에서 사용하기 위한 수정된 클래스
class AdvancedClassifierWithClaude:
    def __init__(self, use_claude_summary: bool = False, use_ai_summary: bool = False):
        self.use_claude_summary = use_claude_summary
        self.use_ai_summary = use_ai_summary
        self.claude_summarizer = None
        self.ai_summarizer = None
        
        # Claude 요약기 초기화
        if self.use_claude_summary:
            try:
                self.claude_summarizer = AnthropicSummarizer()
                logger.info("Claude 요약기 초기화 완료")
            except Exception as e:
                logger.warning(f"Claude 요약기 초기화 실패: {e}. 규칙 기반 요약을 사용합니다.")
                self.claude_summarizer = None
        
        # OpenAI 요약기 초기화 (기존)
        if self.use_ai_summary and not self.use_claude_summary:
            try:
                from ai_summarizer import AISummarizer
                self.ai_summarizer = AISummarizer()
                logger.info("OpenAI 요약기 초기화 완료")
            except Exception as e:
                logger.warning(f"OpenAI 요약기 초기화 실패: {e}")
                self.ai_summarizer = None
        
        # ... 기존 키워드 정의들 유지 ...
    
    def process_news_list(self, news_list: List[Dict]) -> List[Dict]:
        """뉴스 리스트 처리 (Claude 요약 포함)"""
        processed_news = []
        
        # 기본 처리 (카테고리, 태그, 중요도)
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
                
                # 처리된 뉴스 항목
                processed_item = {
                    **news,
                    'category': category,
                    'tags': tags,
                    'importance_score': importance_score
                }
                
                processed_news.append(processed_item)
                
            except Exception as e:
                logger.error(f"뉴스 처리 오류: {e}")
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
                
                # Claude 요약된 뉴스와 나머지 뉴스 합치기
                final_news = []
                for i, news in enumerate(sorted_news):
                    if i < len(claude_processed) and 'claude_summary' in claude_processed[i]:
                        news['summary'] = claude_processed[i]['claude_summary']
                        news['summary_type'] = 'claude_generated'
                    else:
                        # Claude 요약 실패 시 규칙 기반 요약
                        news['summary'] = self.generate_simple_summary(news.get('title', ''), news.get('description', ''))
                        news['summary_type'] = 'rule_based'
                    final_news.append(news)
                
                processed_news = final_news
                
            except Exception as e:
                logger.error(f"Claude 요약 오류: {e}")
                # 실패 시 모든 뉴스에 규칙 기반 요약 적용
                for news in processed_news:
                    news['summary'] = self.generate_simple_summary(news.get('title', ''), news.get('description', ''))
                    news['summary_type'] = 'rule_based'
        
        elif self.use_ai_summary and self.ai_summarizer:
            # 기존 OpenAI 요약 사용
            # ... 기존 로직 유지 ...
            pass
        
        else:
            # 규칙 기반 요약
            for news in processed_news:
                news['summary'] = self.generate_simple_summary(news.get('title', ''), news.get('description', ''))
                news['summary_type'] = 'rule_based'
        
        logger.info(f"{len(processed_news)}개 뉴스 처리 완료")
        return processed_news
    
    def generate_simple_summary(self, title: str, description: str) -> str:
        """간단한 규칙 기반 요약 (Claude 실패 시 대체용)"""
        return f"음악 업계에서 주목할 만한 소식이 전해졌습니다. {title[:50]}..." if len(title) > 50 else title


# 사용 방법 예시
if __name__ == "__main__":
    # 환경변수 확인
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY 환경변수를 설정해주세요.")
        print("GitHub Secrets에 ANTHROPIC_API_KEY 추가 필요")
        exit(1)
    
    # 테스트
    summarizer = AnthropicSummarizer()
    
    test_news = {
        'title': 'Taylor Swift Announces New Album, The Life of a Showgirl',
        'description': 'Pop superstar Taylor Swift has announced her upcoming album during a surprise social media post, featuring collaborations with various artists.',
        'url': 'https://example.com/test'
    }
    
    print("=== Claude 요약 테스트 ===")
    summary = summarizer.generate_summary(
        title=test_news['title'],
        description=test_news['description'],
        url=test_news['url']
    )
    
    print(f"원본 제목: {test_news['title']}")
    print(f"Claude 요약: {summary}")
    print("✅ 테스트 완료!")
