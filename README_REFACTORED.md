# Job Matching API - リファクタリング完了

## 概要

このプロジェクトはFastAPIのベストプラクティスに沿ってリファクタリングされました。

## リファクタリング内容

### 1. プロジェクト構造の改善

```
job-matching-backend/
├── app/
│   ├── __init__.py
│   ├── core/                    # 新規追加
│   │   ├── __init__.py
│   │   ├── config.py           # Pydantic Settings
│   │   ├── dependencies.py      # 依存性注入
│   │   ├── exceptions.py        # カスタム例外
│   │   └── logging.py          # ロギング設定
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints/
│   │       ├── matching.py      # 依存性注入に更新
│   │       └── conversation.py  # 依存性注入に更新
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── embedding_service.py
│   │   ├── matching_service.py
│   │   └── conversation_service.py  # OpenAIServiceに依存
│   ├── services/
│   │   ├── openai_service.py        # Settingsに依存
│   │   ├── conversation_storage.py   # Settingsに依存
│   │   └── vector_search.py
│   └── schemas/
│       └── matching.py
├── data/
├── main.py                     # アプリケーションファクトリパターン
├── .env.example               # 環境変数テンプレート
├── requirements.txt
└── README_REFACTORED.md
```

### 2. 主な変更点

#### 2.1 設定管理の改善 (`app/core/config.py`)
- Pydantic Settingsを使用して環境変数を型安全に管理
- すべての設定を一元管理
- `.env`ファイルから自動読み込み

#### 2.2 依存性注入パターンの実装 (`app/core/dependencies.py`)
- FastAPIの依存性注入を活用
- サービス層のライフサイクル管理を改善
- テストが容易になる設計

#### 2.3 カスタム例外の統一 (`app/core/exceptions.py`)
- 階層的な例外クラス
- エラーハンドリングの一元化
- より詳細なエラー情報

#### 2.4 ロギングの改善 (`app/core/logging.py`)
- 設定可能なログレベル
- 構造化ログ
- サードパーティライブラリのログ制御

#### 2.5 アプリケーションファクトリパターン (`main.py`)
- `create_application()`関数でアプリを生成
- ライフサイクル管理
- グローバル例外ハンドラー
- テスト用の複数インスタンス作成が可能

## セットアップ

### 1. 環境変数の設定

```bash
# .env.exampleをコピーして.envファイルを作成
cp .env.example .env

# .envファイルを編集してOpenAI API Keyを設定
# OPENAI_API_KEY=your-actual-api-key-here
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. アプリケーションの起動

```bash
# 開発モード（自動リロード有効）
python main.py

# または uvicornコマンドで直接起動
uvicorn main:app --host 127.0.0.1 --port 8888 --reload
```

## API エンドポイント

### ヘルスチェック
- `GET /` - ルート情報
- `GET /health` - ヘルスチェック

### マッチング API
- `POST /api/matching/recommend` - 求人レコメンド
- `GET /api/matching/health` - マッチングサービスのヘルスチェック
- `POST /api/matching/analyze-job` - 求人分析
- `POST /api/matching/career-chat` - キャリア相談
- `POST /api/matching/explain-matching` - マッチング説明

### 会話 API
- `POST /api/conversation/chat` - チャット
- `GET /api/conversation/conversations/{user_id}` - 会話履歴取得
- `DELETE /api/conversation/conversations/{user_id}/{conversation_id}` - 会話削除
- `POST /api/conversation/extract-preferences` - 条件抽出

## 開発者向け情報

### 新しい依存性の追加方法

```python
# app/core/dependencies.py に追加
def get_new_service(
    settings: Annotated[Settings, Depends(get_settings_dependency)]
) -> NewService:
    global _new_service
    if _new_service is None:
        _new_service = NewService(settings)
    return _new_service

# 型ヒント用のエイリアスを追加
NewServiceDep = Annotated[NewService, Depends(get_new_service)]
```

### エンドポイントでの依存性注入の使用

```python
from app.core.dependencies import SettingsDep, OpenAIServiceDep

@router.post("/example")
async def example_endpoint(
    settings: SettingsDep,
    openai_service: OpenAIServiceDep
):
    # サービスを直接使用可能
    result = openai_service.create_embedding("text")
    return {"result": result}
```

### カスタム例外の使用

```python
from app.core.exceptions import OpenAIError

def some_function():
    try:
        # 処理
        pass
    except Exception as e:
        raise OpenAIError(
            message="OpenAI API呼び出しに失敗しました",
            details={"error": str(e)}
        )
```

## 後方互換性

既存のコードとの互換性を保つため、古いシングルトン関数(`get_openai_service()`など)は残していますが、新しいコードでは依存性注入の使用を推奨します。

## テストの実行

```bash
# テストの実行
pytest

# カバレッジ付きで実行
pytest --cov=app tests/
```

## 環境変数一覧

主要な環境変数:

- `OPENAI_API_KEY` (必須): OpenAI API Key
- `DEBUG`: デバッグモード (デフォルト: False)
- `LOG_LEVEL`: ログレベル (デフォルト: INFO)
- `HOST`: サーバーホスト (デフォルト: 127.0.0.1)
- `PORT`: サーバーポート (デフォルト: 8888)

詳細は`.env.example`を参照してください。

## トラブルシューティング

### OpenAI API Keyエラー
```
OpenAIError: OPENAI_API_KEY is not configured
```
→ `.env`ファイルに`OPENAI_API_KEY`を設定してください

### インポートエラー
```
ModuleNotFoundError: No module named 'app.core'
```
→ プロジェクトのルートディレクトリから実行していることを確認してください

## 今後の拡張

1. データベース統合 (SQLAlchemy)
2. 認証・認可機能 (JWT)
3. キャッシング (Redis)
4. 非同期タスク処理 (Celery)
5. API レート制限
6. OpenAPI/Swaggerドキュメントの強化

## ライセンス

このプロジェクトは社内利用を目的としています。
