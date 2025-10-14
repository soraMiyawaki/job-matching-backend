# app/services/openai_service.py
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
import json

from app.core.config import Settings
from app.core.exceptions import OpenAIError

logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI API統合サービス"""

    def __init__(self, settings: Settings):
        """
        Args:
            settings: アプリケーション設定
        """
        if not settings.openai_api_key:
            raise OpenAIError("OPENAI_API_KEY is not configured")

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.embedding_model = settings.openai_embedding_model
        self.chat_model = settings.openai_chat_model
        self.embedding_dimension = settings.openai_embedding_dimension

    def create_embedding(self, text: str) -> List[float]:
        """
        テキストをベクトル化（エンベディング）

        Args:
            text: エンベディング化するテキスト

        Returns:
            エンベディングベクトル（1536次元）
        """
        try:
            # 空のテキストをチェック
            if not text or not text.strip():
                logger.warning("Empty text provided for embedding")
                return [0.0] * self.embedding_dimension

            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )

            embedding = response.data[0].embedding
            logger.debug(f"Created embedding of dimension {len(embedding)}")

            return embedding

        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            raise OpenAIError(f"Failed to create embedding: {str(e)}", details={"text": text[:100]})

    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        複数のテキストを一括でエンベディング化

        Args:
            texts: エンベディング化するテキストのリスト

        Returns:
            エンベディングベクトルのリスト
        """
        try:
            # 空のテキストをフィルタリング
            valid_texts = [text if text and text.strip() else " " for text in texts]

            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=valid_texts
            )

            embeddings = [item.embedding for item in response.data]
            logger.debug(f"Created {len(embeddings)} embeddings")

            return embeddings

        except Exception as e:
            logger.error(f"Error creating embeddings batch: {e}")
            raise

    def extract_job_preferences(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        会話履歴から求人条件を抽出

        Args:
            conversation_history: 会話履歴（role, contentのリスト）

        Returns:
            抽出された条件の辞書
        """
        try:
            system_prompt = """
あなたは転職エージェントのAIアシスタントです。
ユーザーとの会話から、以下の求人条件を可能な限り詳細に抽出してください：

【希望条件（ポジティブ）】
- location: 勤務地（複数可、配列で返す。都道府県レベルで）
- salary_min: 最低希望年収（数値、万円単位なら10000倍してください）
- salary_max: 最高希望年収（数値）
- employment_types: 雇用形態（複数可、配列で返す。例: ["正社員", "契約社員"]）
- remote_work: リモートワークの希望（true/false/null）
- job_categories: 希望職種（複数可、配列で返す。「エンジニア」「デザイナー」など）
- skills: スキル・経験（複数可、配列で返す。技術名、ツール名、経験年数などを含む）
- tech_stack: 使いたい技術・言語（配列で返す。React, Python, AWS など）
- industry: 業界の希望（配列で返す。IT、金融、医療など）
- company_size: 企業規模の希望（例: "大企業", "中小企業", "スタートアップ"）
- work_style_preferences: 働き方の希望（配列で返す。例: ["ワークライフバランス", "フレックス"]）
- career_goals: キャリア目標（文字列。できるだけ具体的に）
- priorities: 優先度の高い条件（配列で返す）
- experience_years: 経験年数（数値）

【除外条件（ネガティブ）】
- excluded_job_categories: 避けたい職種（配列で返す。「○○は嫌」「○○以外」などから抽出）
- excluded_skills: 使いたくない技術（配列で返す）
- excluded_industries: 避けたい業界（配列で返す）
- excluded_company_types: 避けたい企業タイプ（配列で返す）

重要：
- 「○○は嫌だ」「○○以外」「○○はやりたくない」などのネガティブな表現は、excluded_○○に分類してください
- 会話の文脈から推測できる情報も積極的に抽出してください
- 明示的に言及されていない項目はnullにしてください
- 必ずJSON形式で返してください
"""

            messages = [
                {"role": "system", "content": system_prompt}
            ] + conversation_history + [
                {"role": "user", "content": "これまでの会話から、私の求人条件を抽出してJSON形式で返してください。"}
            ]

            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.3
            )

            content = response.choices[0].message.content
            preferences = json.loads(content)

            logger.info(f"Extracted preferences: {preferences}")
            return preferences

        except Exception as e:
            logger.error(f"Error extracting job preferences: {e}")
            raise

    def generate_chat_response(
        self,
        conversation_history: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        会話の応答を生成

        Args:
            conversation_history: 会話履歴
            system_prompt: システムプロンプト（オプション）

        Returns:
            生成された応答テキスト
        """
        try:
            default_system_prompt = """
あなたはAEXIT転職のAIキャリアアドバイザーです。
ユーザーの転職活動をサポートし、最適な求人を見つけるお手伝いをします。

以下の点を心がけてください：
1. 親しみやすく、丁寧な口調で対応する
2. ユーザーのキャリア目標や希望条件を自然な会話で引き出す
3. 曖昧な回答には、優しく追加質問をする
4. 具体的な数値や条件は明確に確認する
5. ユーザーの不安や懸念に共感的に対応する

会話を通じて、以下の情報を収集してください：
- 希望の職種・業界
- 勤務地の希望
- 年収の希望範囲
- リモートワークの希望
- スキルや経験
- 働き方の希望
- キャリア目標
"""

            messages = [
                {"role": "system", "content": system_prompt or default_system_prompt}
            ] + conversation_history

            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            reply = response.choices[0].message.content
            logger.debug(f"Generated response: {reply[:100]}...")

            return reply

        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            raise

    def create_search_query_embedding(self, preferences: Dict[str, Any]) -> List[float]:
        """
        抽出された条件からベクトル検索用のクエリを作成

        Args:
            preferences: 抽出された求人条件

        Returns:
            検索クエリのエンベディングベクトル
        """
        try:
            # 条件をテキストに変換（重要度順）
            query_parts = []

            # === ポジティブ条件（含めたいもの） ===

            # 職種（最重要）
            if preferences.get("job_categories"):
                categories = ', '.join(preferences['job_categories'])
                query_parts.append(f"職種: {categories}")
                query_parts.append(categories)  # 重みを増やすため重複追加

            # 技術スタック
            if preferences.get("tech_stack"):
                tech = ', '.join(preferences['tech_stack'])
                query_parts.append(f"技術: {tech}")
                query_parts.append(tech)  # 重みを増やすため重複追加

            # スキル・経験
            if preferences.get("skills"):
                skills = ', '.join(preferences['skills'])
                query_parts.append(f"スキル: {skills}")
                query_parts.append(skills)

            # 業界
            if preferences.get("industry"):
                query_parts.append(f"業界: {', '.join(preferences['industry'])}")

            # キャリア目標
            if preferences.get("career_goals"):
                query_parts.append(f"目標: {preferences['career_goals']}")

            # 働き方
            if preferences.get("work_style_preferences"):
                query_parts.append(f"働き方: {', '.join(preferences['work_style_preferences'])}")

            # 勤務地
            if preferences.get("location"):
                query_parts.append(f"勤務地: {', '.join(preferences['location'])}")

            # 企業規模
            if preferences.get("company_size"):
                query_parts.append(f"企業規模: {preferences['company_size']}")

            # 経験年数
            if preferences.get("experience_years"):
                query_parts.append(f"{preferences['experience_years']}年の経験")

            # === ネガティブ条件（除外したいもの）は検索クエリに含めない ===
            # 除外条件はfilter_by_requirementsで処理されるため、
            # エンベディング検索には含めない（含めるとマッチ度が上がってしまう）

            query_text = " ".join(query_parts)

            if not query_text:
                query_text = "求人検索"

            logger.info(f"Search query text: {query_text}")

            return self.create_embedding(query_text)

        except Exception as e:
            logger.error(f"Error creating search query embedding: {e}")
            raise


# 後方互換性のための非推奨関数（依存性注入を使用することを推奨）
_openai_service = None


def get_openai_service() -> OpenAIService:
    """
    OpenAIServiceのシングルトンインスタンスを取得

    注意: この関数は非推奨です。代わりにFastAPIの依存性注入を使用してください。
    app.core.dependencies.get_openai_service を使用することを推奨します。
    """
    global _openai_service
    if _openai_service is None:
        from app.core.config import get_settings
        settings = get_settings()
        _openai_service = OpenAIService(settings)
    return _openai_service
