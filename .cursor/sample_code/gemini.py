# uv add google-genai

import time

from fugafuga import load_from_gcs, save_to_gcs
from google import genai
from google.genai.types import CreateBatchJobConfig, GenerateContentConfig, HttpOptions
from hogehoge import GeminiResponseModel


class GeminiClient:
    """Gemini APIの使用例"""

    def __init__(self, model_name: str = "gemini-2.5-flash") -> None:
        self.client = genai.Client(
            vertexai=True,
            project="your-project-id",
            location="global",
            http_options=HttpOptions(api_version="v1"),
        )
        self.model_name = model_name
        self.MAX_OUTPUT_TOKENS = 1024
        self.TEMPERATURE = 0

    def create_batch_job(self, input_uri: str, output_uri: str):
        """バッチ推論ジョブを作成する.

        Args:
            input_uri: 入力データのURI (Cloud StorageまたはBigQuery)
                例: "gs://bucket/input.jsonl" または "bq://project.dataset.table"
            output_uri: 出力先のURI (Cloud StorageまたはBigQuery)
                例: "gs://bucket/output" または "bq://project.dataset.table"

        Returns:
            作成されたバッチジョブ
        """
        batch_job = self.client.batches.create(
            model=self.model_name,
            src=input_uri,
            config=CreateBatchJobConfig(dest=output_uri),
        )
        return batch_job

    def get_batch_job(self, job_name: str):
        """バッチジョブの情報を取得する.

        Args:
            job_name: バッチジョブの名前

        Returns:
            バッチジョブの情報
        """
        return self.client.batches.get(name=job_name)

    def wait_for_batch_job(self, job_name: str, check_interval: int = 5) -> bool:
        """バッチジョブの完了を待つ.

        Args:
            job_name: バッチジョブの名前
            check_interval: ステータスチェックの間隔（秒）

        Returns:
            ジョブが成功した場合True、失敗した場合False
        """
        while True:
            batch_job = self.get_batch_job(job_name)
            if batch_job.state in (
                "JOB_STATE_RUNNING",
                "JOB_STATE_PENDING",
                "JOB_STATE_QUEUED",
            ):
                time.sleep(check_interval)
            elif batch_job.state == "JOB_STATE_SUCCEEDED":
                print(batch_job.dest.gcs_uri)
                return True
            else:
                print(f"ジョブが失敗しました: {batch_job.error}")
                return False

    def create_batch_input(self, data: list[dict]):
        """バッチ推論用の入力を生成する.
        ※入力に画像が必要な場合の例

        Args:
            data: 入力データのリスト

        Returns:
            バッチ推論用の入力辞書
        """

        def __create_data(
            key: str | None = None,
            prompt: str | None = None,
            image_url: str | None = None,
        ) -> dict:
            if not prompt:
                raise ValueError("プロンプトは必須です")
            if not image_url:
                raise ValueError("画像URLは必須です")

            parts = [
                {"text": prompt},
                {"file_data": {"file_uri": image_url, "mime_type": "image/jpeg"}},
            ]

            schema = GeminiResponseModel.model_json_schema()

            return {
                "key": key,
                "request": {
                    "contents": [{"role": "user", "parts": parts}],
                    "generationConfig": {
                        "temperature": 0,
                        "response_mime_type": "application/json",
                        "response_schema": schema,
                    },
                },
            }

        return [
            __create_data(key=d["key"], prompt=d["prompt"], image_url=d["image_url"]) for d in data
        ]

    def predict(self, input: dict):
        """オンラインでの推論

        Args:
            input: 入力データ
        """
        config = GenerateContentConfig(
            max_output_tokens=self.MAX_OUTPUT_TOKENS,
            temperature=self.TEMPERATURE,
            response_mime_type="application/json",
            response_schema=GeminiResponseModel,
        )

        contents = [
            {
                "role": "user",
                "parts": [
                    {"text": input["prompt"]},
                    {"file_data": {"file_uri": input["image_url"], "mime_type": "image/jpeg"}},
                ],
            }
        ]
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config,
        )
        return response.text


def batch_example():
    client = GeminiClient()
    data = [
        {
            "key": "1",
            "prompt": "Hello, world!",
            "image_url": "gs://bucket/image.jpg",
        },
        {
            "key": "2",
            "prompt": "Hello, world!",
            "image_url": "gs://bucket/image.jpg",
        },
    ]
    input = client.create_batch_input(data)
    # 入力をCloud Storageに保存
    save_to_gcs(input, "gs://bucket/input.jsonl")

    job = client.create_batch_job("gs://bucket/input.jsonl", "gs://bucket/output")
    client.wait_for_batch_job(job.name)

    # 出力をCloud Storageから読み込む
    output = load_from_gcs("gs://bucket/output")
    return output


def predict_example():
    client = GeminiClient()
    input = {
        "prompt": "Hello, world!",
        "image_url": "gs://bucket/image.jpg",
    }
    output = client.predict(input)
    return output
