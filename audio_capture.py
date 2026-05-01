import threading
import time
import queue
from math import gcd

import numpy as np
import pyaudiowpatch as pyaudio
from scipy.signal import resample_poly

TARGET_RATE = 16000
CHUNK_SECONDS = 4


class AudioCapture:
    def __init__(self, audio_queue: queue.Queue):
        self.audio_queue = audio_queue
        self.running = False

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

    def start(self):
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self.running = False

    def _run(self):
        p = pyaudio.PyAudio()
        try:
            dev = self._find_loopback(p)
            src_rate = int(dev["defaultSampleRate"])
            channels = min(int(dev["maxInputChannels"]), 2)
            chunk_frames = src_rate * CHUNK_SECONDS
            g = gcd(TARGET_RATE, src_rate)
            up, down = TARGET_RATE // g, src_rate // g

            print(f"[오디오] 장치: {dev['name']}")
            print(f"[오디오] {src_rate}Hz {channels}ch → {TARGET_RATE}Hz mono")

            buffer: list[np.ndarray] = []
            buffer_len = 0

            def callback(in_data, frame_count, time_info, status):
                nonlocal buffer_len
                pcm = np.frombuffer(in_data, dtype=np.float32).copy()
                if channels == 2:
                    pcm = pcm.reshape(-1, 2).mean(axis=1)
                buffer.append(pcm)
                buffer_len += len(pcm)

                if buffer_len >= chunk_frames:
                    merged = np.concatenate(buffer)
                    chunk = merged[:chunk_frames]
                    rest = merged[chunk_frames:]
                    buffer.clear()
                    buffer_len = len(rest)
                    if len(rest):
                        buffer.append(rest)

                    if up != down:
                        chunk = resample_poly(chunk, up, down).astype(np.float32)

                    if not self.audio_queue.full():
                        self.audio_queue.put_nowait(chunk)

                return (None, pyaudio.paContinue)

            stream = p.open(
                format=pyaudio.paFloat32,
                channels=channels,
                rate=src_rate,
                input=True,
                input_device_index=dev["index"],
                stream_callback=callback,
                frames_per_buffer=1024,
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
