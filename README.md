# 🎵 Music News API - NewsSection.tsx Compatible

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
