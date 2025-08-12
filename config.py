#!/usr/bin/env python3
"""
Configuration file for Music News Automation System
모든 설정값을 중앙에서 관리
"""

import os
from datetime import datetime, timedelta

# =============================================================================
# RSS 피드 설정
# =============================================================================
RSS_FEEDS = [
    "https://feeds.feedburner.com/billboard/chart-beat",
    "https://www.rollingstone.com/music/music-news/feed/",
    "https://pitchfork.com/rss/news/",
    "https://consequenceofsound.net/feed/",
    "https://variety.com/music/feed/",
    "https://www.allkpop.com/rss",
    "https://www.soompi.com/feed",
    "https://www.musicbusinessworldwide.com/feed/"
]

# =============================================================================
# 날짜 필터 설정 (동적으로 계산)
# =============================================================================
def get_cutoff_date():
    """뉴스 수집 기준일 계산 (현재로부터 7일 전)"""
    return datetime.now() - timedelta(days=7)

NEWS_CUTOFF_DATE = get_cutoff_date()

# =============================================================================
# OpenAI 설정
# =============================================================================
OPENAI_CONFIG = {
    "model": "gpt-4o-mini",
    "max_tokens": 300,
    "temperature": 0.3,
    "max_requests_per_minute": 50
}

# =============================================================================
# Slack 설정
# =============================================================================
SLACK_CONFIG = {
    "channel": "C08RABUFRD0",  # 실제 채널 ID로 변경 필요
    "max_message_length": 4000,
    "username": "Music News Bot",
    "icon_emoji": ":musical_note:"
}

# =============================================================================
# 이메일 설정
# =============================================================================
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "recipient_email": "info@vvckd.ai",
    "subject_prefix": "🎵 음악 업계 뉴스 브리핑"
}

# =============================================================================
# GitHub 설정
# =============================================================================
GITHUB_CONFIG = {
    "username": "YOUR-USERNAME",  # 실제 GitHub 사용자명으로 변경 필요
    "repo_name": "music-news-automation",
    "output_file": "music_news.json",
    "archive_dir": "archive"
}

# =============================================================================
# 파일 경로 설정
# =============================================================================
FILE_PATHS = {
    "output_json": "music_news.json",
    "api_info": "api_info.json",
    "readme": "README.md",
    "archive_dir": "archive",
    "logs_dir": "logs"
}

# =============================================================================
# 처리 설정
# =============================================================================
PROCESSING_CONFIG = {
    "max_news_per_feed": 20,
    "max_news_per_category": 4,
    "duplicate_threshold": 0.8,
    "ai_summary_max_items": 10,
    "request_delay": 1.0  # RSS 요청 간격 (초)
}

# =============================================================================
# 로깅 설정
# =============================================================================
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": "logs/music_news.log",
    "max_log_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# =============================================================================
# API 키 및 토큰 (환경변수에서 가져오기)
# =============================================================================
API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "slack_token": os.getenv("SLACK_TOKEN"),
    "email_password": os.getenv("EMAIL_PASSWORD"),
    "github_token": os.getenv("GITHUB_TOKEN"),
    "spotify_client_id": os.getenv("SPOTIFY_CLIENT_ID"),
    "spotify_client_secret": os.getenv("SPOTIFY_CLIENT_SECRET"),
    "twitter_bearer_token": os.getenv("TWITTER_BEARER_TOKEN")
}

# =============================================================================
# 개발/프로덕션 모드 설정
# =============================================================================
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

DEV_CONFIG = {
    "test_mode": True,
    "max_news_limit": 50,
    "ai_summary_enabled": False,
    "realtime_data_enabled": False
}

PROD_CONFIG = {
    "test_mode": False,
    "max_news_limit": 200,
    "ai_summary_enabled": True,
    "realtime_data_enabled": True
}

# 현재 환경에 따른 설정 선택
CURRENT_CONFIG = PROD_CONFIG if ENVIRONMENT == "production" else DEV_CONFIG

# =============================================================================
# 유효성 검사 함수
# =============================================================================
def validate_config():
    """필수 설정값들이 올바르게 설정되었는지 검사"""
    errors = []
    
    # API 키 검사
    required_keys = ["openai", "slack_token", "email_password"]
    for key in required_keys:
        if not API_KEYS.get(key):
            errors.append(f"Missing API key: {key}")
    
    # GitHub 설정 검사
    if GITHUB_CONFIG["username"] == "YOUR-USERNAME":
        errors.append("GitHub username not configured")
    
    # RSS 피드 검사
    if not RSS_FEEDS:
        errors.append("No RSS feeds configured")
    
    return errors

# =============================================================================
# 설정 정보 출력 함수
# =============================================================================
def print_config_summary():
    """현재 설정 요약 출력"""
    print("=== Music News Automation 설정 ===")
    print(f"환경: {ENVIRONMENT}")
    print(f"RSS 피드 수: {len(RSS_FEEDS)}")
    print(f"테스트 모드: {CURRENT_CONFIG['test_mode']}")
    print(f"AI 요약: {CURRENT_CONFIG['ai_summary_enabled']}")
    print(f"실시간 데이터: {CURRENT_CONFIG['realtime_data_enabled']}")
    print(f"최대 뉴스 수: {CURRENT_CONFIG['max_news_limit']}")
    
    # 설정 유효성 검사
    errors = validate_config()
    if errors:
        print("\n⚠️  설정 오류:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✅ 모든 설정이 올바르게 구성되었습니다.")

if __name__ == "__main__":
    print_config_summary()
