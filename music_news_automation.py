#!/usr/bin/env python3
"""
Music News Automation System
음악 업계 뉴스 자동화 시스템 - 통합 실행 모듈
"""

import sys
import time
import logging
from datetime import datetime
from typing import List, Dict

# 로컬 모듈 임포트
from advanced_news_collector import AdvancedNewsCollector
from advanced_classifier import AdvancedClassifier
from news_delivery_system import NewsDeliverySystem

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
        self.start_time = datetime.now()
        
        # 모듈 초기화
        self.collector = AdvancedNewsCollector()
        self.classifier = AdvancedClassifier()
        self.delivery_system = NewsDeliverySystem(test_mode=test_mode)
        
        # 성능 메트릭
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
    
    def validate_news_quality(self, news_list: List[Dict]) -> List[Dict]:
        """뉴스 품질 검증"""
        validated_news = []
        
        for news in news_list:
            # 기본 필드 검증
            if not news.get('title') or not news.get('description'):
                logger.warning(f"필수 필드 누락: {news.get('title', 'No title')}")
                continue
            
            # 음악 관련성 재검증
            relevance = news.get('relevance_score', 0)
            if relevance < 0.3:
                logger.warning(f"관련성 부족: {news.get('title')} ({relevance:.2f})")
                continue
            
            # 중요도 점수 검증
            importance = news.get('importance_score', 0)
            if importance < 0.1:
                logger.warning(f"중요도 부족: {news.get('title')} ({importance:.2f})")
                continue
            
            validated_news.append(news)
        
        logger.info(f"품질 검증: {len(news_list)} -> {len(validated_news)} 개 뉴스")
        return validated_news
    
    def ensure_category_balance(self, news_list: List[Dict]) -> List[Dict]:
        """카테고리 균형성 확인 및 조정"""
        # 카테고리별 개수 확인
        category_counts = {}
        for news in news_list:
            category = news.get('category', 'NEWS')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        logger.info(f"카테고리 분포: {category_counts}")
        
        # 카테고리가 너무 편중되었는지 확인
        total_news = len(news_list)
        if total_news > 0:
            max_category_ratio = max(category_counts.values()) / total_news
            if max_category_ratio > 0.7:  # 70% 이상 한 카테고리
                logger.warning(f"카테고리 편중 감지: 최대 비율 {max_category_ratio:.1%}")
        
        return news_list
    
    def ensure_tag_diversity(self, news_list: List[Dict]) -> List[Dict]:
        """태그 다양성 확인"""
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
        
        # 다양성 부족 경고
        if diversity_metrics['genre_diversity'] < 3:
            logger.warning("장르 다양성 부족")
        if diversity_metrics['industry_diversity'] < 5:
            logger.warning("업계 태그 다양성 부족")
        if diversity_metrics['region_diversity'] < 2:
            logger.warning("지역 다양성 부족")
        
        return news_list
    
    def run_automation(self) -> Dict:
        """자동화 시스템 실행"""
        logger.info("=" * 60)
        logger.info("음악 업계 뉴스 자동화 시스템 실행 시작")
        logger.info("=" * 60)
        
        try:
            # 1단계: RSS 피드에서 뉴스 수집
            logger.info("1단계: RSS 피드 뉴스 수집 시작")
            collected_news = self.collector.collect_all_news()
            
            if not collected_news:
                logger.error("뉴스 수집 실패 - 시스템 종료")
                return {'success': False, 'error': '뉴스 수집 실패'}
            
            self.metrics['total_news_collected'] = len(collected_news)
            logger.info(f"1단계 완료: {len(collected_news)}개 뉴스 수집")
            
            # 2단계: 카테고리 분류 및 태깅
            logger.info("2단계: 카테고리 분류 및 태깅 시작")
            classified_news = self.classifier.process_news_list(collected_news)
            logger.info(f"2단계 완료: {len(classified_news)}개 뉴스 분류")
            
            # 3단계: 품질 검증
            logger.info("3단계: 뉴스 품질 검증 시작")
            validated_news = self.validate_news_quality(classified_news)
            logger.info(f"3단계 완료: {len(validated_news)}개 뉴스 검증 통과")
            
            # 4단계: 카테고리별 상위 뉴스 선별
            logger.info("4단계: 카테고리별 상위 뉴스 선별 시작")
            selected_news = self.classifier.select_top_news_by_category(validated_news, per_category=4)
            logger.info(f"4단계 완료: {len(selected_news)}개 뉴스 선별")
            
            # 5단계: 균형성 및 다양성 검증
            logger.info("5단계: 균형성 및 다양성 검증 시작")
            balanced_news = self.ensure_category_balance(selected_news)
            final_news = self.ensure_tag_diversity(balanced_news)
            
            self.metrics['final_news_count'] = len(final_news)
            logger.info(f"5단계 완료: 최종 {len(final_news)}개 뉴스 준비")
            
            # 6단계: 발송
            logger.info("6단계: 뉴스 발송 시작")
            delivery_results = self.delivery_system.deliver_news(final_news)
            
            # 메트릭 계산
            self.metrics['processing_time'] = (datetime.now() - self.start_time).total_seconds()
            self.metrics['delivery_success_rate'] = sum(delivery_results.values()) / len(delivery_results) * 100
            
            # 최종 결과
            success = any(delivery_results.values())
            
            if success:
                logger.info("=" * 60)
                logger.info("음악 업계 뉴스 자동화 시스템 실행 완료")
                logger.info(f"처리 시간: {self.metrics['processing_time']:.1f}초")
                logger.info(f"수집된 뉴스: {self.metrics['total_news_collected']}개")
                logger.info(f"최종 발송: {self.metrics['final_news_count']}개")
                logger.info(f"발송 성공률: {self.metrics['delivery_success_rate']:.1f}%")
                logger.info("=" * 60)
                
                return {
                    'success': True,
                    'metrics': self.metrics,
                    'delivery_results': delivery_results,
                    'final_news': final_news
                }
            else:
                logger.error("발송 실패 - 시스템 실행 실패")
                return {'success': False, 'error': '발송 실패'}
                
        except Exception as e:
            logger.error(f"시스템 실행 중 오류 발생: {e}")
            return {'success': False, 'error': str(e)}
    
    def print_summary_report(self, result: Dict):
        """실행 결과 요약 보고서 출력"""
        print("\n" + "=" * 80)
        print("🎵 음악 업계 뉴스 자동화 시스템 실행 보고서")
        print("=" * 80)
        
        if result.get('success'):
            metrics = result.get('metrics', {})
            delivery_results = result.get('delivery_results', {})
            
            print(f"✅ 실행 상태: 성공")
            print(f"⏱️  처리 시간: {metrics.get('processing_time', 0):.1f}초")
            print(f"📊 수집된 뉴스: {metrics.get('total_news_collected', 0)}개")
            print(f"📤 최종 발송: {metrics.get('final_news_count', 0)}개")
            print(f"📱 Slack 발송: {'성공' if delivery_results.get('slack_success') else '실패'}")
            print(f"📧 이메일 발송: {'성공' if delivery_results.get('email_success') else '실패'}")
            print(f"🎯 발송 성공률: {metrics.get('delivery_success_rate', 0):.1f}%")
            
            # 목표 달성 여부
            processing_time = metrics.get('processing_time', 0)
            if processing_time <= 1800:  # 30분
                print("✅ 처리 시간 목표 달성 (30분 이내)")
            else:
                print("⚠️  처리 시간 목표 미달성")
            
            if metrics.get('delivery_success_rate', 0) >= 50:
                print("✅ 발송 성공률 목표 달성")
            else:
                print("⚠️  발송 성공률 목표 미달성")
                
        else:
            print(f"❌ 실행 상태: 실패")
            print(f"🚨 오류: {result.get('error', '알 수 없는 오류')}")
        
        print("=" * 80)

def main():
    """메인 실행 함수"""
    # 명령행 인수 처리
    test_mode = True
    if len(sys.argv) > 1 and sys.argv[1] == '--production':
        test_mode = False
        logger.info("실제 발송 모드로 실행")
    else:
        logger.info("테스트 모드로 실행 (--production 옵션으로 실제 발송)")
    
    # 시스템 실행
    automation_system = MusicNewsAutomationSystem(test_mode=test_mode)
    result = automation_system.run_automation()
    
    # 결과 보고서 출력
    automation_system.print_summary_report(result)
    
    # 종료 코드 반환
    return 0 if result.get('success') else 1

if __name__ == "__main__":
    exit_code = main()


# music_news_automation.py 마지막에 추가
def save_to_json(news_data):
    output = {
        "updated_at": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_count": len(news_data),
        "categories": {
            "NEWS": [item for item in news_data if item["category"] == "NEWS"],
            "REPORT": [item for item in news_data if item["category"] == "REPORT"],
            "INSIGHT": [item for item in news_data if item["category"] == "INSIGHT"],
            "INTERVIEW": [item for item in news_data if item["category"] == "INTERVIEW"],
            "COLUMN": [item for item in news_data if item["category"] == "COLUMN"]
        },
        "all_news": news_data
    }
    
    # JSON 파일 저장
    with open('music_news.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("JSON 파일 생성 완료!")

# 메인 함수 끝에 추가
save_to_json(final_news_list)
