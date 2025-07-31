import hashlib
from typing import Dict

class TokenFusion:
    """Map tokens from different modalities to a shared deterministic ID."""

    def __init__(self) -> None:
        self.token_map: Dict[str, str] = {}

    def _canonical(self, token: str) -> str:
        return token.strip().lower()

    def fuse_token(self, token: str) -> str:
        canon = self._canonical(token)
        token_id = hashlib.sha1(canon.encode()).hexdigest()[:8]
        self.token_map[canon] = token_id
        return token_id

    def fuse_from_stt(self, transcript: str) -> str:
        return self.fuse_token(transcript)

    def fuse_from_image(self, label: str) -> str:
        return self.fuse_token(label)
