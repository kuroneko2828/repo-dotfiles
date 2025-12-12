# uv add google-cloud-storage

import os

from google.cloud import storage
from google.cloud.storage import Blob


class GCSClient:
    """GCSクライアント"""

    def __init__(self):
        """初期化"""
        self.bucket_name = "your-bucket-name"
        self.client = storage.Client(project="your-project-id")
        self.bucket = self.client.get_bucket(self.bucket_name)

    def get_blob(self, blob_name: str) -> Blob:
        """ブロブを取得する"""
        return self.bucket.blob(blob_name)

    def download_file(self, blob_name: str, local_path: str) -> None:
        """ファイルをダウンロードする

        Args:
            blob_name (str): GCS内のファイルパス
            local_path (str): ローカルに保存するファイルパス
        """
        # ローカルディレクトリが存在しない場合は作成する
        local_dir = os.path.dirname(local_path)
        if local_dir and not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)

        blob = self.bucket.blob(blob_name)
        blob.download_to_filename(local_path)

    def download_folder(self, blob_name: str, local_path: str) -> None:
        """フォルダをダウンロードする"""
        prefix = blob_name.rstrip("/") + "/" if not blob_name.endswith("/") else blob_name
        print(prefix)
        blobs = self.bucket.list_blobs(prefix=prefix)
        print(blobs)

        for blob in blobs:
            relative_path = blob.name[len(prefix) :]
            if not relative_path:
                continue

            local_file_path = os.path.join(local_path, relative_path)
            local_dir = os.path.dirname(local_file_path)
            if local_dir and not os.path.exists(local_dir):
                os.makedirs(local_dir, exist_ok=True)

            blob.download_to_filename(local_file_path)

    def upload_file(self, local_path: str, blob_name: str) -> None:
        """ファイルをアップロードする"""
        blob = self.bucket.blob(blob_name)
        blob.upload_from_filename(local_path)

    def extract_blob_name(self, uri: str) -> str:
        """ブロブ名を抽出する"""
        return uri.replace(f"gs://{self.bucket_name}/", "")
