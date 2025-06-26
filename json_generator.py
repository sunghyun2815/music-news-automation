#!/usr/bin/env python3
"""
Music News JSON Generator
GitHub Actions용 JSON 파일 생성 및 커밋 시스템
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import logging
from collections import Counter # Counter 임포트 추가

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MusicNewsJSONGenerator:
    def __init__(self):
        self.output_file = "music_news.json"
        self.archive_dir = "archive"
        
    def generate_json_data(self, processed_news: List[Dict]) -> Dict:
        """뉴스 데이터를 JSON 형태로 변환"""
        
        # 카테고리별로 분류
        categorized_news = {
            'NEWS': [],
            'REPORT': [],
            'INSIGHT': [],
            'INTERVIEW': [],
            'COLUMN': []
        }
        
        for news in processed_news:
            category = news.get('category', 'NEWS')
            if category in categorized_news:
                
                # 웹사이트용 데이터 구조
                # 'link' 대신 'url' 필드를 사용하도록 수정
                web_news_item = {
                    'id': news.get('id', ''),
                    'title': news.get('title', ''),
                    'summary': news.get('summary', ''), # advanced_classifier.py에서 채워진 summary 사용
                    'url': news.get('url', ''), # 'link' 대신 'url' 사용
                    'source': news.get('source', ''),
                    'published_date': news.get('published_date', ''),
                    'importance_score': news.get('importance_score', 0),
                    'tags': {
                        'genre': news.get('tags', {}).get('genre', []),
                        'industry': news.get('tags', {}).get('industry', []),
                        'region': news.get('tags', {}).get('region', [])
                    },
                    'category': category
                }
                
                categorized_news[category].append(web_news_item)
        
        # 메타데이터 추가
        json_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_news': len(processed_news),
                'categories': {
                    category: len(news_list) 
                    for category, news_list in categorized_news.items()
                },
                'version': '1.0',
                'source': 'Music News Automation System'
            },
            'news': categorized_news,
            "summary": { # summary 필드 추가
                "top_genres": self._get_top_tags(processed_news, 'genre'),
                "top_industries": self._get_top_tags(processed_news, 'industry'),
                "top_regions": self._get_top_tags(processed_news, 'region')
            }
        }
        
        return json_data
    
    def _get_top_tags(self, news_list: List[Dict], tag_type: str) -> List[str]:
        """상위 태그 추출"""
        tag_counts = {}
        
        for news in news_list:
            tags = news.get('tags', {}).get(tag_type, [])
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 상위 5개 태그 반환
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, count in sorted_tags[:5]]
    
    def save_json_file(self, json_data: Dict) -> str:
        """JSON 파일 저장"""
        try:
            # 메인 JSON 파일 저장
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON 파일 저장 완료: {self.output_file}")
            
            # 아카이브 파일도 저장 (날짜별)
            os.makedirs(self.archive_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_file = f"{self.archive_dir}/music_news_{timestamp}.json"
            
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"아카이브 파일 저장 완료: {archive_file}")
            
            return self.output_file
            
        except Exception as e:
            logger.error(f"JSON 파일 저장 실패: {e}")
            raise
    
    def generate_api_info(self) -> Dict:
        """API 정보 생성"""
        api_info = {
            'api_info': {
                'name': 'Music News API',
                'version': '1.0',
                'description': 'Automated music industry news aggregation',
                'update_schedule': 'Daily at 10:00 AM KST',
                'endpoints': {
                    'latest_news': 'https://raw.githubusercontent.com/YOUR-USERNAME/music-news-automation/main/music_news.json',
                    'archive': 'https://raw.githubusercontent.com/YOUR-USERNAME/music-news-automation/main/archive/'
                },
                'data_structure': {
                    'metadata': 'Generation info and statistics',
                    'news': '
