#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理画面 - Flask アプリケーション
"""

import sys
import os
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, redirect, url_for, flash
from src.config import load_json, save_json

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')


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
def history():
    try:
        posts = load_json('history.json')['posts']
    except Exception:
        posts = []
    return render_template('history.html', posts=posts)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
