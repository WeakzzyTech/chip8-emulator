import wave
import struct
import math

# Settings
filename = "beep.wav"
sample_rate = 44100
duration = 0.3      # seconds
frequency = 440.0   # Hz (classic beep)
amplitude = 32767

with wave.open(filename, "w") as f:
    f.setnchannels(1)        # mono
    f.setsampwidth(2)        # 16-bit audio
    f.setframerate(sample_rate)

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        sample = int(amplitude * math.sin(2 * math.pi * frequency * t))
        f.writeframes(struct.pack("<h", sample))

print("beep.wav generated")