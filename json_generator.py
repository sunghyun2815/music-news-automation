#!/usr/bin/env python3
"""
Music News JSON Generator - NewsSection.tsx 완전 호환 버전
NewsSection.tsx가 기대하는 정확한 JSON 구조에 맞춰 생성합니다.
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import logging
from collections import Counter

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MusicNewsJSONGenerator:
    def __init__(self):
        self.output_file = "music_news.json"
        self.archive_dir = "archive"

    def generate_json_data(self, processed_news: List[Dict]) -> Dict:
        """
        NewsSection.tsx가 기대하는 정확한 JSON 구조로 생성
        
        NewsSection.tsx 코드 분석:
        Object.values(json.news || {}).forEach((arr: any) => {
          if (Array.isArray(arr)) allNews.push(...arr);
        });
        
        즉, json.news 객체의 모든 값들이 배열이어야 함
        """

        # NewsSection.tsx의 NewsArticle 타입에 맞는 구조로 변환
        all_news_articles = []

        for news in processed_news:
            news_article = {
                'title': news.get('title', ''),
                'summary': news.get('summary', ''),
                'url': news.get('link', ''),  # link -> url로 변경
                'published_date': news.get('published_date', ''),
                'category': 'interview',  # 모든 뉴스를 'interview' 카테고리로 설정!
                'source': news.get('source', ''),  # 추가 정보
            }

            # membersOnly 플래그 (premium 콘텐츠용)
            if news.get('premium', False) or news.get('membersOnly', False):
                news_article['membersOnly'] = True

            all_news_articles.append(news_article)

        # 날짜순으로 정렬 (최신순)
        all_news_articles.sort(
            key=lambda x: x.get('published_date', ''), 
            reverse=True
        )

        # NewsSection.tsx가 기대하는 JSON 구조
        # json.news 객체의 각 키마다 배열을 가져야 함
        json_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_news': len(all_news_articles),
                'last_updated': datetime.now().isoformat(),
                'version': '2.0',
                'compatible_with': 'NewsSection.tsx'
            },
            'news': {
                # NewsSection.tsx는 Object.values()로 이 객체의 모든 값을 순회함
                # 따라서 각 키의 값이 배열이어야 함
                
                'all_articles': [],  # 비워둠 - 사용하지 않음
                
                'news': [],  # 차트파인더용으로 비워둠 (나중에 차트 데이터 들어갈 예정)
                
                'interview': all_news_articles,  # 모든 뉴스를 여기에! NEWS CLIPPER에서 표시됨
                
                'insight': [],  # 비워둠
            },
            'summary': {
                'total_count': len(all_news_articles),
                'by_category': self._get_category_stats(all_news_articles),
                'by_source': self._get_source_stats(all_news_articles),
                'members_only_count': len([a for a in all_news_articles if a.get('membersOnly', False)])
            }
        }

        return json_data

    def _get_category_stats(self, articles: List[Dict]) -> Dict:
        """카테고리별 통계"""
        categories = {}
        for article in articles:
            category = article.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        return categories

    def _get_source_stats(self, articles: List[Dict]) -> Dict:
        """소스별 통계 (상위 10개)"""
        sources = {}
        for article in articles:
            source = article.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        return dict(sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10])

    def save_json_file(self, json_data: Dict) -> str:
        """JSON 파일 저장"""
        try:
            # 메인 JSON 파일 저장
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            logger.info(f"NewsSection.tsx 호환 JSON 파일 저장 완료: {self.output_file}")

            # 아카이브 파일도 저장
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
                'version': '2.0',
                'description': 'Automated music industry news aggregation - NewsSection.tsx compatible',
                'update_schedule': 'Daily at 10:00 AM KST',
                'endpoints': {
                    'latest_news': 'https://raw.githubusercontent.com/YOUR-USERNAME/music-news-automation/main/music_news.json',
                    'archive': 'https://raw.githubusercontent.com/YOUR-USERNAME/music-news-automation/main/archive/'
                },
                'data_structure': {
                    'metadata': 'Generation info and statistics',
                    'news': 'Object with arrays - compatible with NewsSection.tsx',
                    'summary': 'Statistics and counts'
                },
                'compatible_with': 'NewsSection.tsx',
                'categories': ['news', 'interview', 'insight', 'column'],
                'last_updated': datetime.now().isoformat()
            }
        }

        # API 정보 파일 저장
        try:
            with open('api_info.json', 'w', encoding='utf-8') as f:
                json.dump(api_info, f, ensure_ascii=False, indent=2)
            logger.info("API 정보 파일 생성 완료: api_info.json")
        except Exception as e:
            logger.error(f"API 정보 파일 생성 실패: {e}")

        return api_info

    def create_readme_for_api(self) -> str:
        """API 사용법 README 생성"""
        readme_content = """# 🎵 Music News API - NewsSection.tsx Compatible

NewsSection.tsx와 완벽 호환되는 자동화된 음악 업계 뉴스 API입니다. 
매일 오전 10시(한국시간)에 업데이트됩니다.

## 📡 API 엔드포인트

### 최신 뉴스
```
https://raw.githubusercontent.com/YOUR-USERNAME/music-news-automation/main/music_news.json
```

### API 정보
```
https://raw.githubusercontent.com/YOUR-USERNAME/music-news-automation/main/api_info.json
```

## 📊 NewsSection.tsx 호환 데이터 구조

```json
{
  "metadata": {
    "generated_at": "2025-08-28T10:00:00",
    "total_news": 15,
    "version": "2.0",
    "compatible_with": "NewsSection.tsx"
  },
  "news": {
    "all_articles": [...],  // 모든 뉴스 배열
    "news": [...],         // news 카테고리 뉴스들
    "interview": [...],    // interview/column 카테고리
    "insight": [...]       // insight 카테고리
  },
  "summary": {
    "total_count": 15,
    "by_category": {...},
    "members_only_count": 3
  }
}
```

## 🔄 NewsSection.tsx 사용법

```javascript
// NewsSection.tsx에서 이렇게 사용됩니다:
Object.values(json.news || {}).forEach((arr) => {
  if (Array.isArray(arr)) allNews.push(...arr);
});
```

## 🏷️ 뉴스 아티클 구조

```typescript
type NewsArticle = {
  title: string;
  summary: string;
  url: string;
  published_date: string;
  category: string;
  source: string;
  membersOnly?: boolean;  // 멤버 전용 컨텐츠
};
```

## 📅 카테고리 매칭

- **all**: HOME (터미널 표시)
- **news**: CHART FINDER (차트 터미널) 
- **interview**: NEWS CLIPPER (뉴스 카드들)
- **members**: TREND JACKER (멤버 전용)

## 📞 문의

이슈나 개선사항은 GitHub Issues를 통해 제보해주세요.
"""

        try:
            with open('README.md', 'w', encoding='utf-8') as f:
                f.write(readme_content)
            logger.info("README.md 파일 생성 완료")
            return readme_content
        except Exception as e:
            logger.error(f"README.md 파일 생성 실패: {e}")
            raise

    def create_test_json_for_newsection(self) -> Dict:
        """NewsSection.tsx 테스트용 샘플 JSON"""
        sample_news = [
            {
                'title': '글로벌 K-POP 시장, 전년 대비 30% 성장',
                'summary': 'K-POP 산업이 2025년 상반기 전 세계적으로 30%의 성장률을 기록하며 새로운 전성기를 맞이하고 있습니다. 특히 동남아시아와 남미 지역에서의 성장이 두드러집니다.',
                'link': 'https://example.com/news/kpop-growth-2025',
                'published_date': '2025-08-28T10:00:00Z',
                'category': 'news',
                'source': 'Music Business Worldwide'
            },
            {
                'title': '아이브 신곡, 빌보드 핫 100 진입 성공',
                'summary': '아이브의 최신 싱글이 빌보드 핫 100 차트 78위에 진입하며 K-POP 걸그룹의 미국 시장 진출 성과를 보여주고 있습니다.',
                'link': 'https://example.com/news/ive-billboard-hot100',
                'published_date': '2025-08-28T09:30:00Z',
                'category': 'news',
                'source': 'Billboard Korea'
            },
            {
                'title': '스트리밍 플랫폼 수익 분배 정책 개편안 발표',
                'summary': '주요 음원 스트리밍 서비스들이 아티스트 수익 분배율을 기존 60%에서 70%로 상향 조정하는 새로운 정책을 내년부터 시행한다고 발표했습니다.',
                'link': 'https://example.com/news/streaming-revenue-share',
                'published_date': '2025-08-28T09:00:00Z',
                'category': 'insight',
                'source': 'Music Industry Today',
                'membersOnly': True  # 멤버 전용 콘텐츠
            },
            {
                'title': 'BTS RM "솔로 앨범으로 새로운 도전"',
                'summary': 'BTS의 리더 RM이 곧 발매될 두 번째 솔로 앨범에 대해 "더욱 개인적이고 실험적인 음악을 선보이겠다"고 밝혔습니다.',
                'link': 'https://example.com/interview/rm-solo-album-2025',
                'published_date': '2025-08-28T08:30:00Z',
                'category': 'interview',
                'source': 'Rolling Stone Korea'
            },
            {
                'title': '국내 음반 시장 규모 1조원 돌파 전망',
                'summary': '한국음악콘텐츠협회에 따르면 2025년 국내 음반 시장 규모가 처음으로 1조원을 돌파할 것으로 예상된다고 발표했습니다.',
                'link': 'https://example.com/news/music-market-1trillion',
                'published_date': '2025-08-28T08:00:00Z',
                'category': 'news',
                'source': '한국음악콘텐츠협회'
            },
            {
                'title': '[전문가 칼럼] AI 시대, 음악 산업의 미래',
                'summary': '인공지능 기술이 음악 창작, 유통, 소비 전반에 미치는 영향과 앞으로의 전망에 대해 업계 전문가들이 분석했습니다.',
                'link': 'https://example.com/column/ai-music-future',
                'published_date': '2025-08-28T07:30:00Z',
                'category': 'column',
                'source': 'Music Tech Review',
                'membersOnly': True  # 전문가 칼럼은 멤버 전용
            }
        ]

        return self.generate_json_data(sample_news)


# 실행부
if __name__ == "__main__":
    generator = MusicNewsJSONGenerator()
    
    print("🔄 NewsSection.tsx 호환 JSON 생성 중...")
    
    # 테스트 JSON 생성
    sample_json = generator.create_test_json_for_newsection()
    
    # 파일 저장
    generator.save_json_file(sample_json)
    
    print("\n📊 생성된 JSON 구조:")
    print(f"- 총 뉴스: {sample_json['metadata']['total_news']}개")
    print(f"- json.news 키 목록: {list(sample_json['news'].keys())}")
    print(f"- 각 배열 크기:")
    for key, value in sample_json['news'].items():
        if isinstance(value, list):
            print(f"  - {key}: {len(value)}개")
    
    print(f"\n✅ NewsSection.tsx와 완벽 호환되는 JSON 생성 완료!")
    print(f"📁 저장 위치: {generator.output_file}")
    
    # NewsSection.tsx에서 어떻게 사용되는지 확인
    print(f"\n🔍 NewsSection.tsx 동작 확인:")
    print(f"Object.values(json.news)로 가져올 배열들:")
    for key, value in sample_json['news'].items():
        if isinstance(value, list):
            print(f"- {key}: {len(value)}개 뉴스 (첫 번째: '{value[0]['title'][:30]}...')")
