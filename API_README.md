# 🎵 Music News API

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
