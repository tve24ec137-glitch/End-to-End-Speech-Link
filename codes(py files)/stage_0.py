import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

# 1. Load the Audio File
# Make sure your file is named 'voice.wav' and is in the same directory
sample_rate, data = wavfile.read('voice.wav')

# Convert to Mono if the recording is Stereo
if len(data.shape) > 1:
    data = data.mean(axis=1)

# Convert data to float64 to prevent integer overflow during math operations
data = data.astype(np.float64)

# Create a time vector in seconds
duration = len(data) / sample_rate
time = np.linspace(0., duration, len(data))

# 2. Compute the Crest Factor (Peak-to-RMS ratio)
peak_val = np.max(np.abs(data))
rms_val = np.sqrt(np.mean(data**2))
crest_factor_linear = peak_val / rms_val
crest_factor_dB = 20 * np.log10(crest_factor_linear)

print(f"Sample Rate: {sample_rate} Hz")
print(f"Duration: {duration:.2f} seconds")
print(f"Crest Factor (Linear): {crest_factor_linear:.2f}")
print(f"Crest Factor (dB): {crest_factor_dB:.2f} dB")

# 3. Plotting: Waveform and Spectrogram
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Subplot 1: Time-Domain Waveform
ax1.plot(time, data, color='b', alpha=0.7)
ax1.set_title('Speech Waveform')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Amplitude')
ax1.grid(True)

# Subplot 2: Spectrogram
# NFFT dictates the frequency resolution. 1024 is standard for speech.
Pxx, freqs, bins, im = ax2.specgram(data, Fs=sample_rate, NFFT=1024, cmap='viridis')
ax2.set_title('Spectrogram (Frequency Content over Time)')
ax2.set_xlabel('Time [s]')
ax2.set_ylabel('Frequency [Hz]')
# Limit Y-axis to 10 kHz since human speech energy drops off heavily after 4-5 kHz
ax2.set_ylim(0, 10000) 
fig.colorbar(im, ax=ax2, label='Intensity [dB]')

plt.tight_layout()
plt.show()
