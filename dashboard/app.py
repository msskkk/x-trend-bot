#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理画面 - Flask アプリケーション
"""

import sys
import os
import uuid
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, redirect, url_for, flash
from src.config import load_json, save_json

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Jinja2グローバル関数: サイドバーでジャンル一覧を使用するため
@app.context_processor
def inject_globals():
    try:
        genres = load_json('genres.json')['genres']
    except Exception:
        genres = []
    def load_genres():
        return genres
    return dict(load_genres=load_genres)


# --- ダッシュボード ---

@app.route('/')
def index():
    users = load_json('users.json')['users']
    genres = load_json('genres.json')['genres']
    try:
        history = load_json('history.json')['posts'][:10]
    except Exception:
        history = []

    enabled_users = len([u for u in users if u.get('enabled', True)])
    enabled_genres = len([g for g in genres if g.get('enabled', True)])

    return render_template('index.html',
                           users=users,
                           genres=genres,
                           history=history,
                           enabled_users=enabled_users,
                           enabled_genres=enabled_genres)


# --- ユーザー管理 ---

@app.route('/users')
def users():
    users_data = load_json('users.json')['users']
    genres = load_json('genres.json')['genres']
    return render_template('users.html', users=users_data, genres=genres)


@app.route('/users/add', methods=['POST'])
def add_user():
    username = request.form.get('username', '').strip().lstrip('@')
    display_name = request.form.get('display_name', '').strip()
    genre = request.form.get('genre', '')

    if not username:
        flash('ユーザー名を入力してください', 'error')
        return redirect(url_for('users'))

    data = load_json('users.json')

    # 重複チェック
    if any(u['username'] == username for u in data['users']):
        flash(f'@{username} は既に登録されています', 'error')
        return redirect(url_for('users'))

    data['users'].append({
        'username': username,
        'display_name': display_name or username,
        'genre': genre,
        'enabled': True,
    })
    save_json('users.json', data)
    flash(f'@{username} を追加しました', 'success')
    return redirect(url_for('users'))


@app.route('/users/toggle/<username>', methods=['POST'])
def toggle_user(username):
    data = load_json('users.json')
    for user in data['users']:
        if user['username'] == username:
            user['enabled'] = not user.get('enabled', True)
            break
    save_json('users.json', data)
    return redirect(url_for('users'))


@app.route('/users/delete/<username>', methods=['POST'])
def delete_user(username):
    data = load_json('users.json')
    data['users'] = [u for u in data['users'] if u['username'] != username]
    save_json('users.json', data)
    flash(f'@{username} を削除しました', 'success')
    return redirect(url_for('users'))


# --- ジャンル管理 ---

@app.route('/genres')
def genres():
    genres_data = load_json('genres.json')['genres']
    return render_template('genres.html', genres=genres_data)


@app.route('/genres/add', methods=['POST'])
def add_genre():
    genre_id = request.form.get('genre_id', '').strip()
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not genre_id or not name:
        flash('IDと名前は必須です', 'error')
        return redirect(url_for('genres'))

    data = load_json('genres.json')

    if any(g['id'] == genre_id for g in data['genres']):
        flash(f'ID "{genre_id}" は既に存在します', 'error')
        return redirect(url_for('genres'))

    data['genres'].append({
        'id': genre_id,
        'name': name,
        'description': description,
        'enabled': True,
    })
    save_json('genres.json', data)
    flash(f'ジャンル「{name}」を追加しました', 'success')
    return redirect(url_for('genres'))


@app.route('/genres/toggle/<genre_id>', methods=['POST'])
def toggle_genre(genre_id):
    data = load_json('genres.json')
    for genre in data['genres']:
        if genre['id'] == genre_id:
            genre['enabled'] = not genre.get('enabled', True)
            break
    save_json('genres.json', data)
    return redirect(url_for('genres'))


@app.route('/genres/delete/<genre_id>', methods=['POST'])
def delete_genre(genre_id):
    data = load_json('genres.json')
    name = next((g['name'] for g in data['genres'] if g['id'] == genre_id), genre_id)
    data['genres'] = [g for g in data['genres'] if g['id'] != genre_id]
    save_json('genres.json', data)
    flash(f'ジャンル「{name}」を削除しました', 'success')
    return redirect(url_for('genres'))


# --- 投稿履歴 ---

@app.route('/history')
@app.route('/history/<genre_id>')
def history(genre_id=None):
    genres = load_json('genres.json')['genres']
    try:
        all_posts = load_json('history.json')['posts']
    except Exception:
        all_posts = []

    # ジャンル別フィルタリング
    if genre_id:
        posts = [p for p in all_posts if genre_id in p.get('genres', [])]
        current_genre = next((g for g in genres if g['id'] == genre_id), None)
    else:
        posts = all_posts
        current_genre = None

    # ジャンルごとの件数を集計
    genre_counts = {}
    for g in genres:
        genre_counts[g['id']] = sum(1 for p in all_posts if g['id'] in p.get('genres', []))

    return render_template('history.html',
                           posts=posts,
                           genres=genres,
                           current_genre=current_genre,
                           genre_counts=genre_counts,
                           total_count=len(all_posts))


# --- 新規投稿管理 ---

DRAFTS_FILE = 'drafts.json'


def load_drafts():
    try:
        return load_json(DRAFTS_FILE)
    except Exception:
        return {'drafts': []}


@app.route('/posts')
@app.route('/posts/<tab>')
def posts(tab='drafts'):
    genres = load_json('genres.json')['genres']
    data = load_drafts()
    all_drafts = data.get('drafts', [])

    draft_list = [d for d in all_drafts if d.get('status') == 'draft']
    scheduled_list = [d for d in all_drafts if d.get('status') == 'scheduled']

    return render_template('posts.html',
                           tab=tab,
                           draft_list=draft_list,
                           scheduled_list=scheduled_list,
                           all_drafts=all_drafts,
                           genres=genres)


@app.route('/posts/save_draft', methods=['POST'])
def save_draft():
    text = request.form.get('text', '').strip()
    genre = request.form.get('genre', '')

    if not text:
        flash('テキストを入力してください', 'error')
        return redirect(url_for('posts', tab='drafts'))

    data = load_drafts()
    data['drafts'].append({
        'id': str(uuid.uuid4()),
        'text': text,
        'genre': genre,
        'status': 'draft',
        'created_at': datetime.now().isoformat(),
        'scheduled_at': None,
    })
    save_json(DRAFTS_FILE, data)
    flash('下書きを保存しました', 'success')
    return redirect(url_for('posts', tab='drafts'))


@app.route('/posts/schedule/<draft_id>', methods=['POST'])
def schedule_draft(draft_id):
    scheduled_at = request.form.get('scheduled_at', '')
    data = load_drafts()
    for d in data['drafts']:
        if d['id'] == draft_id:
            d['status'] = 'scheduled'
            d['scheduled_at'] = scheduled_at
            break
    save_json(DRAFTS_FILE, data)
    flash('予約を設定しました', 'success')
    return redirect(url_for('posts', tab='scheduled'))


@app.route('/posts/delete/<draft_id>', methods=['POST'])
def delete_draft(draft_id):
    data = load_drafts()
    data['drafts'] = [d for d in data['drafts'] if d['id'] != draft_id]
    save_json(DRAFTS_FILE, data)
    flash('削除しました', 'success')
    return redirect(url_for('posts', tab='drafts'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
