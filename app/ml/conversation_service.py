# app/ml/conversation_service.py
"""
OpenAI APIを使用した会話型AIマッチングサービス
"""
from typing import List, Dict, Optional
import logging

from app.services.openai_service import OpenAIService
from app.core.exceptions import OpenAIError

logger = logging.getLogger(__name__)


class ConversationService:
    """会話型AIマッチングサービス"""

    def __init__(self, openai_service: OpenAIService):
        """
        Args:
            openai_service: OpenAIサービスインスタンス
        """
        self.openai_service = openai_service
        self.client = openai_service.client
        self.chat_model = openai_service.chat_model

    def generate_job_analysis(
        self,
        seeker_profile: dict,
        job_data: dict,
        match_score: float
    ) -> str:
        """
        OpenAI APIを使って求人とのマッチング分析を生成

        Args:
            seeker_profile: 求職者プロフィール
            job_data: 求人情報
            match_score: マッチスコア

        Returns:
            AI生成の分析テキスト
        """
        if not self.client:
            return "OpenAI APIが設定されていません"

        try:
            # プロンプト作成
            prompt = self._create_analysis_prompt(seeker_profile, job_data, match_score)

            # OpenAI API呼び出し
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {
                        "role": "system",
                        "content": "あなたは転職支援の専門家です。求職者のプロフィールと求人情報を分析し、マッチングの詳細な説明を提供してください。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )

            analysis = response.choices[0].message.content.strip()
            return analysis

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return f"分析の生成に失敗しました: {str(e)}"

    def chat_about_career(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        seeker_profile: dict
    ) -> str:
        """
        キャリアに関する会話

        Args:
            message: ユーザーのメッセージ
            conversation_history: 会話履歴
            seeker_profile: 求職者プロフィール

        Returns:
            AIの返答
        """
        if not self.client:
            return "OpenAI APIが設定されていません"

        try:
            # システムプロンプト
            system_prompt = self._create_career_system_prompt(seeker_profile)

            # メッセージ履歴作成
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})

            # OpenAI API呼び出し
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                max_tokens=800,
                temperature=0.8
            )

            reply = response.choices[0].message.content.strip()
            return reply

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return f"申し訳ございません。エラーが発生しました: {str(e)}"

    def generate_matching_explanation(
        self,
        seeker_profile: dict,
        recommendations: List[dict]
    ) -> str:
        """
        マッチング結果全体の説明を生成

        Args:
            seeker_profile: 求職者プロフィール
            recommendations: レコメンデーション結果

        Returns:
            AI生成の説明テキスト
        """
        if not self.client:
            return "OpenAI APIが設定されていません"

        try:
            prompt = f"""
以下の求職者プロフィールに基づいて、{len(recommendations)}件の求人をマッチングしました。
全体的なマッチング結果について、求職者にわかりやすく説明してください。

【求職者プロフィール】
スキル: {', '.join(seeker_profile.get('skills', []))}
希望勤務地: {seeker_profile.get('location', '指定なし')}
希望年収: {seeker_profile.get('desired_salary_min', 0):,}円以上

【マッチング結果】
トップ3の求人:
"""
            for i, rec in enumerate(recommendations[:3], 1):
                prompt += f"\n{i}. {rec['job_data']['title']} (スコア: {rec['match_score']:.0f}点)"

            prompt += "\n\n簡潔に（200文字程度で）、このマッチング結果の特徴と求職者へのアドバイスを提供してください。"

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "あなたは親しみやすい転職アドバイザーです。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )

            explanation = response.choices[0].message.content.strip()
            return explanation

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return "マッチング結果の説明生成に失敗しました"

    def _create_analysis_prompt(
        self,
        seeker_profile: dict,
        job_data: dict,
        match_score: float
    ) -> str:
        """分析用プロンプトを作成"""
        prompt = f"""
以下の求職者と求人のマッチング分析を行ってください。

【求職者プロフィール】
スキル: {', '.join(seeker_profile.get('skills', []))}
経験: {seeker_profile.get('experience', 'なし')}
希望勤務地: {seeker_profile.get('location', '指定なし')}
希望年収: {seeker_profile.get('desired_salary_min', 0):,}円以上

【求人情報】
職種: {job_data.get('title')}
勤務地: {job_data.get('location')}
年収: {job_data.get('salary_min', 0):,}円 〜 {job_data.get('salary_max', 0):,}円
必要スキル: {', '.join(job_data.get('tags', []))}
仕事内容: {job_data.get('description', '')[:100]}...

【マッチスコア】: {match_score:.0f}/100点

以下の観点で分析してください（150文字程度）:
1. スキルの適合度
2. この求人で得られる成長機会
3. 応募する際のポイント
"""
        return prompt

    def _create_career_system_prompt(self, seeker_profile: dict) -> str:
        """キャリア相談用システムプロンプトを作成"""
        return f"""あなたは経験豊富な転職アドバイザーです。
求職者のプロフィールを理解し、キャリアに関する相談に親身に答えてください。

【求職者プロフィール】
スキル: {', '.join(seeker_profile.get('skills', []))}
経験: {seeker_profile.get('experience', 'なし')}
希望勤務地: {seeker_profile.get('location', '指定なし')}

以下の点に注意してください:
- 親しみやすく、励ます tone で話す
- 具体的で実践的なアドバイスを提供
- 200文字程度で簡潔に回答
"""


# 後方互換性のための非推奨関数（依存性注入を使用することを推奨）
_conversation_service: Optional[ConversationService] = None


def get_conversation_service() -> ConversationService:
    """
    会話サービスのシングルトンインスタンスを取得

    注意: この関数は非推奨です。代わりにFastAPIの依存性注入を使用してください。
    app.core.dependencies.get_conversation_service_dependency を使用することを推奨します。

    Returns:
        ConversationServiceインスタンス
    """
    global _conversation_service
    if _conversation_service is None:
        from app.services.openai_service import get_openai_service
        openai_service = get_openai_service()
        _conversation_service = ConversationService(openai_service)
    return _conversation_service
