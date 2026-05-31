import os
from pathlib import Path
from typing import List, Optional

from transformers import AutoTokenizer

from dak.usf.config import VOCAB_SIZE


HF_TOKENIZER_REPO = "allenai/OLMo-2-0425-1B"


class USFTokenizer:
    def __init__(self, vocab_size: int = VOCAB_SIZE, model_path: Optional[str] = None):
        self._vocab_size = vocab_size

        if model_path and os.path.isdir(model_path):
            self._tokenizer = AutoTokenizer.from_pretrained(model_path)
        else:
            self._tokenizer = AutoTokenizer.from_pretrained(HF_TOKENIZER_REPO)

        if model_path and os.path.isfile(model_path):
            os.remove(model_path)

        self._tokenizer.deprecation_warnings = False

        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token
        if self._tokenizer.bos_token is None:
            self._tokenizer.bos_token = self._tokenizer.eos_token

    @property
    def bos_id(self) -> int:
        return self._tokenizer.bos_token_id or 1

    @property
    def eos_id(self) -> int:
        return self._tokenizer.eos_token_id or 2

    @property
    def pad_id(self) -> int:
        return self._tokenizer.pad_token_id or 0

    @property
    def unk_id(self) -> int:
        return self._tokenizer.unk_token_id or 3

    @property
    def vocab_size(self) -> int:
        return len(self._tokenizer)

    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        return self._tokenizer.encode(text, add_special_tokens=add_special_tokens)

    def encode_batch(self, texts: List[str], add_special_tokens: bool = True) -> List[List[int]]:
        return [self.encode(t, add_special_tokens=add_special_tokens) for t in texts]

    def decode(self, ids: List[int], skip_special_tokens: bool = True) -> str:
        return self._tokenizer.decode(ids, skip_special_tokens=skip_special_tokens)

    def decode_batch(self, ids_batch: List[List[int]], skip_special_tokens: bool = True) -> List[str]:
        return self._tokenizer.batch_decode(ids_batch, skip_special_tokens=skip_special_tokens)

    def save(self, path: str):
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        self._tokenizer.save_pretrained(str(p))

    def load(self, path: str):
        p = Path(path)
        load_dir = p if p.is_dir() else p.parent
        self._tokenizer = AutoTokenizer.from_pretrained(str(load_dir))
