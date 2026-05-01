import numpy as np
from faster_whisper import WhisperModel


class Transcriber:
    """일본어 STT — Whisper medium + 도메인 프롬프트 + 롤링 컨텍스트.

    이전 인식 결과 약 200자를 다음 인식의 initial_prompt로 흘려보내
    Whisper가 화자/주제를 일관되게 따라가도록 만든다.
    """

    JA_HINT = "これは日本語の動画の文字起こしです。話者は自然な日本語で話しています。"
    CONTEXT_LIMIT = 200

    def __init__(self, model_name: str = "medium"):
        print(f"[Whisper] 모델 로딩 중 ({model_name} / CPU / int8)...")
        self.model = WhisperModel(
            model_name,
            device="cpu",
            compute_type="int8",
            num_workers=2,
        )
        self._context = ""
        print("[Whisper] 로딩 완료")

    def transcribe(self, audio: np.ndarray) -> str:
        # 거의 무음이면 스킵 (VAD가 이미 걸렀지만 안전망)
        if np.abs(audio).mean() < 0.0005:
            return ""

        prompt = self.JA_HINT
        if self._context:
            prompt = f"{self.JA_HINT} {self._context}"

        segments, _ = self.model.transcribe(
            audio,
            language="ja",
            beam_size=3,
            vad_filter=False,  # 상위에서 이미 silero-VAD 통과
            initial_prompt=prompt,
            condition_on_previous_text=False,  # 컨텍스트는 수동 관리
            no_speech_threshold=0.6,
        )
        text = "".join(seg.text for seg in segments).strip()

        # 롤링 컨텍스트 갱신 (최신 N자 유지)
        if text:
            self._context = (self._context + " " + text)[-self.CONTEXT_LIMIT:]

        return text
