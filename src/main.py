#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メイン実行スクリプト
監視ユーザーの投稿取得 → Claude分析 → ツイート自動投稿
"""

import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import validate_config, load_users, load_genres, load_json, save_json
from src.fetch_posts import PostFetcher
from src.analyze import PostAnalyzer
from src.post_tweet import TweetPoster
from src.logger import get_logger

logger = get_logger(__name__)


def save_history(tweet_text, genre_ids):
    """投稿履歴を保存"""
    try:
        data = load_json('history.json')
    except Exception:
        data = {'posts': []}

    data['posts'].insert(0, {
        'text': tweet_text,
        'genres': genre_ids,
        'posted_at': datetime.now().isoformat(),
    })

    # 最新100件のみ保持
    data['posts'] = data['posts'][:100]
    save_json('history.json', data)


def main():
    """メイン処理"""
    logger.info("=" * 50)
    logger.info("Bot起動")
    logger.info("=" * 50)

    try:
        validate_config()
        logger.info("設定の検証完了")

        # ステップ1: 設定読み込み
        users = load_users()
        genres = load_genres()

        if not users:
            logger.warning("監視ユーザーが登録されていません")
            return False

        logger.info(f"監視ユーザー: {len(users)}人")

        # ステップ2: 投稿取得
        logger.info("投稿取得中...")
        fetcher = PostFetcher()
        posts_by_genre = fetcher.fetch_all_users_posts(users)

        if not posts_by_genre:
            logger.warning("取得できた投稿がありません")
            return False

        # ステップ3: Claude APIで分析・ツイート生成
        logger.info("投稿分析・ツイート生成中...")
        analyzer = PostAnalyzer()
        tweet_text = analyzer.analyze_and_generate(posts_by_genre, genres)

        if not tweet_text:
            logger.error("ツイート生成に失敗")
            return False

        logger.info(f"生成されたツイート:\n{tweet_text}")

        # ステップ4: 投稿
        logger.info("投稿実行中...")
        poster = TweetPoster()
        result = poster.safe_post_tweet(tweet_text)

        if result:
            save_history(tweet_text, list(posts_by_genre.keys()))
            logger.info("投稿成功！")
            return True
        else:
            logger.error("投稿失敗")
            return False

    except Exception as e:
        logger.error(f"エラー: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
