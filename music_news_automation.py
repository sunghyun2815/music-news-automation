#!/usr/bin/env python3
"""
Music News Automation System
음악 산업 뉴스를 자동으로 수집, 분류, 요약하고 Slack 및 이메일로 발송합니다.
"""
import os
import argparse
import logging
from datetime import datetime
from typing import List, Dict

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 모듈 임포트 (경로 문제 해결을 위해 sys.path 추가 가능)
# import sys
# sys.path.append(os.path.dirname(__file__))

from advanced_news_collector import AdvancedNewsCollector
from advanced_classifier import AdvancedClassifier
from news_delivery_system import NewsDeliverySystem
from json_generator import MusicNewsJSONGenerator  # 클래스 이름 변경에 맞춰 수정

def main():
    parser = argparse.ArgumentParser(description="음악 뉴스 자동화 시스템")
    parser.add_argument('--production', action='store_true', help='실제 발송 모드 (Slack, Email)')
    args = parser.parse_args()
    
    logger.info("--- 음악 뉴스 자동화 시스템 시작 ---")
    start_time = datetime.now()
    
    # 1. 뉴스 수집
    logger.info("1. 뉴스 수집 시작...")
    collector = AdvancedNewsCollector()
    
    # ✅ 수정: collect_news → collect_all_news (RSS 피드 목록은 클래스 내부에 정의됨)
    all_news_items = collector.collect_all_news()
    logger.info(f"총 {len(all_news_items)}개 뉴스 아이템 수집 완료.")
    
    # 2. 중복 제거
    logger.info("2. 중복 제거 시작...")
    # ✅ 수정: collect_all_news()가 이미 중복 제거를 수행하므로 그대로 사용
    # deduplicate_news 메서드가 없으므로 이미 처리된 데이터 사용
    unique_news_items = all_news_items
    logger.info(f"중복 제거 후 {len(unique_news_items)}개 뉴스 아이템 남음.")
    
    # 3. 뉴스 분류, 태깅, 요약, 중요도 점수 계산
    logger.info("3. 뉴스 분류, 태깅, 요약, 중요도 점수 계산 시작...")
    classifier = AdvancedClassifier()
    processed_news = classifier.process_news_list(unique_news_items)
    logger.info(f"총 {len(processed_news)}개 뉴스 아이템 처리 완료.")
    
    # 4. 카테고리별 상위 뉴스 선별 (예: 각 카테고리별 4개)
    logger.info("4. 카테고리별 상위 뉴스 선별 시작...")
    selected_news = classifier.select_top_news_by_category(processed_news, max_per_category=4)
    logger.info(f"총 {len(selected_news)}개 뉴스 아이템 선별 완료.")
    
    # 5. JSON 파일 생성 및 저장
    logger.info("5. JSON 파일 생성 및 저장 시작...")
    json_generator = MusicNewsJSONGenerator()
    json_data = json_generator.generate_json_data(selected_news)
    json_generator.save_json_file(json_data)
    json_generator.generate_api_info()  # API 정보 파일도 생성
    json_generator.create_readme_for_api()  # ✅ 추가: README 파일 생성
    logger.info("JSON 파일, API 정보 파일, README 파일 생성 완료.")
    
    # 6. 뉴스 발송 (프로덕션 모드에서만)
    if args.production:
        logger.info("6. 프로덕션 모드: 뉴스 발송 시작 (Slack & Email)...")
        
        # test_mode=False로 설정하여 실제 발송 모드 활성화
        delivery_system = NewsDeliverySystem(test_mode=False)
        
        # 통합 발송 (Slack + 이메일 동시)
        try:
            results = delivery_system.deliver_news(selected_news)
            
            if results['slack_success']:
                logger.info("✅ Slack 발송 완료")
            else:
                logger.warning("❌ Slack 발송 실패")
            
            if results['email_success']:
                logger.info("✅ 이메일 발송 완료")
            else:
                logger.warning("❌ 이메일 발송 실패")
                
            # 발송 결과 요약
            success_count = sum(results.values())
            total_channels = len(results)
            logger.info(f"📊 발송 결과: {success_count}/{total_channels} 채널 성공")
            
        except Exception as e:
            logger.error(f"❌ 뉴스 발송 중 오류 발생: {e}")
            
    else:
        logger.info("6. 테스트 모드: 뉴스 발송을 건너뜁니다. '--production' 플래그를 사용하여 발송하세요.")
    
    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"--- 음악 뉴스 자동화 시스템 완료 (총 소요 시간: {duration}) ---")

if __name__ == "__main__":
    main()
