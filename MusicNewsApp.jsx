import React, { useState, useEffect } from 'react';
import './MusicNewsApp.css';

const MusicNewsApp = () => {
  const [newsData, setNewsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // GitHub 저장소 정보 (환경변수로 설정 권장)
  const GITHUB_USERNAME = process.env.REACT_APP_GITHUB_USERNAME || 'YOUR-USERNAME';
  const REPO_NAME = process.env.REACT_APP_REPO_NAME || 'music-news-automation';
  const JSON_URL = `https://raw.githubusercontent.com/${GITHUB_USERNAME}/${REPO_NAME}/main/music_news.json`;

  const CATEGORY_NAMES = {
    'NEWS': '📰 뉴스',
    'REPORT': '📊 리포트',
    'INSIGHT': '💡 인사이트',
    'INTERVIEW': '🎤 인터뷰',
    'COLUMN': '✍️ 칼럼'
  };

  const CATEGORY_CLASSES = {
    'NEWS': 'news',
    'REPORT': 'report',
    'INSIGHT': 'insight',
    'INTERVIEW': 'interview',
    'COLUMN': 'column'
  };

  useEffect(() => {
    loadMusicNews();
    
    // 5분마다 자동 새로고침
    const interval = setInterval(loadMusicNews, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  const loadMusicNews = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('뉴스 데이터 로딩 시작...');
      
      const response = await fetch(JSON_URL);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('뉴스 데이터 로딩 완료:', data);
      
      setNewsData(data);
      setLastUpdated(new Date(data.metadata.generated_at));
      
    } catch (err) {
      console.error('뉴스 로딩 실패:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatKoreanTime = (date) => {
    return date.toLocaleString('ko-KR', {
      timeZone: 'Asia/Seoul',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const StatCard = ({ label, value }) => (
    <div className="stat-card">
      <div className="stat-number">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );

  const NewsItem = ({ article }) => {
    const tags = [
      ...article.tags.genre.map(tag => ({ type: '🎵', value: tag })),
      ...article.tags.industry.map(tag => ({ type: '🏢', value: tag })),
      ...article.tags.region.map(tag => ({ type: '🌍', value: tag }))
    ];

    return (
      <div className="news-item">
        <div className="news-title">
          <a 
            href={article.url} 
            target="_blank" 
            rel="noopener noreferrer"
          >
            {article.title}
          </a>
        </div>
        <div className="news-summary">{article.summary}</div>
        <div className="news-meta">
          <span className="news-source">📍 {article.source}</span>
          <span className="news-score">⭐ {article.importance_score}</span>
        </div>
        <div className="tags">
          {tags.map((tag, index) => (
            <span key={index} className="tag">
              {tag.type} {tag.value}
            </span>
          ))}
        </div>
      </div>
    );
  };

  const CategorySection = ({ category, articles }) => (
    <div className="category-section">
      <div className={`category-header ${CATEGORY_CLASSES[category]}`}>
        {CATEGORY_NAMES[category]} ({articles.length}개)
      </div>
      {articles.map((article, index) => (
        <NewsItem key={article.id || index} article={article} />
      ))}
    </div>
  );

  if (loading) {
    return (
      <div className="container">
        <div className="header">
          <h1>🎵 Music News Dashboard</h1>
          <p>실시간 음악 업계 뉴스 - 매일 오전 10시 업데이트</p>
        </div>
        <div className="loading">
          📡 뉴스 데이터를 불러오는 중...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="header">
          <h1>🎵 Music News Dashboard</h1>
          <p>실시간 음악 업계 뉴스 - 매일 오전 10시 업데이트</p>
        </div>
        <div className="error">
          ❌ 뉴스 데이터를 불러올 수 없습니다: {error}
          <br />
          <button onClick={loadMusicNews} style={{ marginTop: '10px' }}>
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  if (!newsData) {
    return null;
  }

  const { metadata, news, summary } = newsData;

  const stats = [
    { label: '총 뉴스', value: metadata.total_news },
    { label: '카테고리', value: Object.keys(metadata.categories).length },
    { label: '상위 장르', value: summary.top_genres.length },
    { label: '커버 지역', value: summary.top_regions.length }
  ];

  return (
    <div className="container">
      <div className="header">
        <h1>🎵 Music News Dashboard</h1>
        <p>실시간 음악 업계 뉴스 - 매일 오전 10시 업데이트</p>
      </div>

      <div className="stats">
        {stats.map((stat, index) => (
          <StatCard key={index} label={stat.label} value={stat.value} />
        ))}
      </div>

      <div className="categories">
        {Object.entries(news)
          .filter(([category, articles]) => articles.length > 0)
          .map(([category, articles]) => (
            <CategorySection 
              key={category} 
              category={category} 
              articles={articles} 
            />
          ))}
      </div>

      {lastUpdated && (
        <div className="last-updated">
          📅 마지막 업데이트: {formatKoreanTime(lastUpdated)}
        </div>
      )}
    </div>
  );
};

export default MusicNewsApp;

