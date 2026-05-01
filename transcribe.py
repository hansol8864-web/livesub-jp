import numpy as np
from faster_whisper import WhisperModel


class Transcriber:
    def __init__(self):
        print("[Whisper] 모델 로딩 중 (small / CPU / int8)...")
        self.model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8",
            num_workers=2,
        )
        print("[Whisper] 로딩 완료")

    def transcribe(self, audio: np.ndarray) -> str:
        if np.abs(audio).mean() < 0.0005:
            return ""

        segments, _ = self.model.transcribe(
            audio,
            language="ja",
            beam_size=5,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 400},
        )
        text = "".join(seg.text for seg in segments).strip()
        return text
