#!/usr/bin/env python3
"""
AI 요약 시스템 (Claude API 연동)
음악 뉴스에 대한 고품질 5W1H 요약 생성
"""

import os
import time
import logging
from typing import List, Dict, Optional
from anthropic import Anthropic
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AISummarizer:
    def __init__(self):
        """AI 요약기 초기화"""
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY 환경 변수가 설정되지 않았습니다.")
        
        self.client = Anthropic(api_key=self.api_key)
        self.request_count = 0
        self.max_requests_per_minute = 50  # API 레이트 리미트
        
        # 음악 뉴스 전용 프롬프트 템플릿
        self.prompt_template = """
다음 음악 뉴스를 분석하여 5W1H 형식으로 요약해주세요.

제목: {title}
내용: {description}
URL: {url}

요구사항:
1. Who: 관련 아티스트, 인물, 회사명
2. What: 주요 사건/발표 내용
3. When: 시기 정보
4. Where: 지역/국가 정보
5. Why/How: 배경/이유/방법

응답 형식:
- 2-3문장의 간결한 요약
- 음악 업계 전문 용어 사용
- 핵심 정보만 포함
- 한국어로 작성

요약:"""

    def generate_summary(self, title: str, description: str, url: str = "") -> str:
        """
        Claude API를 사용하여 뉴스 요약 생성
        
        Args:
            title: 뉴스 제목
            description: 뉴스 내용
            url: 뉴스 URL (선택사항)
            
        Returns:
            생성된 요약 텍스트
        """
        try:
            # 레이트 리미트 체크
            self._check_rate_limit()
            
            # 프롬프트 생성
            prompt = self.prompt_template.format(
                title=title,
                description=description,
                url=url
            )
            
            logger.info(f"AI 요약 요청: {title[:50]}...")
            
            # Claude API 호출
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # 빠르고 경제적인 모델
                max_tokens=200,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # 응답 처리
            summary = response.content[0].text.strip()
            
            # 요약 후처리
            summary = self._post_process_summary(summary)
            
            logger.info(f"AI 요약 완료: {len(summary)} 문자")
            self.request_count += 1
            
            return summary
            
        except Exception as e:
            logger.error(f"AI 요약 생성 오류: {e}")
            # 오류 시 기본 요약 반환
            return self._generate_fallback_summary(title, description)
    
    def batch_summarize(self, news_list: List[Dict], max_items: int = 10) -> List[Dict]:
        """
        여러 뉴스를 배치로 요약 처리
        
        Args:
            news_list: 뉴스 리스트
            max_items: 최대 처리 개수 (비용 제한)
            
        Returns:
            AI 요약이 추가된 뉴스 리스트
        """
        logger.info(f"배치 AI 요약 시작: {len(news_list)} 개 중 상위 {max_items}개 처리")
        
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
                    # 나머지는 기존 요약 유지
                    processed_news.append(news)
                    continue
                
                # AI 요약 생성
                ai_summary = self.generate_summary(
                    title=news.get('title', ''),
                    description=news.get('description', ''),
                    url=news.get('url', '')
                )
                
                # 뉴스 항목 업데이트
                updated_news = {
                    **news,
                    'ai_summary': ai_summary,
                    'summary_type': 'ai_generated'
                }
                
                processed_news.append(updated_news)
                
                # API 레이트 리미트 준수
                time.sleep(0.1)  # 요청 간격 조절
                
            except Exception as e:
                logger.error(f"뉴스 처리 오류: {e} - {news.get('title', '')}")
                # 오류 시 원본 뉴스 유지
                processed_news.append({
                    **news,
                    'summary_type': 'rule_based'
                })
        
        logger.info(f"배치 AI 요약 완료: {min(max_items, len(news_list))}개 처리됨")
        return processed_news
    
    def _check_rate_limit(self):
        """API 레이트 리미트 체크"""
        if self.request_count >= self.max_requests_per_minute:
            logger.warning("API 레이트 리미트 도달, 1분 대기...")
            time.sleep(60)
            self.request_count = 0
    
    def _post_process_summary(self, summary: str) -> str:
        """요약 후처리"""
        # "요약:" 접두사 제거
        if summary.startswith("요약:"):
            summary = summary[3:].strip()
        
        # 불필요한 문자 제거
        summary = summary.replace("**", "").replace("*", "")
        
        # 길이 제한
        if len(summary) > 300:
            summary = summary[:297] + "..."
        
        return summary
    
    def _generate_fallback_summary(self, title: str, description: str) -> str:
        """오류 시 기본 요약 생성"""
        # 간단한 규칙 기반 요약
        if "announces" in title.lower() or "releases" in title.lower():
            return f"{title.split()[0] if title else '아티스트'}가 새로운 음악 발표를 공개했습니다."
        elif "tour" in title.lower():
            return f"{title.split()[0] if title else '아티스트'}의 투어 관련 소식입니다."
        elif "deal" in title.lower() or "signs" in title.lower():
            return f"음악 업계 계약 관련 소식입니다."
        else:
            return f"{title[:50]}... 관련 음악 업계 뉴스입니다."

# 설정 정보
AI_SUMMARIZER_CONFIG = {
    "model": "claude-3-haiku-20240307",
    "max_tokens": 200,
    "temperature": 0.3,
    "max_items_per_batch": 10,
    "rate_limit_per_minute": 50
}

def test_ai_summarizer():
    """AI 요약기 테스트"""
    try:
        summarizer = AISummarizer()
        
        # 테스트 뉴스
        test_news = {
            'title': 'Taylor Swift Announces New Album "Midnight Stories"',
            'description': 'Pop superstar Taylor Swift revealed her upcoming album during a surprise announcement, featuring collaborations with indie artists.',
            'url': 'https://example.com/taylor-swift-album'
        }
        
        summary = summarizer.generate_summary(
            title=test_news['title'],
            description=test_news['description'],
            url=test_news['url']
        )
        
        print(f"테스트 요약 결과:\n{summary}")
        return True
        
    except Exception as e:
        print(f"테스트 실패: {e}")
        return False

if __name__ == "__main__":
    # 테스트 실행
    print("=== AI 요약기 테스트 ===")
    test_ai_summarizer()
