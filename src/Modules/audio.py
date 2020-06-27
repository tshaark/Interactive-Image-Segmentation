import pyaudio
import wave
import threading as th

class AudioRecorder():
    
    def __init__(self, record_seconds):
        self.flag = True
        self.filename = "audios/recorded.wav"
        self.chunk = 1024
        self.FORMAT = pyaudio.paInt16
        self.channels = 1
        self.sample_rate = 44100
        self.record_seconds = record_seconds
    def stop_record(self):
        self.flag = False
    def record(self):
        p = pyaudio.PyAudio()
        print("Recording...")
        stream = p.open(format=self.FORMAT,
                        channels=self.channels,
                        rate=self.sample_rate,
                        input=True,
                        output=True,
                        frames_per_buffer=self.chunk)
        frames = []
        for i in range(0, int(44100 / self.chunk * 3)):
            data = stream.read(self.chunk)
            frames.append(data)
        
        print("Finished recording.")
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(self.filename, "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b"".join(frames))
        wf.close()
