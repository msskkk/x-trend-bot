#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ロガー設定
"""

import logging
import os
from datetime import datetime

# ログディレクトリ
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# ログファイル名（日付ごと）
LOG_FILE = os.path.join(LOG_DIR, f"bot_{datetime.now().strftime('%Y%m%d')}.log")

# ログフォーマット
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def get_logger(name):
    """
    ロガーを取得
    
    Args:
        name: ロガー名
        
    Returns:
        logger: ロガーインスタンス
    """
    logger = logging.getLogger(name)
    
    # 既に設定済みの場合はそのまま返す
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # コンソールハンドラ
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    
    # ファイルハンドラ
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # ハンドラを追加
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


if __name__ == "__main__":
    # テスト実行
    logger = get_logger(__name__)
    
    logger.debug("これはDEBUGメッセージです")
    logger.info("これはINFOメッセージです")
    logger.warning("これはWARNINGメッセージです")
    logger.error("これはERRORメッセージです")
    logger.critical("これはCRITICALメッセージです")
    
    print(f"\n✅ ログファイル: {LOG_FILE}")
