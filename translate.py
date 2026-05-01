import deepl


class Translator:
    def __init__(self, api_key: str):
        self.client = deepl.Translator(api_key)

    def translate(self, text: str) -> str:
        if not text.strip():
            return ""
        try:
            result = self.client.translate_text(
                text, source_lang="JA", target_lang="KO"
            )
            return result.text
        except deepl.DeepLException as e:
            print(f"[번역 오류] {e}")
            return text
