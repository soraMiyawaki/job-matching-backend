"""
簡易モックAPIサーバー
フロントエンドの動作確認用
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime

app = FastAPI(title="Job Matching Mock API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# インメモリストレージ
users_db = {}
tokens_db = {}


# --- モデル定義 ---
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LineAuthData(BaseModel):
    lineUserId: str
    lineDisplayName: str
    linePictureUrl: Optional[str] = None
    lineEmail: Optional[str] = None


class User(BaseModel):
    id: str
    email: str
    name: str
    lineUserId: Optional[str] = None
    lineDisplayName: Optional[str] = None
    linePictureUrl: Optional[str] = None
    role: str
    createdAt: str


class AuthResponse(BaseModel):
    user: User
    token: str


# --- エンドポイント ---
@app.get("/")
def root():
    return {"message": "Job Matching Mock API Server", "status": "running"}


@app.post("/api/auth/register", response_model=AuthResponse)
def register(data: RegisterRequest):
    """新規登録"""
    print(f"[DEBUG] Register request received: email={data.email}, name={data.name}, role={data.role}")

    # メールアドレスの重複チェック
    if data.email in users_db:
        raise HTTPException(status_code=400, detail="このメールアドレスは既に登録されています")

    # ユーザー作成
    user_id = str(uuid.uuid4())
    token = f"mock_token_{uuid.uuid4()}"

    user = User(
        id=user_id,
        email=data.email,
        name=data.name,
        role=data.role,
        createdAt=datetime.now().isoformat()
    )

    users_db[data.email] = {
        "user": user,
        "password": data.password  # 本番環境ではハッシュ化必須
    }
    tokens_db[token] = user_id

    return AuthResponse(user=user, token=token)


@app.post("/api/auth/login", response_model=AuthResponse)
def login(data: LoginRequest):
    """ログイン"""
    if data.email not in users_db:
        raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが間違っています")

    user_data = users_db[data.email]
    if user_data["password"] != data.password:
        raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが間違っています")

    token = f"mock_token_{uuid.uuid4()}"
    tokens_db[token] = user_data["user"].id

    return AuthResponse(user=user_data["user"], token=token)


@app.post("/api/auth/line/link", response_model=AuthResponse)
def link_line(data: LineAuthData):
    """LINE連携"""
    # 仮実装：最後に登録されたユーザーにLINE情報を追加
    if not users_db:
        raise HTTPException(status_code=401, detail="ユーザーが見つかりません")

    # 最後のユーザーを取得
    last_user_email = list(users_db.keys())[-1]
    user_data = users_db[last_user_email]

    # LINE情報を更新
    user_data["user"].lineUserId = data.lineUserId
    user_data["user"].lineDisplayName = data.lineDisplayName
    user_data["user"].linePictureUrl = data.linePictureUrl

    token = f"mock_token_{uuid.uuid4()}"
    tokens_db[token] = user_data["user"].id

    return AuthResponse(user=user_data["user"], token=token)


@app.post("/api/auth/line/login", response_model=AuthResponse)
def login_with_line(data: LineAuthData):
    """LINEログイン"""
    # LINE IDでユーザーを検索
    for email, user_data in users_db.items():
        if user_data["user"].lineUserId == data.lineUserId:
            token = f"mock_token_{uuid.uuid4()}"
            tokens_db[token] = user_data["user"].id
            return AuthResponse(user=user_data["user"], token=token)

    raise HTTPException(status_code=404, detail="このLINEアカウントは登録されていません")


@app.get("/api/auth/me", response_model=AuthResponse)
def get_me():
    """現在のユーザー情報取得"""
    # 仮実装：最後に登録されたユーザーを返す
    if not users_db:
        raise HTTPException(status_code=401, detail="認証が必要です")

    last_user_email = list(users_db.keys())[-1]
    user_data = users_db[last_user_email]

    token = f"mock_token_{uuid.uuid4()}"

    return AuthResponse(user=user_data["user"], token=token)


@app.post("/api/auth/logout")
def logout():
    """ログアウト"""
    return {"message": "ログアウトしました"}


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Mock API Server Starting...")
    print("=" * 60)
    print("URL: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
