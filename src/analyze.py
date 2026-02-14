#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude APIで投稿分析・ツイート生成
"""

import anthropic
from src.config import ANTHROPIC_API_KEY
from src.logger import get_logger

logger = get_logger(__name__)


class PostAnalyzer:
    """Claude APIによる投稿分析・ツイート生成"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        logger.info("Claude API初期化完了")

    def analyze_and_generate(self, posts_by_genre, genres):
        """
        収集した投稿を分析してツイートを生成

        Args:
            posts_by_genre: ジャンル別投稿 {"stocks": [posts], ...}
            genres: ジャンル定義リスト

        Returns:
            生成されたツイート文（280文字以内）
        """
        # ジャンル名のマッピング
        genre_names = {g['id']: g['name'] for g in genres}

        # 投稿をまとめてプロンプト用テキストにする
        collected_text = ""
        for genre_id, posts in posts_by_genre.items():
            genre_name = genre_names.get(genre_id, genre_id)
            collected_text += f"\n【{genre_name}】\n"
            for post in posts:
                collected_text += f"@{post['username']}: {post['text']}\n"

        if not collected_text.strip():
            logger.warning("分析する投稿がありません")
            return None

        prompt = f"""以下はXで影響力のあるアカウントの最新投稿です。
これらを分析して、今のトレンドや注目ポイントをまとめた投稿を1つ生成してください。

ルール:
- 日本語で書く
- 280文字以内に収める（厳守）
- 情報を簡潔にまとめ、読者に価値のある内容にする
- 絵文字を適度に使って読みやすくする
- ハッシュタグを2〜3個つける
- 出典のアカウント名は入れなくてよい
- 自然な投稿文にする（AIっぽさを出さない）

収集した投稿:
{collected_text}

ツイート文のみを出力してください。"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )

            tweet = response.content[0].text.strip()

            # 280文字チェック
            if len(tweet) > 280:
                logger.warning(f"生成文が{len(tweet)}文字。再生成します")
                return self._retry_shorter(tweet)

            logger.info(f"ツイート生成完了（{len(tweet)}文字）")
            return tweet

        except Exception as e:
            logger.error(f"Claude API エラー: {e}")
            return None

    def _retry_shorter(self, long_tweet):
        """280文字以内に短縮"""
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": f"以下のツイートを280文字以内に短縮してください。意味は保ったまま簡潔にしてください。ツイート文のみを出力してください。\n\n{long_tweet}"},
                ],
            )
            tweet = response.content[0].text.strip()
            if len(tweet) <= 280:
                return tweet
            # それでも長い場合は先頭280文字で切る
            return tweet[:277] + "..."
        except Exception as e:
            logger.error(f"短縮リトライエラー: {e}")
            return long_tweet[:277] + "..."
