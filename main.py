import queue
import sys
import threading

from PyQt6.QtWidgets import QApplication

from audio_capture import AudioCapture
from overlay import SubtitleOverlay
from transcribe import Transcriber
from translate import Translator


def _worker(audio_queue: queue.Queue, transcriber: Transcriber,
            translator: Translator, overlay: SubtitleOverlay):
    while True:
        audio = audio_queue.get()
        if audio is None:
            break

        text_ja = transcriber.transcribe(audio)
        if not text_ja:
            continue

        print(f"[JA] {text_ja}")
        text_ko = translator.translate(text_ja)
        if text_ko:
            print(f"[KO] {text_ko}")
            overlay.update_text(text_ko)


def main():
    app = QApplication(sys.argv)

    overlay = SubtitleOverlay()
    overlay.show()

    transcriber = Transcriber()
    translator = Translator()

    audio_queue: queue.Queue = queue.Queue(maxsize=3)
    capture = AudioCapture(audio_queue)
    capture.start()

    worker_thread = threading.Thread(
        target=_worker,
        args=(audio_queue, transcriber, translator, overlay),
        daemon=True,
    )
    worker_thread.start()

    print("[시작] 브라우저에서 일본어 영상을 재생하세요")
    print("[종료] 자막창 더블클릭 또는 터미널 Ctrl+C")

    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        capture.stop()
        audio_queue.put(None)


if __name__ == "__main__":
    main()
