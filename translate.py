from deep_translator import GoogleTranslator


class Translator:
    """일본어 → 한국어 무료 번역기 (Google Translate 비공식 인터페이스).

    API 키 불필요. 인터넷 연결 필요.
    """

    def __init__(self):
        self.client = GoogleTranslator(source="ja", target="ko")

    def translate(self, text: str) -> str:
        text = text.strip()
        if not text:
            return ""
        try:
            return self.client.translate(text)
        except Exception as e:
            print(f"[번역 오류] {e}")
            return text
