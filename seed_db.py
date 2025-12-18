# seed_db.py
"""
サンプルデータ投入スクリプト
"""
import uuid
import json
from datetime import datetime, timedelta
import bcrypt

from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.job import Job, JobStatus, EmploymentType
from app.models.application import Application, ApplicationStatus
from app.models.scout import Scout, ScoutStatus


def hash_password(password: str) -> str:
    """パスワードをハッシュ化"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def seed_db():
    """サンプルデータを投入"""
    db = SessionLocal()

    try:
        print("Seeding database...")

        # ユーザー作成（求職者）
        seeker1 = User(
            id=str(uuid.uuid4()),
            email="seeker@example.com",
            password_hash=hash_password("password"),
            name="山田太郎",
            role=UserRole.SEEKER,
            skills=json.dumps(["React", "TypeScript", "Node.js"]),
            experience_years="5年",
            desired_salary_min="500万円",
            desired_salary_max="800万円",
            desired_location="東京都",
            desired_employment_type="正社員",
            profile_completion="75",
        )
        db.add(seeker1)

        # ユーザー作成（企業）
        employer1 = User(
            id=str(uuid.uuid4()),
            email="employer@example.com",
            password_hash=hash_password("password"),
            name="採用担当者",
            role=UserRole.EMPLOYER,
            company_name="株式会社テックカンパニー",
            industry="IT・インターネット",
            company_size="51-200名",
            company_location="東京都渋谷区",
        )
        db.add(employer1)

        db.commit()

        # 求人作成
        jobs_data = [
            {
                "id": str(uuid.uuid4()),
                "employer_id": employer1.id,
                "title": "フロントエンドエンジニア",
                "company": "株式会社テックカンパニー",
                "description": "自社プロダクトの開発を担当していただきます。最新技術を活用した開発環境で、チームと協力しながらユーザー体験を向上させるプロダクト開発をお任せします。",
                "location": "東京都渋谷区",
                "employment_type": EmploymentType.FULL_TIME,
                "salary_min": 500,
                "salary_max": 800,
                "salary_text": "500万円～800万円",
                "required_skills": json.dumps(["React", "TypeScript", "チーム開発経験"]),
                "preferred_skills": json.dumps(["Next.js", "GraphQL"]),
                "requirements": "・React 2年以上の実務経験\n・TypeScript経験\n・チーム開発経験",
                "benefits": "・フルリモート可\n・フレックスタイム\n・副業OK\n・書籍購入補助",
                "tags": json.dumps(["React", "TypeScript", "Next.js", "フルリモート可"]),
                "remote": True,
                "status": JobStatus.PUBLISHED,
                "featured": True,
                "posted_date": datetime.now() - timedelta(days=5),
            },
            {
                "id": str(uuid.uuid4()),
                "employer_id": employer1.id,
                "title": "バックエンドエンジニア",
                "company": "合同会社クラウドソリューション",
                "description": "クラウドサービスのバックエンド開発をお任せします。スケーラブルなアーキテクチャ設計から実装まで、幅広い業務に携わっていただきます。",
                "location": "東京都港区",
                "employment_type": EmploymentType.FULL_TIME,
                "salary_min": 600,
                "salary_max": 900,
                "salary_text": "600万円～900万円",
                "required_skills": json.dumps(["Python", "AWS", "API設計経験"]),
                "preferred_skills": json.dumps(["Django", "Docker", "Kubernetes"]),
                "requirements": "・Python 3年以上の実務経験\n・AWS経験\n・API設計経験",
                "benefits": "・リモート週2-3日\n・ストックオプション\n・書籍購入補助",
                "tags": json.dumps(["Python", "Django", "AWS", "ハイブリッド"]),
                "remote": True,
                "status": JobStatus.PUBLISHED,
                "featured": True,
                "posted_date": datetime.now() - timedelta(days=4),
            },
            {
                "id": str(uuid.uuid4()),
                "employer_id": employer1.id,
                "title": "フルスタックエンジニア",
                "company": "スタートアップ株式会社",
                "description": "少数精鋭のチームで新規サービス開発を担当。フロントエンドからバックエンドまで幅広く担当していただきます。",
                "location": "大阪府大阪市",
                "employment_type": EmploymentType.FULL_TIME,
                "salary_min": 450,
                "salary_max": 700,
                "salary_text": "450万円～700万円",
                "required_skills": json.dumps(["Webアプリ開発経験", "フロント・バックエンド両方の経験"]),
                "preferred_skills": json.dumps(["Vue.js", "Node.js", "MongoDB"]),
                "requirements": "・Webアプリ開発経験2年以上\n・フロント・バックエンド両方の経験",
                "benefits": "・フルリモート\n・裁量大\n・ストックオプション",
                "tags": json.dumps(["Vue.js", "Node.js", "MongoDB", "スタートアップ"]),
                "remote": True,
                "status": JobStatus.PUBLISHED,
                "featured": False,
                "posted_date": datetime.now() - timedelta(days=3),
            },
            {
                "id": str(uuid.uuid4()),
                "employer_id": employer1.id,
                "title": "モバイルアプリエンジニア",
                "company": "株式会社モバイルイノベーション",
                "description": "自社アプリの開発・運用をお任せします。ユーザーに愛されるアプリを一緒に作りましょう。",
                "location": "東京都新宿区",
                "employment_type": EmploymentType.FULL_TIME,
                "salary_min": 550,
                "salary_max": 850,
                "salary_text": "550万円～850万円",
                "required_skills": json.dumps(["React Native", "iOS or Android開発経験"]),
                "preferred_skills": json.dumps(["Swift", "Kotlin"]),
                "requirements": "・React Native経験1年以上\n・iOS or Android開発経験",
                "benefits": "・社員食堂\n・資格取得補助\n・交通費全額支給",
                "tags": json.dumps(["React Native", "iOS", "Android", "出社"]),
                "remote": False,
                "status": JobStatus.PUBLISHED,
                "featured": False,
                "posted_date": datetime.now() - timedelta(days=2),
            },
        ]

        for job_data in jobs_data:
            job = Job(**job_data)
            db.add(job)

        db.commit()

        # 応募作成（サンプル）
        application1 = Application(
            id=str(uuid.uuid4()),
            seeker_id=seeker1.id,
            job_id=jobs_data[0]["id"],
            status=ApplicationStatus.INTERVIEW,
            status_detail="一次面接待ち",
            status_color="blue",
            match_score=92,
            next_step="一次面接",
            interview_date=datetime.now() + timedelta(days=7),
            resume_submitted="true",
            portfolio_submitted="true",
            cover_letter="貴社の革新的なプロダクト開発に強く惹かれ、応募させていただきました。",
        )
        db.add(application1)

        # スカウト作成（サンプル）
        scout1 = Scout(
            id=str(uuid.uuid4()),
            employer_id=employer1.id,
            seeker_id=seeker1.id,
            job_id=jobs_data[0]["id"],
            title="フロントエンドエンジニア募集",
            message="あなたのReactスキルに興味があります。ぜひ一度お話しさせてください。",
            match_score=95,
            status=ScoutStatus.NEW,
            tags=json.dumps(["React", "TypeScript", "フルリモート"]),
        )
        db.add(scout1)

        db.commit()

        print("Database seeded successfully!")
        print("\n=== サンプルユーザー ===")
        print(f"求職者: seeker@example.com / password")
        print(f"企業: employer@example.com / password")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
