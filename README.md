<div align="center">
  <img src="icon.ico" alt="LiveSub JP" width="120">
  <h1>LiveSub JP</h1>
  <p>일본어 영상을 실시간 한국어 자막으로 보여주는 Windows 앱</p>
  <p>설치 불필요. 더블클릭으로 바로 실행.</p>
</div>

---

## 다운로드 (친구용 · 권장)

[**Releases 페이지**](https://github.com/hansol8864-web/livesub-jp/releases/latest)에서 최신 ZIP 받기.

1. **`LiveSubJP-vX.X.X-win64.zip`** 다운로드
2. **압축 풀기** (어디든 OK — 바탕화면, 다운로드 폴더 등)
3. 풀어진 `LiveSubJP` 폴더 안의 **`LiveSubJP.exe`** 더블클릭

> ⚠️ Windows SmartScreen 경고가 뜨면: **추가 정보 → 실행** 클릭 (서명 안 된 .exe라서 그래요. 안전합니다.)

> ⚠️ 첫 실행 시 Whisper medium 모델 약 1.5GB 다운로드. 인터넷 필요. 두 번째부터는 바로 실행.

## 사용법

`LiveSubJP.exe` 더블클릭 → 검은 cmd 창 + 화면 하단에 자막창 등장.

이후 브라우저(Chrome/Edge/Firefox/뭐든)나 미디어 플레이어로 일본어 영상 재생하면 5~7초 후 한국어 자막이 나옵니다.

### 자막창 조작
- **드래그**: 위치 이동
- **더블클릭**: 종료

### 종료
- 자막창 더블클릭
- cmd 창 X 버튼
- cmd에서 `Ctrl + C`

---

## 작동 방식

브라우저나 어떤 플레이어든 일본어 영상을 재생하면 시스템 오디오를 캡처해서 일본어 음성 → 한국어 자막을 화면 위에 띄움.

- **오디오 캡처**: WASAPI 루프백 (브라우저/플레이어 종류 무관)
- **VAD (음성 검출)**: silero-VAD — 발화 단위로 동적 청킹 (고정 4초 청크 X)
- **음성 인식**: faster-whisper **medium** + 롤링 컨텍스트 (이전 200자 활용)
- **번역**: Google Translate (무료, API 키 불필요)
- **자막**: 항상 위 떠있는 PyQt6 오버레이

지연시간: 발화 종료 후 약 2~4초 (VAD 동적 청킹 적용).

## 시스템 요구사항

- Windows 10 또는 11 (64비트)
- RAM 8GB 이상 권장
- 인터넷 연결 (번역 + 첫 실행 시 모델 다운로드)
- 약 2.5GB 디스크 공간 (Whisper medium 모델 포함)

## 자주 묻는 질문

**Q. 유튜브, 넷플릭스, 트위치 다 됨?**
A. 네. 시스템에서 소리만 나면 영상 출처 무관.

**Q. 번역 정확도는?**
A. 또렷한 발음의 뉴스/다큐는 80~90%, 잡담/노이즈/사투리 많은 영상은 떨어집니다.

**Q. 인터넷 끊기면 작동해요?**
A. 음성 인식은 로컬이지만 Google Translate 호출이라 인터넷 필수.

**Q. 다른 언어 조합으로 바꿀 수 있나요?**
A. 코드 수정으로 가능. 아래 [개발자 설치] 참고.

## 트러블슈팅

| 증상 | 해결 |
|------|------|
| SmartScreen 경고 | "추가 정보 → 실행" 클릭. 정상. |
| 첫 실행이 느림 (1~2분 멈춤) | 정상. Whisper 모델 다운로드 중. |
| 자막 안 뜸 | 영상 소리가 실제 출력되는지 확인 (음소거 X) |
| 자막이 5~7초 늦음 | 정상. 4초 오디오 청크 + 처리 시간 |
| `루프백 장치 없음` 에러 | 시스템 출력 장치(스피커) 확인 |
| 백신이 차단 | 서명 안 된 PyInstaller 빌드의 흔한 오탐. 신뢰 등록 후 재실행. |

---

## 개발자 설치 (코드 수정/기여용)

소스에서 직접 돌리거나 수정하고 싶으면:

```bash
git clone https://github.com/hansol8864-web/livesub-jp.git
cd livesub-jp
```

1. Python 3.12 설치 (PATH 체크 필수)
2. `setup.bat` 더블클릭 → venv + 패키지 자동 설치
3. `run.bat`으로 실행

다른 언어 조합:
- `transcribe.py`의 `language="ja"` → 원하는 ISO 코드
- `translate.py`의 `source/target` → 원하는 ISO 코드

## 빌드 (.exe 직접 만들기)

```bash
venv\Scripts\pyinstaller.exe --name LiveSubJP --icon=icon.ico ^
  --collect-all faster_whisper --collect-all ctranslate2 ^
  --collect-all pyaudiowpatch --collect-all deep_translator ^
  --add-data "icon.ico;." --noconfirm --console main.py
```

결과는 `dist/LiveSubJP/`에 생성.

## 라이선스

[MIT License](LICENSE). 자유롭게 사용/수정/재배포 가능.

## 사용 라이브러리

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — 음성 인식
- [deep-translator](https://github.com/nidhaloff/deep-translator) — 번역
- [PyAudioWPatch](https://github.com/s0d3s/PyAudioWPatch) — Windows WASAPI 루프백
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) — UI
