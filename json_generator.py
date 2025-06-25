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
                web_news_item = {
                    'id': news.get('id', ''),
                    'title': news.get('title', ''),
                    'summary': news.get('summary', ''),
                    'url': news.get('link', ''),
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
            'summary': {
                'top_genres': self._get_top_tags(processed_news, 'genre'),
                'top_regions': self._get_top_tags(processed_news, 'region'),
                'top_industries': self._get_top_tags(processed_news, 'industry')
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
                    'news': 'Categorized news articles',
                    'summary': 'Top tags and trends'
                },
                'categories': ['NEWS', 'REPORT', 'INSIGHT', 'INTERVIEW', 'COLUMN'],
                'last_updated': datetime.now().isoformat()
            }
        }
        
        # API 정보 파일 저장
        with open('api_info.json', 'w', encoding='utf-8') as f:
            json.dump(api_info, f, ensure_ascii=False, indent=2)
        
        return api_info
    
    def create_readme_for_api(self) -> str:
        """API 사용법 README 생성"""
        readme_content = """# 🎵 Music News API

자동화된 음악 업계 뉴스 API입니다. 매일 오전 10시(한국시간)에 업데이트됩니다.

## 📡 API 엔드포인트

### 최신 뉴스
```
https://raw.githubusercontent.com/YOUR-USERNAME/music-news-automation/main/music_news.json
```

### API 정보
```
https://raw.githubusercontent.com/YOUR-USERNAME/music-news-automation/main/api_info.json
```

## 📊 데이터 구조

```json
{
  "metadata": {
    "generated_at": "2025-06-24T10:00:00",
    "total_news": 14,
    "categories": {
      "NEWS": 4,
      "REPORT": 3,
      "INSIGHT": 4,
      "INTERVIEW": 2,
      "COLUMN": 1
    }
  },
  "news": {
    "NEWS": [
      {
        "id": "unique_id",
        "title": "뉴스 제목",
        "summary": "5W1H 기반 요약",
        "url": "원본 링크",
        "source": "출처",
        "published_date": "발행일",
        "importance_score": 0.87,
        "tags": {
          "genre": ["pop", "rock"],
          "industry": ["tour", "album"],
          "region": ["us", "korea"]
        },
        "category": "NEWS"
      }
    ]
  },
  "summary": {
    "top_genres": ["pop", "rock", "hip-hop"],
    "top_regions": ["us", "korea", "uk"],
    "top_industries": ["tour", "album", "streaming"]
  }
}
```

## 🚀 사용 예시

### JavaScript (Fetch)
```javascript
async function getMusicNews() {
  try {
    const response = await fetch('https://raw.githubusercontent.com/YOUR-USERNAME/music-news-automation/main/music_news.json');
    const data = await response.json();
    
    console.log(`총 ${data.metadata.total_news}개 뉴스`);
    
    // NEWS 카테고리 뉴스 표시
    data.news.NEWS.forEach(news => {
      console.log(`${news.title} - ${news.source}`);
    });
    
  } catch (error) {
    console.error('뉴스 로딩 실패:', error);
  }
}
```

### Python
```python
import requests

def get_music_news():
    url = 'https://raw.githubusercontent.com/YOUR-USERNAME/music-news-automation/main/music_news.json'
    response = requests.get(url)
    data = response.json()
    
    print(f"총 {data['metadata']['total_news']}개 뉴스")
    
    for news in data['news']['NEWS']:
        print(f"{news['title']} - {news['source']}")

get_music_news()
```

## 📅 업데이트 스케줄

- **자동 업데이트**: 매일 오전 10시 (한국시간)
- **데이터 소스**: 8개 주요 음악 미디어 RSS 피드
- **처리 과정**: 수집 → 중복제거 → 분류 → 태깅 → 요약 → JSON 생성

## 🏷️ 카테고리

- **NEWS**: 일반 뉴스 (투어, 앨범 발매 등)
- **REPORT**: 산업 리포트 (차트, 매출 등)
- **INSIGHT**: 분석 및 인사이트
- **INTERVIEW**: 인터뷰 기사
- **COLUMN**: 칼럼 및 오피니언

## 🔄 CORS 정책

GitHub Raw 파일은 CORS가 허용되어 있어 웹사이트에서 직접 fetch 가능합니다.

## 📞 문의

이슈나 개선사항은 GitHub Issues를 통해 제보해주세요.
"""
        
        with open('API_README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return 'API_README.md'

if __name__ == "__main__":
    # 테스트 코드
    generator = MusicNewsJSONGenerator()
    
    # 테스트 데이터
    test_news = [
        {
            'id': 'test_1',
            'title': 'Test News 1',
            'summary': 'Test summary 1',
            'link': 'https://example.com/1',
            'source': 'Test Source',
            'published_date': '2025-06-24',
            'importance_score': 0.8,
            'category': 'NEWS',
            'tags': {
                'genre': ['pop'],
                'industry': ['tour'],
                'region': ['us']
            }
        }
    ]
    
    json_data = generator.generate_json_data(test_news)
    file_path = generator.save_json_file(json_data)
    api_info = generator.generate_api_info()
    readme_file = generator.create_readme_for_api()
    
    print(f"JSON 파일 생성 완료: {file_path}")
    print(f"API 정보 생성 완료: api_info.json")
    print(f"README 생성 완료: {readme_file}")

