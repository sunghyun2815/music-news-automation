#!/usr/bin/env python3
"""
Simplified Music News Automation System
중복 제거 + 최신순 정렬로 단순화된 음악 뉴스 자동화 시스템
"""
import os
import argparse
import logging
from datetime import datetime
from typing import List, Dict

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 모듈 임포트
from advanced_news_collector import AdvancedNewsCollector
from advanced_classifier import AdvancedClassifier
from news_delivery_system import NewsDeliverySystem
from json_generator import MusicNewsJSONGenerator

def main():
    """메인 실행 함수 - 단순화된 버전"""
    # 명령행 인수 파싱
    parser = argparse.ArgumentParser(description="단순화된 음악 뉴스 자동화 시스템 (중복제거 + 최신순)")
    parser.add_argument('--production', action='store_true', help='실제 발송 모드 (Slack, Email)')
    parser.add_argument('--count', type=int, default=50, help='가져올 뉴스 개수 (기본값: 50)')
    parser.add_argument('--ai-summary', action='store_true', help='AI 요약 사용 (OpenAI API 필요)')
    parser.add_argument('--claude', action='store_true', help='Claude 요약 사용')
    args = parser.parse_args()
    
    logger.info("🎵 === 단순화된 음악 뉴스 자동화 시스템 시작 ===")
    logger.info(f"목표 뉴스 개수: {args.count}개")
    logger.info(f"AI 요약: {'사용' if args.ai_summary or args.claude else '미사용'}")
    logger.info(f"발송 모드: {'프로덕션' if args.production else '테스트'}")
    
    start_time = datetime.now()
    
    try:
        # 1. 뉴스 수집
        logger.info("\n📰 1단계: 뉴스 수집 시작...")
        collector = AdvancedNewsCollector()
        all_news_items = collector.collect_all_news()
        
        if not all_news_items:
            raise ValueError("수집된 뉴스가 없습니다. RSS 피드를 확인해주세요.")
        
        logger.info(f"✅ 총 {len(all_news_items)}개 뉴스 아이템 수집 완료")
        
        # 2. 중복 제거 (이미 collector에서 수행됨)
        logger.info(f"\n🔄 2단계: 중복 제거 완료 - {len(all_news_items)}개 고유 뉴스")
        
        # 3. 뉴스 분류, 태깅, 요약 (중요도 점수 제외)
        logger.info(f"\n🏷️  3단계: 뉴스 분류, 태깅, 요약...")
        classifier = AdvancedClassifier(
            use_ai_summary=args.ai_summary,
            use_claude_summary=args.claude
        )
        processed_news = classifier.process_news_list_simplified(all_news_items)
        
        if not processed_news:
            raise ValueError("처리된 뉴스가 없습니다.")
        
        logger.info(f"✅ 총 {len(processed_news)}개 뉴스 아이템 처리 완료")
        
        # 처리 통계 출력
        categories = {}
        for news in processed_news:
            category = news.get('category', 'NEWS')
            categories[category] = categories.get(category, 0) + 1
        
        logger.info(f"📊 카테고리별 분포: {dict(sorted(categories.items()))}")
        
        # 4. 최신순으로 정렬하여 상위 N개 선택
        logger.info(f"\n📅 4단계: 최신순 정렬하여 상위 {args.count}개 선택...")
        
        # 발행 시간순으로 정렬 (최신순)
        try:
            sorted_news = sorted(
                processed_news, 
                key=lambda x: x.get('published_date', ''), 
                reverse=True
            )
        except:
            # 정렬 실패 시 원본 순서 유지
            sorted_news = processed_news
        
        # 상위 N개 선택
        selected_news = sorted_news[:args.count]
        
        logger.info(f"✅ 최신순으로 {len(selected_news)}개 뉴스 선택 완료")
        
        # 선별된 뉴스 통계
        selected_categories = {}
        for news in selected_news:
            category = news.get('category', 'NEWS')
            selected_categories[category] = selected_categories.get(category, 0) + 1
        
        logger.info(f"📊 선별된 뉴스 카테고리 분포: {dict(sorted(selected_categories.items()))}")
        
        # 상위 5개 뉴스 미리보기
        logger.info(f"\n🔝 최신 5개 뉴스 미리보기:")
        for i, news in enumerate(selected_news[:5]):
            title = news.get('title', '')[:50] + "..." if len(news.get('title', '')) > 50 else news.get('title', '')
            category = news.get('category', 'NEWS')
            source = news.get('source', '')
            published_date = news.get('published_date', '')
            
            logger.info(f"  {i+1}. [{category}] {title} ({source}) - {published_date}")
        
        # 5. JSON 파일 생성 및 저장
        logger.info(f"\n💾 5단계: JSON 파일 생성 및 저장...")
        json_generator = MusicNewsJSONGenerator()
        json_data = json_generator.generate_json_data(selected_news)
        
        # JSON 파일 저장
        json_generator.save_json_file(json_data)
        logger.info("✅ 메인 JSON 파일 저장 완료")
        
        # API 정보 파일 생성
        json_generator.generate_api_info()
        logger.info("✅ API 정보 파일 생성 완료")
        
        # README 파일 생성
        json_generator.create_readme_for_api()
        logger.info("✅ README 파일 생성 완료")
        
        # 6. 뉴스 발송
        if args.production:
            logger.info(f"\n📤 6단계: 뉴스 발송 시작...")
            delivery_system = NewsDeliverySystem(test_mode=False)
            
            # 발송 실행
            delivery_results = delivery_system.deliver_news(json_data)
            
            # 발송 결과 처리
            success_count = sum(delivery_results.values())
            total_channels = len(delivery_results)
            success_rate = (success_count / total_channels) * 100 if total_channels > 0 else 0
            
            logger.info(f"📊 발송 결과:")
            logger.info(f"  - Slack: {'✅ 성공' if delivery_results.get('slack_success') else '❌ 실패'}")
            logger.info(f"  - Email: {'✅ 성공' if delivery_results.get('email_success') else '❌ 실패'}")
            logger.info(f"  - 전체 성공률: {success_rate:.1f}% ({success_count}/{total_channels})")
            
            # 발송 실패 시 경고
            if success_rate < 50:
                logger.error("❌ 발송 실패율이 높습니다. 설정을 확인해주세요.")
            elif success_rate < 100:
                logger.warning("⚠️  일부 채널 발송에 실패했습니다.")
            else:
                logger.info("🎉 모든 채널 발송 성공!")
        else:
            logger.info(f"\n🧪 6단계: 테스트 모드 - 발송 시뮬레이션")
            delivery_system = NewsDeliverySystem(test_mode=True)
            delivery_results = delivery_system.deliver_news(json_data)
            logger.info("✅ 테스트 모드 발송 시뮬레이션 완료")
        
        # 7. 실행 완료 및 요약
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"\n🎉 === 단순화된 음악 뉴스 자동화 시스템 완료 ===")
        logger.info(f"⏱️  총 실행 시간: {duration:.1f}초")
        logger.info(f"📊 처리 통계:")
        logger.info(f"  - 수집된 뉴스: {len(all_news_items)}개")
        logger.info(f"  - 처리된 뉴스: {len(processed_news)}개")
        logger.info(f"  - 선별된 뉴스: {len(selected_news)}개")
        logger.info(f"  - 선별 방식: 최신순 정렬")
        logger.info(f"  - AI 요약: {'사용됨' if args.ai_summary or args.claude else '미사용'}")
        
        if args.production:
            success_rate = (sum(delivery_results.values()) / len(delivery_results)) * 100
            logger.info(f"  - 발송 성공률: {success_rate:.1f}%")
        
        # 다음 실행 안내
        logger.info(f"\n📅 다음 자동 실행: 내일 오전 10시 (한국시간)")
        logger.info(f"🔗 결과 확인: music_news.json 파일 또는 API 엔드포인트")
        
        return 0  # 성공
        
    except KeyboardInterrupt:
        logger.info("\n👋 사용자에 의해 중단되었습니다.")
        return 1
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.error(f"\n💥 치명적 오류 발생!")
        logger.error(f"❌ 오류: {str(e)}")
        logger.error(f"⏱️  실행 시간: {duration:.1f}초")
        
        return 1  # 실패

def validate_environment():
    """실행 전 환경 검증"""
    logger.info("🔍 환경 검증 중...")
    
    # 필수 파일 확인
    required_files = [
        'advanced_news_collector.py',
        'advanced_classifier.py', 
        'news_delivery_system.py',
        'json_generator.py'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        logger.error(f"❌ 필수 파일 누락: {missing_files}")
        return False
    
    # 디렉토리 생성
    os.makedirs('archive', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    logger.info("✅ 환경 검증 완료")
    return True

if __name__ == "__main__":
    # 환경 검증
    if not validate_environment():
        exit(1)
    
    # 메인 실행
    exit_code = main()
    exit(exit_code)
