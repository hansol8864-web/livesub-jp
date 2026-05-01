import queue
import threading
import time
from math import gcd
from typing import List

import numpy as np
import pyaudiowpatch as pyaudio
from scipy.signal import butter, resample_poly, sosfilt
from silero_vad import VADIterator, load_silero_vad

TARGET_RATE = 16000
VAD_FRAME = 512  # silero VAD는 16kHz에서 정확히 512샘플 프레임 필요
MIN_SPEECH_S = 0.5
MAX_SPEECH_S = 5.0
SILENCE_DURATION_MS = 500
SPEECH_PAD_MS = 100


class AudioCapture:
    """WASAPI 루프백 + 실시간 silero-VAD 동적 청크.

    발화 시작/종료를 감지해 자연스러운 단위로 잘라 큐에 넣는다.
    고정 4초 청크 대비 평균 지연이 절반 가까이 줄어든다.
    """

    def __init__(self, audio_queue: "queue.Queue[np.ndarray]"):
        self.audio_queue = audio_queue
        self.running = False

        # silero-VAD (ONNX 모드 — torch 의존성 없음)
        print("[VAD] silero-VAD 로딩 중...")
        self._vad_model = load_silero_vad(onnx=True)
        self._vad_iter = VADIterator(
            self._vad_model,
            threshold=0.4,
            sampling_rate=TARGET_RATE,
            min_silence_duration_ms=SILENCE_DURATION_MS,
            speech_pad_ms=SPEECH_PAD_MS,
        )
        print("[VAD] 로딩 완료")

        # 80Hz 이하 럼블 제거용 하이패스
        self._hp_sos = butter(2, 80, btype="hp", fs=TARGET_RATE, output="sos")

        # 상태
        self._vad_residue = np.zeros(0, dtype=np.float32)
        self._active_speech: List[np.ndarray] = []
        self._is_speaking = False

    # ---------------------------------------------------------------- helpers

    def _find_loopback(self, p: pyaudio.PyAudio) -> dict:
        wasapi = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        default_out = p.get_device_info_by_index(wasapi["defaultOutputDevice"])
        if default_out.get("isLoopbackDevice"):
            return default_out
        for dev in p.get_loopback_device_info_generator():
            if default_out["name"] in dev["name"]:
                return dev
        raise RuntimeError(
            f"루프백 장치 없음. 기본 출력장치: {default_out['name']}"
        )

    def _emit_chunk(self):
        if not self._active_speech:
            return
        chunk = np.concatenate(self._active_speech)
        self._active_speech = []

        if len(chunk) < int(MIN_SPEECH_S * TARGET_RATE):
            return  # 너무 짧으면 노이즈일 가능성

        # 80Hz 하이패스 (럼블/리코딩 노이즈 감소)
        try:
            chunk = sosfilt(self._hp_sos, chunk).astype(np.float32)
        except Exception:
            pass

        try:
            self.audio_queue.put_nowait(chunk)
        except queue.Full:
            # 백프레셔 발생 시 가장 오래된 것 버리고 최신 우선
            try:
                self.audio_queue.get_nowait()
                self.audio_queue.put_nowait(chunk)
            except queue.Empty:
                pass

    def _process_16k(self, pcm: np.ndarray):
        """16kHz mono 리샘플된 오디오를 VAD 프레임 단위로 처리."""
        self._vad_residue = np.concatenate([self._vad_residue, pcm])

        while len(self._vad_residue) >= VAD_FRAME:
            frame = self._vad_residue[:VAD_FRAME].astype(np.float32)
            self._vad_residue = self._vad_residue[VAD_FRAME:]

            # 발화 중이면 누적
            if self._is_speaking:
                self._active_speech.append(frame.copy())

            # VAD 이벤트 체크
            try:
                event = self._vad_iter(frame, return_seconds=True)
            except Exception:
                event = None

            if event is not None:
                if "start" in event and not self._is_speaking:
                    self._is_speaking = True
                    self._active_speech = [frame.copy()]
                elif "end" in event and self._is_speaking:
                    self._is_speaking = False
                    self._emit_chunk()

            # 너무 길어지면 강제 컷
            if self._is_speaking:
                acc = sum(len(f) for f in self._active_speech)
                if acc > MAX_SPEECH_S * TARGET_RATE:
                    self._emit_chunk()
                    self._is_speaking = False
                    try:
                        self._vad_iter.reset_states()
                    except Exception:
                        pass

    # ---------------------------------------------------------------- public

    def start(self):
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self.running = False

    # ---------------------------------------------------------------- runner

    def _run(self):
        p = pyaudio.PyAudio()
        try:
            dev = self._find_loopback(p)
            src_rate = int(dev["defaultSampleRate"])
            channels = min(int(dev["maxInputChannels"]), 2)
            g = gcd(TARGET_RATE, src_rate)
            up, down = TARGET_RATE // g, src_rate // g

            print(f"[오디오] 장치: {dev['name']}")
            print(f"[오디오] {src_rate}Hz {channels}ch -> {TARGET_RATE}Hz mono (VAD 동적)")

            def callback(in_data, frame_count, time_info, status):
                pcm = np.frombuffer(in_data, dtype=np.float32).copy()
                if channels == 2:
                    pcm = pcm.reshape(-1, 2).mean(axis=1)
                if up != down:
                    pcm = resample_poly(pcm, up, down).astype(np.float32)
                self._process_16k(pcm)
                return (None, pyaudio.paContinue)

            stream = p.open(
                format=pyaudio.paFloat32,
                channels=channels,
                rate=src_rate,
                input=True,
                input_device_index=dev["index"],
                stream_callback=callback,
                frames_per_buffer=2048,
            )
            stream.start_stream()
            while self.running:
                time.sleep(0.1)
            stream.stop_stream()
            stream.close()
        except Exception as e:
            print(f"[오디오 오류] {e}")
        finally:
            p.terminate()
