#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定ファイル読み込み
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

# X API認証情報
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_SECRET = os.getenv('ACCESS_SECRET')

# Claude API
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# 投稿設定
TWEETS_PER_USER = int(os.getenv('TWEETS_PER_USER', '5'))
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'

# パス
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')


def load_json(filename):
    """config/配下のJSONファイルを読み込む"""
    path = os.path.join(CONFIG_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filename, data):
    """config/配下のJSONファイルに保存"""
    path = os.path.join(CONFIG_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_users():
    """有効な監視ユーザーを取得"""
    data = load_json('users.json')
    return [u for u in data['users'] if u.get('enabled', True)]


def load_genres():
    """有効なジャンルを取得"""
    data = load_json('genres.json')
    return [g for g in data['genres'] if g.get('enabled', True)]


def validate_config():
    """設定の検証"""
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
        raise ValueError("X API認証情報が設定されていません。")
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEYが設定されていません。")
    return True
