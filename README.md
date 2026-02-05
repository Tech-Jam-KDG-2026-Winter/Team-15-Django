コンディション・パートナー（Condition Partner）

概要

コンディション・パートナーは、
ユーザーの「疲れ」「気分」「体の悩み」に応じて、
その日に最適な運動メニュー（ストレッチ・軽い運動など）を提案する Web アプリケーションです。

運動が苦手な人や、何をすれば良いか分からない人でも
無理なく健康習慣を続けられることを目的としています。

⸻

主な機能

ユーザー向け機能
	•	体調ログ入力（疲れ・気分・体の悩み）
	•	体調に応じた運動メニューの自動提案
	•	運動メニュー詳細表示
	•	ルーティン（お気に入り）登録・削除
	•	体調ログ履歴の確認
    •	運動メニュー一覧、検索

管理者向け機能
	•	Django 管理画面による運動メニュー・タグ管理

技術スタック
バックエンド
Python / Django / Django REST Framework
フロントエンド
HTML / CSS / JavaScript
データベース
SQLite（開発用）
認証
Django 標準認証
バージョン管理
Git / GitHub

画面構成
	•	/ トップページ（体調入力・おすすめ表示）
	•	/history/ 体調ログ履歴
	•	/routines/ ルーティン一覧
	•	/exercises/<id>/ 運動メニュー詳細
    •	/exercises/運動メニュー一覧
	•	/admin/ 管理者画面（Django admin）


# Django Team Starter

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install django==6.0.1
python manage.py migrate
python manage.py runserver
```

## Endpoints
- /           root check
- /healthz/   health check
- /admin/     django admin
