#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指定ユーザーの投稿取得モジュール（X API v2）
"""

import tweepy
from src.config import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET, TWEETS_PER_USER
from src.logger import get_logger

logger = get_logger(__name__)


class PostFetcher:
    """ユーザー投稿取得クラス"""

    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET,
        )
        logger.info("X API認証成功")

    def fetch_user_posts(self, username, max_results=None):
        """
        指定ユーザーの最新投稿を取得

        Args:
            username: Xのユーザー名（@なし）
            max_results: 取得件数

        Returns:
            投稿リスト [{"text": ..., "created_at": ..., "username": ...}]
        """
        if max_results is None:
            max_results = TWEETS_PER_USER

        try:
            # ユーザーIDを取得
            user = self.client.get_user(username=username)
            if not user.data:
                logger.warning(f"ユーザーが見つかりません: @{username}")
                return []

            user_id = user.data.id
            display_name = user.data.name

            # 最新の投稿を取得
            tweets = self.client.get_users_tweets(
                user_id,
                max_results=max(max_results, 5),  # API最低5件
                tweet_fields=['created_at', 'public_metrics'],
                exclude=['retweets', 'replies'],
            )

            if not tweets.data:
                logger.info(f"@{username} の投稿が見つかりません")
                return []

            posts = []
            for tweet in tweets.data[:max_results]:
                posts.append({
                    'text': tweet.text,
                    'created_at': str(tweet.created_at) if tweet.created_at else '',
                    'username': username,
                    'display_name': display_name,
                    'metrics': tweet.public_metrics or {},
                })

            logger.info(f"@{username} から {len(posts)}件の投稿を取得")
            return posts

        except Exception as e:
            logger.error(f"@{username} の投稿取得エラー: {e}")
            return []

    def fetch_all_users_posts(self, users):
        """
        複数ユーザーの投稿をまとめて取得

        Args:
            users: ユーザー設定リスト [{"username": ..., "genre": ...}]

        Returns:
            ジャンル別の投稿辞書 {"stocks": [posts], "crypto": [posts]}
        """
        posts_by_genre = {}

        for user in users:
            username = user['username']
            genre = user.get('genre', 'general')

            posts = self.fetch_user_posts(username)
            if posts:
                if genre not in posts_by_genre:
                    posts_by_genre[genre] = []
                posts_by_genre[genre].extend(posts)

        total = sum(len(p) for p in posts_by_genre.values())
        logger.info(f"合計 {total}件の投稿を取得（{len(posts_by_genre)}ジャンル）")
        return posts_by_genre
