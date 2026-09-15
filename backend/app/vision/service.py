class VisionService:
    """E.D.I.T.H. vision boundary for image/scene analysis adapters."""

    async def analyze(self, image: bytes) -> dict:
        raise NotImplementedError("Configure a vision model or object-detection adapter")
