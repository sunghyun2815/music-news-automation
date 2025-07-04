#!/usr/bin/env python3
"""
News Delivery System
Slack 채널 및 이메일 발송 시스템 (JSON 구조에 맞게 수정)
"""

import smtplib
import logging
import json
import os
from datetime import datetime
from typing import List, Dict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsDeliverySystem:
    def __init__(self, test_mode: bool = True):
        self.test_mode = test_mode
        
        # Slack 설정 - 환경변수 우선 사용
        self.slack_token = os.getenv('SLACK_TOKEN', "xoxb-your-slack-token")
        self.slack_channel = "C08RABUFRD0"
        
        # 이메일 설정 - 환경변수 우선 사용
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': os.getenv('EMAIL_ADDRESS', 'your-email@gmail.com'),
            'sender_password': os.getenv('EMAIL_PASSWORD', 'your-app-password'),
            'recipient_email': 'info@vvckd.ai'
        }
        
        # Slack 클라이언트 초기화
        if not self.test_mode:
            try:
                self.slack_client = WebClient(token=self.slack_token)
                # 토큰 테스트
                response = self.slack_client.auth_test()
                logger.info(f"Slack 연결 성공: {response['user']}")
            except Exception as e:
                logger.error(f"Slack 연결 실패: {e}")
                self.slack_client = None
        else:
            self.slack_client = None
            logger.info("테스트 모드: Slack 연결 건너뜀")
    
    def format_slack_message_from_json(self, news_data: Dict) -> str:
        """JSON 구조에서 Slack 메시지 포맷팅"""
        
        # 헤더
        current_date = datetime.now().strftime('%Y년 %m월 %d일')
        message = f"🎵 음악 업계 뉴스 브리핑 - {current_date}\n\n"
        
        # 메타데이터
        metadata = news_data.get('metadata', {})
        total_news = metadata.get('total_news', 0)
        message += f"📊 총 {total_news}개 뉴스\n\n"
        
        # 카테고리 이모지 매핑
        category_emojis = {
            'NEWS': '📰',
            'REPORT': '📈',
            'INSIGHT': '🔍',
            'INTERVIEW': '🎤',
            'COLUMN': '✍️'
        }
        
        # 카테고리별 뉴스 추가
        news_items = news_data.get('news', {})
        news_count = 0
        
        for category, emoji in category_emojis.items():
            if category in news_items and news_items[category]:
                message += f"{emoji} {category}\n"
                
                for news in news_items[category]:
                    news_count += 1
                    title = news.get('title', '')
                    url = news.get('url', '')  # JSON에서는 url 필드
                    source = news.get('source', '')
                    summary = news.get('summary', '')  # JSON에서는 summary 필드
                    tags = news.get('tags', {})
                    published_date = news.get('published_date', '')
                    
                    # 태그 문자열 생성 (장르/업계 우선, 없으면 지역)
                    tag_parts = []
                    if tags.get('genre'):
                        tag_parts.extend(tags['genre'])
                    if tags.get('industry'):
                        tag_parts.extend(tags['industry'])
                    if not tag_parts and tags.get('region'):
                        tag_parts.extend(tags['region'])
                    
                    tag_text = " ".join(tag_parts) if tag_parts else ""
                    
                    # 요약 길이 제한 (슬랙 메시지 길이 고려)
                    if summary and len(summary) > 200:
                        summary = summary[:197] + "..."
                    
                    message += f"{news_count}. {title}\n"
                    if summary:
                        message += f"_{summary}_\n"  # 요약을 이탤릭체로
                    message += f"{published_date} | {url}\n"
                    if tag_text:
                        message += f"{tag_text}\n"
                    message += "\n"
        
        return message
    
    def format_slack_message(self, news_list: List[Dict]) -> str:
        """기존 리스트 형식 지원 (하위 호환성)"""
        
        # 헤더
        message = f"음악 업계 뉴스 브리핑 - {datetime.now().strftime('%Y년 %m월 %d일')}\n"
        
        # 카테고리별로 그룹화
        categorized_news = {}
        for news in news_list:
            category = news.get('category', 'NEWS')
            if category not in categorized_news:
                categorized_news[category] = []
            categorized_news[category].append(news)
        
        # 카테고리 이모지 매핑
        category_emojis = {
            'NEWS': ':newspaper:',
            'REPORT': ':bar_chart:',
            'INSIGHT': ':bulb:',
            'INTERVIEW': ':microphone2:',
            'COLUMN': ':writing_hand:'
        }
        
        # 카테고리별 뉴스 추가
        for category, news_items in categorized_news.items():
            emoji = category_emojis.get(category, ':newspaper:')
            message += f"{emoji} {category}\n"
            
            for i, news in enumerate(news_items, 1):
                title = news.get('title', '')
                link = news.get('link', news.get('url', ''))  # link 또는 url 필드
                source = news.get('source', '')
                summary = news.get('summary_5w1h', news.get('summary', ''))  # 둘 다 지원
                tags = news.get('tags', {})
                published_date = news.get('published_date', '')
                
                # 태그 문자열 생성 (장르/업계 우선, 없으면 지역)
                tag_parts = []
                if tags.get('genre'):
                    tag_parts.extend(tags['genre'])
                if tags.get('industry'):
                    tag_parts.extend(tags['industry'])
                if not tag_parts and tags.get('region'):
                    tag_parts.extend(tags['region'])
                
                tag_text = " ".join(tag_parts) if tag_parts else ""
                
                message += f"{i}. {title}\n"
                if summary:
                    message += f"{summary}\n"
                message += f":date: {published_date} | :link: {link}\n"
                if tag_text:
                    message += f"{tag_text}\n"
                message += "\n"
        
        return message
    
    def format_email_html_from_json(self, news_data: Dict) -> str:
        """JSON 구조에서 이메일 HTML 포맷팅"""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; }}
                .header {{ background-color: #1a1a1a; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                .category {{ margin: 20px 0; }}
                .category-title {{ background-color: #333; color: white; padding: 10px; border-radius: 5px; font-weight: bold; }}
                .news-item {{ border-left: 4px solid #007cba; padding: 15px; margin: 10px 0; background-color: #f9f9f9; }}
                .news-title {{ font-weight: bold; font-size: 16px; margin-bottom: 5px; }}
                .news-meta {{ color: #666; font-size: 12px; margin-bottom: 10px; }}
                .news-summary {{ margin-bottom: 10px; line-height: 1.5; }}
                .news-tags {{ background-color: #e9e9e9; padding: 5px; border-radius: 3px; font-size: 11px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎵 음악 업계 뉴스 브리핑</h1>
                    <p>{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</p>
                </div>
        """
        
        # 메타데이터
        metadata = news_data.get('metadata', {})
        total_news = metadata.get('total_news', 0)
        
        # 카테고리별 뉴스 추가
        news_items = news_data.get('news', {})
        
        for category, news_list in news_items.items():
            if news_list:
                html += f'<div class="category">'
                html += f'<div class="category-title">{category} ({len(news_list)}개)</div>'
                
                for news in news_list:
                    title = news.get('title', '')
                    url = news.get('url', '')
                    source = news.get('source', '')
                    summary = news.get('summary', '')
                    tags = news.get('tags', {})
                    importance = news.get('importance_score', 0)
                    published_date = news.get('published_date', '')
                    
                    # 태그 문자열 생성
                    tag_strings = []
                    for tag_type, tag_list in tags.items():
                        if tag_list:
                            tag_strings.append(f"<strong>{tag_type}:</strong> {', '.join(tag_list[:3])}")
                    
                    tag_text = " | ".join(tag_strings) if tag_strings else "태그 없음"
                    
                    html += f'''
                    <div class="news-item">
                        <div class="news-title"><a href="{url}" target="_blank">{title}</a></div>
                        <div class="news-meta">📍 {source} | 📅 {published_date} | ⭐ 중요도: {importance:.2f}</div>
                        <div class="news-summary">{summary}</div>
                        <div class="news-tags">{tag_text}</div>
                    </div>
                    '''
                
                html += '</div>'
        
        # 푸터
        html += f'''
                <div class="footer">
                    <p>📊 총 {total_news}개 뉴스 | 🤖 자동 수집 및 분류</p>
                    <p>⏰ 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        return html
    
    def format_email_html(self, news_list: List[Dict]) -> str:
        """기존 리스트 형식 지원 (하위 호환성)"""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; }}
                .header {{ background-color: #1a1a1a; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                .category {{ margin: 20px 0; }}
                .category-title {{ background-color: #333; color: white; padding: 10px; border-radius: 5px; font-weight: bold; }}
                .news-item {{ border-left: 4px solid #007cba; padding: 15px; margin: 10px 0; background-color: #f9f9f9; }}
                .news-title {{ font-weight: bold; font-size: 16px; margin-bottom: 5px; }}
                .news-meta {{ color: #666; font-size: 12px; margin-bottom: 10px; }}
                .news-summary {{ margin-bottom: 10px; }}
                .news-tags {{ background-color: #e9e9e9; padding: 5px; border-radius: 3px; font-size: 11px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎵 음악 업계 뉴스 브리핑</h1>
                    <p>{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</p>
                </div>
        """
        
        # 카테고리별로 그룹화
        categorized_news = {}
        for news in news_list:
            category = news.get('category', 'NEWS')
            if category not in categorized_news:
                categorized_news[category] = []
            categorized_news[category].append(news)
        
        # 카테고리별 뉴스 추가
        for category, news_items in categorized_news.items():
            html += f'<div class="category">'
            html += f'<div class="category-title">{category} ({len(news_items)}개)</div>'
            
            for news in news_items:
                title = news.get('title', '')
                link = news.get('link', news.get('url', ''))
                source = news.get('source', '')
                summary = news.get('summary_5w1h', news.get('summary', ''))
                tags = news.get('tags', {})
                importance = news.get('importance_score', 0)
                
                # 태그 문자열 생성
                tag_strings = []
                for tag_type, tag_list in tags.items():
                    if tag_list:
                        tag_strings.append(f"<strong>{tag_type}:</strong> {', '.join(tag_list[:3])}")
                
                tag_text = " | ".join(tag_strings) if tag_strings else "태그 없음"
                
                html += f'''
                <div class="news-item">
                    <div class="news-title"><a href="{link}" target="_blank">{title}</a></div>
                    <div class="news-meta">📍 {source} | ⭐ 중요도: {importance:.2f}</div>
                    <div class="news-summary">{summary}</div>
                    <div class="news-tags">{tag_text}</div>
                </div>
                '''
            
            html += '</div>'
        
        # 푸터
        html += f'''
                <div class="footer">
                    <p>📊 총 {len(news_list)}개 뉴스 | 🤖 자동 수집 및 분류</p>
                    <p>⏰ 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        return html
    
    def send_slack_message(self, news_data) -> bool:
        """Slack 메시지 발송 (JSON 구조와 리스트 구조 모두 지원)"""
        if self.test_mode:
            logger.info("테스트 모드: Slack 메시지 발송 시뮬레이션")
            
            # JSON 구조인지 리스트 구조인지 판단
            if isinstance(news_data, dict) and 'news' in news_data:
                message = self.format_slack_message_from_json(news_data)
            else:
                message = self.format_slack_message(news_data)
                
            print("=== Slack 메시지 미리보기 ===")
            print(message[:1000] + "..." if len(message) > 1000 else message)
            return True
        
        if not self.slack_client:
            logger.error("Slack 클라이언트가 초기화되지 않음")
            return False
        
        try:
            # JSON 구조인지 리스트 구조인지 판단
            if isinstance(news_data, dict) and 'news' in news_data:
                message = self.format_slack_message_from_json(news_data)
            else:
                message = self.format_slack_message(news_data)
            
            # 메시지가 너무 길면 분할 발송
            max_length = 4000  # Slack 메시지 길이 제한
            
            if len(message) <= max_length:
                response = self.slack_client.chat_postMessage(
                    channel=self.slack_channel,
                    text=message,
                    mrkdwn=True
                )
                logger.info(f"Slack 메시지 발송 성공: {response['ts']}")
            else:
                # 메시지 분할
                parts = []
                current_part = ""
                lines = message.split('\n')
                
                for line in lines:
                    if len(current_part + line + '\n') > max_length:
                        if current_part:
                            parts.append(current_part)
                            current_part = line + '\n'
                        else:
                            parts.append(line[:max_length])
                    else:
                        current_part += line + '\n'
                
                if current_part:
                    parts.append(current_part)
                
                # 분할된 메시지 발송
                for i, part in enumerate(parts):
                    response = self.slack_client.chat_postMessage(
                        channel=self.slack_channel,
                        text=f"[{i+1}/{len(parts)}]\n{part}",
                        mrkdwn=True
                    )
                    logger.info(f"Slack 메시지 {i+1}/{len(parts)} 발송 성공")
            
            return True
            
        except SlackApiError as e:
            logger.error(f"Slack 메시지 발송 실패: {e.response['error']}")
            return False
        except Exception as e:
            logger.error(f"Slack 메시지 발송 오류: {e}")
            return False
    
    def send_email(self, news_data) -> bool:
        """이메일 발송 (JSON 구조와 리스트 구조 모두 지원)"""
        if self.test_mode:
            logger.info("테스트 모드: 이메일 발송 시뮬레이션")
            
            # JSON 구조인지 리스트 구조인지 판단
            if isinstance(news_data, dict) and 'news' in news_data:
                html_content = self.format_email_html_from_json(news_data)
            else:
                html_content = self.format_email_html(news_data)
                
            print("=== 이메일 HTML 미리보기 ===")
            print(html_content[:500] + "..." if len(html_content) > 500 else html_content)
            return True
        
        try:
            # 이메일 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"음악 업계 뉴스 브리핑 - {datetime.now().strftime('%Y.%m.%d')}"
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            
            # JSON 구조인지 리스트 구조인지 판단
            if isinstance(news_data, dict) and 'news' in news_data:
                html_content = self.format_email_html_from_json(news_data)
            else:
                html_content = self.format_email_html(news_data)
                
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # SMTP 서버 연결 및 발송
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['sender_email'], self.email_config['sender_password'])
                server.send_message(msg)
            
            logger.info(f"이메일 발송 성공: {self.email_config['recipient_email']}")
            return True
            
        except Exception as e:
            logger.error(f"이메일 발송 실패: {e}")
            return False
    
    def deliver_news(self, news_data) -> Dict[str, bool]:
        """뉴스 발송 (Slack + 이메일) - JSON 구조와 리스트 구조 모두 지원"""
        results = {
            'slack_success': False,
            'email_success': False
        }
        
        # 뉴스 개수 계산
        if isinstance(news_data, dict) and 'news' in news_data:
            total_news = sum(len(category_news) for category_news in news_data['news'].values())
        else:
            total_news = len(news_data) if isinstance(news_data, list) else 0
            
        logger.info(f"{total_news}개 뉴스 발송 시작")
        
        # Slack 발송
        try:
            results['slack_success'] = self.send_slack_message(news_data)
        except Exception as e:
            logger.error(f"Slack 발송 중 오류: {e}")
        
        # 이메일 발송
        try:
            results['email_success'] = self.send_email(news_data)
        except Exception as e:
            logger.error(f"이메일 발송 중 오류: {e}")
        
        # 결과 로깅
        success_count = sum(results.values())
        logger.info(f"발송 완료: {success_count}/2 성공")
        
        if success_count == 0:
            logger.error("모든 발송 채널 실패")
        elif success_count == 1:
            logger.warning("일부 발송 채널 실패")
        else:
            logger.info("모든 발송 채널 성공")
        
        return results

    def send_news(self, news_data) -> Dict[str, bool]:
        """뉴스 발송 (deliver_news의 별칭)"""
        return self.deliver_news(news_data)

if __name__ == "__main__":
    # 테스트용 JSON 구조 뉴스
    sample_json_news = {
        "metadata": {"total_news": 2},
        "news": {
            "NEWS": [
                {
                    'title': 'Taylor Swift Announces New Album',
                    'summary': 'Who: Taylor Swift\nWhat: announces new album\nWhen: recently',
                    'url': 'https://example.com/news1',
                    'source': 'billboard.com',
                    'tags': {'genre': ['POP'], 'industry': ['LABEL'], 'region': []},
                    'importance_score': 0.9,
                    'published_date': '2025-07-04 10:00:00'
                }
            ]
        }
    }
    
    # 테스트 모드로 실행
    delivery_system = NewsDeliverySystem(test_mode=True)
    results = delivery_system.deliver_news(sample_json_news)
    print(f"발송 결과: {results}")
