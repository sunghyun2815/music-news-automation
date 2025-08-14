#!/usr/bin/env python3
"""
AI 요약 시스템 (Claude API 연동) - 개선된 5W1H 한국어 요약
음악 뉴스에 대한 고품질 한국어 요약 생성
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
        
        # 개선된 5W1H 한국어 요약 프롬프트 템플릿
        self.prompt_template = """
다음 음악 업계 뉴스를 한국어로 요약해주세요.

제목: {title}
내용: {description}
출처: {url}

요구사항:
1. **자연스러운 한국어 문장 2-3개로 작성** (총 120-200자)
2. **5W1H 정보를 구체적으로 포함**:
   - 누가(Who): 아티스트명, 밴드명을 정확히 명시
   - 무엇을(What): 구체적인 활동 (앨범 발매, 투어, 싱글 등)
   - 언제(When): 발매일, 일정 등 시기 정보 (있는 경우)
   - 어디서(Where): 지역, 국가 정보 (해당 시)

3. **문체 스타일**:
   - 뉴스 기사 톤의 자연스러운 한국어
   - "~했다", "~한다", "~될 예정이다" 등 다양한 문미
   - 아티스트명은 원어 그대로 유지
   - 구체적인 정보 우선 (날짜, 숫자, 고유명사)

4. **금지사항**:
   - "음악 활동 소식이 업데이트되었다" 같은 일반적 표현 금지
   - "최신 소식이 전해졌다" 같은 뻔한 표현 금지
   - 너무 간단한 1문장 요약 금지

예시:
- 좋은 예: "호주 밴드 템퍼 트랩(The Temper Trap)이 9년 만의 신곡 'Lucky Dimes'를 발표했다. 이번 싱글은 인디 록 그룹의 오랜 공백을 깨고 돌아온 의미 있는 작품으로 평가받고 있다."
- 나쁜 예: "음악 아티스트의 최신 음악 활동 소식이 업데이트되었다."

요약 (5W1H 포함, 구체적이고 자연스러운 문장):"""

    def generate_summary(self, title: str, description: str, url: str = "") -> str:
        """
        Claude API를 사용하여 개선된 한국어 자연문 뉴스 요약 생성
        
        Args:
            title: 뉴스 제목
            description: 뉴스 내용
            url: 뉴스 URL (선택사항)
            
        Returns:
            생성된 5W1H 기반 한국어 요약 텍스트
        """
        try:
            # 레이트 리미트 체크
            self._check_rate_limit()
            
            # 프롬프트 생성
            prompt = self.prompt_template.format(
                title=title,
                description=description[:800],  # 토큰 제한
                url=url
            )
            
            logger.info(f"AI 한글 요약 요청: {title[:50]}...")
            
            # Claude API 호출
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # 빠르고 경제적인 모델
                max_tokens=400,  # 한국어 요약을 위해 증가
                temperature=0.2,  # 일관성을 위해 낮춤
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # 응답 처리
            summary = response.content[0].text.strip()
            
            # 요약 후처리
            summary = self._post_process_summary(summary)
            
            # 품질 검증
            if self._validate_summary_quality(summary, title):
                logger.info(f"AI 한글 요약 완료: {len(summary)} 문자")
                self.request_count += 1
                return summary
            else:
                logger.warning("생성된 요약이 품질 기준 미달. 대체 요약 생성.")
                return self._generate_fallback_summary(title, description)
            
        except Exception as e:
            logger.error(f"AI 요약 생성 오류: {e}")
            # 오류 시 개선된 대체 요약 반환
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
        logger.info(f"배치 AI 한글 요약 시작: {len(news_list)} 개 중 상위 {max_items}개 처리")
        
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
                    # 나머지는 대체 요약 사용
                    fallback_summary = self._generate_fallback_summary(
                        news.get('title', ''),
                        news.get('description', '')
                    )
                    processed_news.append({
                        **news,
                        'summary': fallback_summary,
                        'summary_type': 'rule_based'
                    })
                    continue
                
                # AI 한글 요약 생성
                ai_summary = self.generate_summary(
                    title=news.get('title', ''),
                    description=news.get('description', ''),
                    url=news.get('url', '')
                )
                
                # 뉴스 항목 업데이트
                updated_news = {
                    **news,
                    'summary': ai_summary,
                    'summary_type': 'ai_generated'
                }
                
                processed_news.append(updated_news)
                
                # API 레이트 리미트 준수
                time.sleep(0.1)  # 요청 간격 조절
                
            except Exception as e:
                logger.error(f"뉴스 처리 오류: {e} - {news.get('title', '')}")
                # 오류 시 대체 요약 사용
                fallback_summary = self._generate_fallback_summary(
                    news.get('title', ''),
                    news.get('description', '')
                )
                processed_news.append({
                    **news,
                    'summary': fallback_summary,
                    'summary_type': 'rule_based'
                })
        
        logger.info(f"배치 AI 한글 요약 완료: {min(max_items, len(news_list))}개 처리됨")
        return processed_news
    
    def _check_rate_limit(self):
        """API 레이트 리미트 체크"""
        if self.request_count >= self.max_requests_per_minute:
            logger.warning("API 레이트 리미트 도달, 1분 대기...")
            time.sleep(60)
            self.request_count = 0
    
    def _post_process_summary(self, summary: str) -> str:
        """요약 후처리 - 품질 검증 강화"""
        if not summary:
            return summary
        
        # 기본 정리
        summary = summary.strip()
        
        # 프롬프트 잔재 제거
        import re
        summary = re.sub(r'^(요약|Summary|한국어 요약)\s*[:：]\s*', '', summary)
        summary = summary.strip('"\'""''')
        
        # 문장 끝 정리
        if summary and not summary.endswith(('.', '다', '요', '음', '됨', '함')):
            summary += '.'
        
        # 길이 제한 (200자)
        if len(summary) > 200:
            sentences = summary.split('.')
            if len(sentences) > 1:
                truncated = sentences[0]
                for sentence in sentences[1:]:
                    if len(truncated + '. ' + sentence) <= 197:
                        truncated += '. ' + sentence
                    else:
                        break
                summary = truncated.rstrip('.') + '.'
            else:
                summary = summary[:197] + '...'
        
        return summary
    
    def _validate_summary_quality(self, summary: str, title: str) -> bool:
        """요약 품질 검증"""
        if not summary or len(summary) < 30:
            return False
        
        # 너무 일반적인 표현 금지
        generic_phrases = [
            "음악 활동 소식이 업데이트되었다",
            "최신 소식이 전해졌다", 
            "새로운 소식을 발표했다",
            "업계 뉴스가 보도되었다",
            "음악 업계 뉴스 업데이트입니다"
        ]
        
        for phrase in generic_phrases:
            if phrase in summary:
                return False
        
        # 5W1H 중 최소 2개 요소가 포함되어야 함
        w5h1_indicators = {
            'who': any(indicator in summary for indicator in ['가', '이', '는', '의', '밴드', '아티스트', '가수', '뮤지션']),
            'what': any(indicator in summary for indicator in ['앨범', '곡', '투어', '콘서트', '발매', '공개', '발표', '계약']),
            'when': any(indicator in summary for indicator in ['월', '일', '년', '예정', '오는', '다음', '이번']),
        }
        
        valid_elements = sum(w5h1_indicators.values())
        return valid_elements >= 2  # 최소 2개 요소 필요
    
    def _generate_fallback_summary(self, title: str, description: str) -> str:
        """오류 시 개선된 대체 요약 생성 (5W1H 기반)"""
        # 제목에서 핵심 정보 추출
        title_lower = title.lower()
        
        # 아티스트명 추출 시도
        artist_name = self._extract_artist_name(title)
        
        # 활동 유형별 개선된 템플릿
        if any(word in title_lower for word in ['album', 'ep']):
            return f"{artist_name}가 새 앨범 발매 소식을 공개했다. 이번 릴리스는 팬들과 음악 업계의 큰 관심을 받고 있다."
        elif any(word in title_lower for word in ['single', 'song', 'track']):
            return f"{artist_name}가 새로운 싱글을 발표했다. 새 곡은 아티스트의 음악적 진화를 보여주는 작품으로 평가받고 있다."
        elif any(word in title_lower for word in ['tour', 'concert', 'live']):
            return f"{artist_name}가 새로운 투어 일정을 발표했다. 콘서트 관련 상세 정보는 공식 채널을 통해 확인할 수 있다."
        elif any(word in title_lower for word in ['chart', 'number', 'top']):
            return f"{artist_name}가 음악 차트에서 주목할 만한 성과를 기록했다. 이번 차트 진입은 아티스트의 상업적 성공을 입증한다."
        elif any(word in title_lower for word in ['deal', 'sign', 'contract']):
            return f"{artist_name}가 새로운 음악 계약을 체결했다고 발표되었다. 이번 파트너십은 아티스트의 향후 활동에 긍정적 영향을 미칠 전망이다."
        elif any(word in title_lower for word in ['announces', 'reveals', 'drops']):
            return f"{artist_name}가 중요한 음악 관련 발표를 했다. 이번 소식은 팬들과 업계 관계자들의 주목을 받고 있다."
        else:
            return f"{artist_name}와 관련된 주요 음악 업계 소식이 전해졌다. {title[:60]}{'...' if len(title) > 60 else ''}"
    
    def _extract_artist_name(self, title: str) -> str:
        """제목에서 아티스트명 추출 시도"""
        # 간단한 아티스트명 추출 로직
        import re
        
        # 첫 번째 단어나 구문이 아티스트일 가능성이 높음
        words = title.split()
        if words:
            # 첫 1-3단어를 아티스트로 가정
            if len(words) >= 2:
                potential_artist = ' '.join(words[:2])
                # 일반적인 동사들이 포함되면 첫 단어만
                if any(verb in potential_artist.lower() for verb in ['announces', 'reveals', 'drops', 'releases', 'shares']):
                    return words[0] if words else "음악 아티스트"
                return potential_artist
            else:
                return words[0]
        
        return "음악 아티스트"


# 설정 정보
AI_SUMMARIZER_CONFIG = {
    "model": "claude-3-haiku-20240307",
    "max_tokens": 400,
    "temperature": 0.2,
    "max_items_per_batch": 10,
    "rate_limit_per_minute": 50,
    "language": "Korean",
    "style": "5W1H Natural Korean News Style",
    "quality_validation": True
}

def test_ai_summarizer():
    """AI 요약기 테스트"""
    try:
        summarizer = AISummarizer()
        
        # 테스트 뉴스
        test_news = {
            'title': 'The Temper Trap Unveil "Lucky Dimes," First New Single in Nine Years',
            'description': 'Australian band The Temper Trap has released their first new single in nine years, titled "Lucky Dimes." The track marks a significant return for the indie rock group.',
            'url': 'https://example.com/temper-trap-news'
        }
        
        summary = summarizer.generate_summary(
            title=test_news['title'],
            description=test_news['description'],
            url=test_news['url']
        )
        
        print(f"개선된 5W1H 한글 요약 결과:\n{summary}")
        print(f"요약 길이: {len(summary)} 문자")
        return True
        
    except Exception as e:
        print(f"테스트 실패: {e}")
        return False

if __name__ == "__main__":
    # 테스트 실행
    print("=== 개선된 AI 한글 요약기 테스트 (5W1H) ===")
    test_ai_summarizer()
