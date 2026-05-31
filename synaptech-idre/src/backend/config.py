import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "SynapTech IDRE"
    debug: bool = False

    csc_dtype: str = "float32"
    n_neurons: int = 130_000

    root_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    data_path: str = ""
    layout_path: str = ""

    api_keys: Optional[str] = None
    jwt_secret: Optional[str] = None

    pinecone_api_key: Optional[str] = None
    pinecone_index: str = "synaptech-telemetry"

    deepseek_api_key: Optional[str] = None
    deepseek_model: str = "deepseek-v4"

    lava_backend: str = "sim"
    inrc_enabled: bool = False

    s3_endpoint: Optional[str] = None
    s3_bucket: str = "synaptech-ip-encrypted"
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None

    flywire_real_enabled: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def model_post_init(self, __context) -> None:
        root = self.root_dir
        if not self.data_path:
            self.data_path = os.path.join(root, "data", "flywire")
        if not self.layout_path:
            self.layout_path = os.path.join(root, "data", "layout.json")

    @property
    def flywire_real_connections(self) -> str:
        return os.path.join(self.root_dir, "data", "flywire", "proofread_connections.feather")

    @property
    def flywire_root_ids(self) -> str:
        return os.path.join(self.root_dir, "data", "flywire", "root_ids.npy")

    @property
    def flywire_positions(self) -> str:
        return os.path.join(self.root_dir, "data", "flywire", "positions.npy")


settings = Settings()
