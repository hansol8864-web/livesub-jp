<div align="center">
  <img src="icon.ico" alt="LiveSub JP" width="120">
  <h1>LiveSub JP</h1>
  <p>일본어 영상을 실시간 한국어 자막으로 보여주는 Windows 앱</p>
</div>

---

## 작동 방식

브라우저나 어떤 플레이어든 일본어 영상을 재생하면 시스템 오디오를 캡처해서 일본어 음성 → 한국어 자막을 화면 위에 띄워줍니다.

- **오디오 캡처**: WASAPI 루프백 (브라우저/플레이어 종류 무관)
- **음성 인식**: faster-whisper (small / CPU)
- **번역**: DeepL API (일본어 → 한국어)
- **자막**: 항상 위 떠있는 PyQt6 오버레이

지연시간: 발화 후 약 5~7초.

## 시스템 요구사항

- Windows 10 또는 11 (64비트)
- Python 3.10 ~ 3.14
- RAM 8GB 이상 권장
- 인터넷 연결 (DeepL 호출 + 첫 실행 시 모델 다운로드 약 500MB)

## 설치 (5~10분)

### 1. 이 레포 다운로드

녹색 **Code** 버튼 → **Download ZIP** → 압축 풀기

또는 git이 있으면:
```bash
git clone https://github.com/hansol8864-web/livesub-jp.git
```

### 2. Python 설치 (없는 경우만)

[python.org](https://www.python.org/downloads/) 에서 **3.12 다운로드** → 설치 시 첫 화면에서 **`Add python.exe to PATH`** 반드시 체크.

> Python 3.14는 일부 패키지 wheel이 아직 없어서 설치 실패할 수 있어요. 3.12 권장.

### 3. DeepL API 키 발급 (무료)

1. https://www.deepl.com/pro-api 접속
2. **`Sign up for free`** 클릭 → 가입
3. 가입 시 **DeepL API Free** 플랜 선택 (월 50만 자 무료)
4. 가입 후 계정 페이지 → **API Keys** 탭에서 키 복사

### 4. .env 파일 만들기

`.env.example` 파일을 복사해서 이름을 `.env`로 바꿔주세요.
`.env`를 메모장으로 열어서 본인 키 붙여넣기:

```
DEEPL_API_KEY=발급받은_키_여기_붙여넣기
```

### 5. setup.bat 실행

`setup.bat` 더블클릭 → 자동으로 venv 생성 + 패키지 설치 + Whisper 모델 다운로드.

> Windows SmartScreen 경고가 뜨면 **추가 정보 → 실행** 클릭.

`Setup complete!` 메시지가 뜨면 끝.

## 사용법

`run.bat` 더블클릭 → 검은 cmd 창 + 화면 하단에 자막창이 뜸.

브라우저(Chrome/Edge/Firefox/뭐든)에서 일본어 영상 재생하면 5~7초 후 자막이 나옵니다.

### 자막창 조작
- **드래그**: 위치 이동
- **더블클릭**: 종료

### 종료
- 자막창 더블클릭
- cmd 창에서 `Ctrl + C`
- cmd 창 X 버튼

## 자주 묻는 질문

**Q. 유튜브, 넷플릭스, 트위치 다 됨?**
A. 네. 시스템에서 소리만 나면 영상 출처 무관.

**Q. 정확도는?**
A. faster-whisper small 모델 + DeepL 조합. 또렷한 발음은 90%+, 노이즈/사투리/효과음 많은 영상은 떨어집니다.

**Q. 인터넷 끊기면 작동해요?**
A. 음성 인식은 로컬이지만 번역은 DeepL 호출이라 인터넷 필수.

**Q. 다른 언어 조합으로 바꿀 수 있나요?**
A. 가능. `transcribe.py`의 `language="ja"`와 `translate.py`의 `source_lang/target_lang` 수정.

**Q. 50만 자 한도 넘으면?**
A. 다음 달까지 번역 중단 (음성 인식은 계속 작동). DeepL Pro 유료 전환 가능.

## 트러블슈팅

| 증상 | 해결 |
|------|------|
| `Python not found` | python.org에서 설치 + PATH 체크 |
| `Package install failed` | Python 3.14면 3.12로 다운그레이드 |
| `[오류] DEEPL_API_KEY가 없어요` | `.env` 파일 생성 + 키 입력 |
| 자막 안 뜸 | 영상 소리가 실제 출력되는지 확인 (음소거 X) |
| 자막이 5~7초 늦음 | 정상. 4초 오디오 청크 + 처리 시간 |

## 라이선스

[MIT License](LICENSE). 자유롭게 사용/수정/재배포 가능.

## 사용 라이브러리

- [DeepL API](https://www.deepl.com/pro-api) — 번역
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — 음성 인식
- [PyAudioWPatch](https://github.com/s0d3s/PyAudioWPatch) — Windows WASAPI 루프백
- [Silero VAD](https://github.com/snakers4/silero-vad) — 무음 검출
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) — UI
