#!/usr/bin/env python3
"""
Music News Automation System
음악 업계 뉴스 자동화 시스템 - JSON 생성 기능 포함
"""

import sys
import argparse
import logging
from datetime import datetime
from typing import List, Dict

# 로컬 모듈 임포트
from advanced_news_collector import AdvancedNewsCollector
from advanced_classifier import AdvancedClassifier
from news_delivery_system import NewsDeliverySystem
from json_generator import MusicNewsJSONGenerator

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('music_news_automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MusicNewsAutomationSystem:
    def __init__(self, test_mode: bool = True):
        self.test_mode = test_mode
        self.collector = AdvancedNewsCollector()
        self.classifier = AdvancedClassifier()
        self.delivery_system = NewsDeliverySystem(test_mode=test_mode)
        self.json_generator = MusicNewsJSONGenerator()
        
        # 성능 지표
        self.start_time = None
        self.metrics = {
            'collection_success_rate': 0,
            'duplicate_removal_count': 0,
            'classification_accuracy': 0,
            'delivery_success_rate': 0,
            'processing_time': 0,
            'total_news_collected': 0,
            'final_news_count': 0
        }
        
        logger.info(f"음악 뉴스 자동화 시스템 초기화 완료 (테스트 모드: {test_mode})")
    
    def run_automation(self) -> Dict:
        """전체 자동화 프로세스 실행"""
        self.start_time = datetime.now()
        logger.info("============================================================")
        logger.info("음악 업계 뉴스 자동화 시스템 시작")
        logger.info("============================================================")
        
        try:
            # 1단계: RSS 피드 수집
            logger.info("1단계: RSS 피드 수집 시작")
            collected_news = self.collector.collect_all_news()
            self.metrics['total_news_collected'] = len(collected_news)
            logger.info(f"1단계 완료: {len(collected_news)}개 뉴스 수집")
            
            if not collected_news:
                logger.warning("수집된 뉴스가 없습니다. 프로세스를 종료합니다.")
                return self._generate_report(success=False)
            
            # 2단계: 카테고리 분류 및 태깅
            logger.info("2단계: 카테고리 분류 및 태깅 시작")
            processed_news = self.classifier.process_news_list(collected_news)
            logger.info(f"2단계 완료: {len(processed_news)}개 뉴스 분류")
            
            # 3단계: 뉴스 품질 검증
            logger.info("3단계: 뉴스 품질 검증 시작")
            validated_news = self._validate_news_quality(processed_news)
            logger.info(f"3단계 완료: {len(validated_news)}개 뉴스 검증 통과")
            
            # 4단계: 카테고리별 상위 뉴스 선별
            logger.info("4단계: 카테고리별 상위 뉴스 선별 시작")
            selected_news = self.classifier.select_top_news_by_category(validated_news, max_per_category=4)
            self.metrics['final_news_count'] = len(selected_news)
            logger.info(f"4단계 완료: {len(selected_news)}개 뉴스 선별")
            
            # 5단계: 균형성 및 다양성 검증
            logger.info("5단계: 균형성 및 다양성 검증 시작")
            final_news = self._verify_balance_and_diversity(selected_news)
            logger.info(f"5단계 완료: 최종 {len(final_news)}개 뉴스 준비")
            
            # 6단계: JSON 파일 생성
            logger.info("6단계: JSON 파일 생성 시작")
            json_data = self.json_generator.generate_json_data(final_news)
            json_file = self.json_generator.save_json_file(json_data)
            api_info = self.json_generator.generate_api_info()
            readme_file = self.json_generator.create_readme_for_api()
            logger.info(f"6단계 완료: JSON 파일 생성 ({json_file})")
            
            # 7단계: 뉴스 발송 (기존 Slack/이메일)
            logger.info("7단계: 뉴스 발송 시작")
            delivery_result = self.delivery_system.send_news(final_news)
            
            # 발송 성공률 계산
            success_count = sum(delivery_result.values())
            total_channels = len(delivery_result)
            success_rate = (success_count / total_channels * 100) if total_channels > 0 else 0
            
            self.metrics['delivery_success_rate'] = success_rate
            logger.info(f"7단계 완료: 발송 성공률 {success_rate:.1f}%")
            
            # 성공 보고서 생성
            return self._generate_report(success=True, final_news=final_news, json_file=json_file)
            
        except Exception as e:
            logger.error(f"자동화 프로세스 실행 중 오류 발생: {e}")
            return self._generate_report(success=False, error=str(e))
    
    def _validate_news_quality(self, news_list: List[Dict]) -> List[Dict]:
        """뉴스 품질 검증"""
        validated_news = []
        
        for news in news_list:
            # 필수 필드 확인
            required_fields = ['title', 'link', 'source']
            if all(news.get(field) for field in required_fields):
                validated_news.append(news)
            else:
                logger.warning(f"필수 필드 누락: {news.get('title', 'Unknown')}")
        
        logger.info(f"품질 검증: {len(news_list)} -> {len(validated_news)} 개 뉴스")
        return validated_news
    
    def _verify_balance_and_diversity(self, news_list: List[Dict]) -> List[Dict]:
        """균형성 및 다양성 검증"""
        # 카테고리 분포 확인
        category_distribution = {}
        for news in news_list:
            category = news.get('category', 'NEWS')
            category_distribution[category] = category_distribution.get(category, 0) + 1
        
        logger.info(f"카테고리 분포: {category_distribution}")
        
        # 태그 다양성 확인
        all_genres = set()
        all_industries = set()
        all_regions = set()
        
        for news in news_list:
            tags = news.get('tags', {})
            all_genres.update(tags.get('genre', []))
            all_industries.update(tags.get('industry', []))
            all_regions.update(tags.get('region', []))
        
        diversity_metrics = {
            'genre_diversity': len(all_genres),
            'industry_diversity': len(all_industries),
            'region_diversity': len(all_regions)
        }
        
        logger.info(f"태그 다양성: {diversity_metrics}")
        
        return news_list
    
    def _generate_report(self, success: bool, final_news: List[Dict] = None, 
                        json_file: str = None, error: str = None) -> Dict:
        """실행 보고서 생성"""
        end_time = datetime.now()
        processing_time = (end_time - self.start_time).total_seconds() if self.start_time else 0
        self.metrics['processing_time'] = processing_time
        
        report = {
            'success': success,
            'timestamp': end_time.isoformat(),
            'processing_time': processing_time,
            'metrics': self.metrics,
            'test_mode': self.test_mode
        }
        
        if success and final_news:
            report.update({
                'final_news_count': len(final_news),
                'json_file': json_file,
                'delivery_success': self.metrics['delivery_success_rate'] > 0
            })
        
        if error:
            report['error'] = error
        
        # 로그 출력
        logger.info("============================================================")
        logger.info("음악 업계 뉴스 자동화 시스템 실행 완료")
        logger.info(f"처리 시간: {processing_time:.1f}초")
        logger.info(f"수집된 뉴스: {self.metrics['total_news_collected']}개")
        logger.info(f"최종 발송: {self.metrics['final_news_count']}개")
        if json_file:
            logger.info(f"JSON 파일: {json_file}")
        logger.info(f"발송 성공률: {self.metrics['delivery_success_rate']:.1f}%")
        
        # 목표 달성 여부 확인
        if processing_time <= 1800:  # 30분 이내
            logger.info("✅ 처리 시간 목표 달성 (30분 이내)")
        else:
            logger.warning("⚠️ 처리 시간 목표 미달성")
        
        if self.metrics['delivery_success_rate'] >= 50:  # 50% 이상
            logger.info("✅ 발송 성공률 목표 달성")
        else:
            logger.warning("⚠️ 발송 성공률 목표 미달성")
        
        logger.info("============================================================")
        
        # 콘솔 출력용 요약
        print("=" * 80)
        print("🎵 음악 업계 뉴스 자동화 시스템 실행 보고서")
        print("=" * 80)
        print(f"✅ 실행 상태: {'성공' if success else '실패'}")
        print(f"⏱️  처리 시간: {processing_time:.1f}초")
        print(f"📊 수집된 뉴스: {self.metrics['total_news_collected']}개")
        print(f"📤 최종 발송: {self.metrics['final_news_count']}개")
        if json_file:
            print(f"📄 JSON 파일: {json_file}")
        print(f"📱 Slack 발송: {'성공' if self.metrics['delivery_success_rate'] > 0 else '실패'}")
        print(f"📧 이메일 발송: {'성공' if self.metrics['delivery_success_rate'] > 0 else '실패'}")
        print(f"🎯 발송 성공률: {self.metrics['delivery_success_rate']:.1f}%")
        print(f"✅ 처리 시간 목표 달성 (30분 이내)" if processing_time <= 1800 else "⚠️ 처리 시간 목표 미달성")
        print(f"✅ 발송 성공률 목표 달성" if self.metrics['delivery_success_rate'] >= 50 else "⚠️ 발송 성공률 목표 미달성")
        print("=" * 80)
        
        return report

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='음악 업계 뉴스 자동화 시스템')
    parser.add_argument('--production', action='store_true', 
                       help='프로덕션 모드로 실행 (실제 발송)')
    parser.add_argument('--json-only', action='store_true',
                       help='JSON 파일만 생성 (발송 없음)')
    
    args = parser.parse_args()
    
    # 테스트 모드 결정
    test_mode = not args.production
    
    try:
        # 시스템 초기화 및 실행
        automation_system = MusicNewsAutomationSystem(test_mode=test_mode)
        
        if args.json_only:
            # JSON만 생성하는 모드
            logger.info("JSON 전용 모드로 실행")
            collected_news = automation_system.collector.collect_all_news()
            processed_news = automation_system.classifier.process_news_list(collected_news)
            validated_news = automation_system._validate_news_quality(processed_news)
            selected_news = automation_system.classifier.select_top_news_by_category(validated_news)
            
            json_data = automation_system.json_generator.generate_json_data(selected_news)
            json_file = automation_system.json_generator.save_json_file(json_data)
            automation_system.json_generator.generate_api_info()
            automation_system.json_generator.create_readme_for_api()
            
            print(f"JSON 파일 생성 완료: {json_file}")
        else:
            # 전체 자동화 실행
            result = automation_system.run_automation()
            
            # 실행 결과에 따른 종료 코드 설정
            if result['success']:
                sys.exit(0)
            else:
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("사용자에 의해 프로세스가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

