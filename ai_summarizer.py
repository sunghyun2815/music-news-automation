# ai_summarizer.py의 프롬프트 템플릿을 다음과 같이 교체하세요:

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

# 그리고 _post_process_summary 함수도 다음과 같이 개선:

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
    
    # 품질 검증 - 너무 일반적인 표현 체크
    generic_phrases = [
        "음악 활동 소식이 업데이트되었다",
        "최신 소식이 전해졌다",
        "새로운 소식을 발표했다",
        "업계 뉴스가 보도되었다"
    ]
    
    for phrase in generic_phrases:
        if phrase in summary:
            # 일반적인 표현이 발견되면 경고 로그
            logger.warning(f"일반적인 표현 발견: {phrase}")
            # 여전히 반환하되, 향후 개선이 필요함을 표시
            break
    
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

# _generate_fallback_summary 함수도 개선:

def _generate_fallback_summary(self, title: str, description: str) -> str:
    """오류 시 개선된 대체 요약 생성"""
    # 아티스트명 추출
    artist_name = title.split()[0] if title else "음악 아티스트"
    
    # 키워드 기반 구체적 요약
    title_lower = title.lower()
    
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
    else:
        return f"{artist_name}와 관련된 주요 음악 업계 소식이 전해졌다. {title[:60]}{'...' if len(title) > 60 else ''}"
