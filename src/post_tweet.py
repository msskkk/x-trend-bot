#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投稿実行モジュール
"""

import tweepy
import sys
import os
from datetime import datetime

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET, DRY_RUN
from src.logger import get_logger

logger = get_logger(__name__)

class TweetPoster:
    """投稿実行クラス"""
    
    def __init__(self):
        """初期化"""
        try:
            self.client = tweepy.Client(
                consumer_key=API_KEY,
                consumer_secret=API_SECRET,
                access_token=ACCESS_TOKEN,
                access_token_secret=ACCESS_SECRET
            )
            logger.info("✅ X API認証成功")
        except Exception as e:
            logger.error(f"❌ 認証エラー: {e}")
            raise
    
    def post_tweet(self, text):
        """
        ツイートを投稿
        
        Args:
            text: 投稿文
            
        Returns:
            投稿結果（成功/失敗）
        """
        if not text:
            logger.warning("⚠️ 投稿文が空です")
            return False
        
        # DRY RUNモード
        if DRY_RUN:
            logger.info("🧪 DRY RUNモード: 実際には投稿しません")
            logger.info(f"投稿予定の内容:\n{text}")
            logger.info(f"文字数: {len(text)}")
            return True
        
        try:
            # 投稿実行
            response = self.client.create_tweet(text=text)
            tweet_id = response.data['id']
            
            logger.info(f"✅ 投稿成功！")
            logger.info(f"ツイートID: {tweet_id}")
            logger.info(f"URL: https://twitter.com/user/status/{tweet_id}")
            
            return True
        except tweepy.errors.TweepyException as e:
            logger.error(f"❌ 投稿エラー: {e}")
            
            # エラーの詳細をログに記録
            if hasattr(e, 'response'):
                logger.error(f"レスポンス: {e.response.text}")
            
            return False
        except Exception as e:
            logger.error(f"❌ 予期しないエラー: {e}")
            return False
    
    def validate_tweet(self, text):
        """
        投稿文の検証
        
        Args:
            text: 投稿文
            
        Returns:
            (有効かどうか, エラーメッセージ)
        """
        if not text:
            return False, "投稿文が空です"
        
        if len(text) > 280:
            return False, f"文字数オーバー: {len(text)}文字（最大280文字）"
        
        if len(text.strip()) == 0:
            return False, "投稿文が空白のみです"
        
        return True, "OK"
    
    def safe_post_tweet(self, text):
        """
        検証付きの安全な投稿
        
        Args:
            text: 投稿文
            
        Returns:
            投稿結果（成功/失敗）
        """
        # 検証
        is_valid, error_message = self.validate_tweet(text)
        
        if not is_valid:
            logger.error(f"❌ 検証エラー: {error_message}")
            return False
        
        logger.info(f"📝 投稿文の検証OK（{len(text)}文字）")
        
        # 投稿実行
        return self.post_tweet(text)


if __name__ == "__main__":
    # テスト実行
    poster = TweetPoster()
    
    test_tweet = """📊 投資系トレンド

💰 ビットコイン (12,450ツイート)
📈 日経平均 (8,230ツイート)
🔥 円安 (15,680ツイート)

#投資 #トレンド"""
    
    print("="*50)
    print("📤 投稿テスト")
    print("="*50)
    print(f"\n投稿内容:\n{test_tweet}")
    print(f"\n文字数: {len(test_tweet)}")
    
    # 検証
    is_valid, message = poster.validate_tweet(test_tweet)
    print(f"\n検証結果: {message}")
    
    if is_valid:
        print("\n⚠️  DRY_RUN=trueの場合は実際には投稿されません")
        print("実際に投稿する場合は .env で DRY_RUN=false に設定してください")
        
        # 投稿実行
        result = poster.safe_post_tweet(test_tweet)
        
        if result:
            print("\n✅ 投稿処理完了")
        else:
            print("\n❌ 投稿処理失敗")
