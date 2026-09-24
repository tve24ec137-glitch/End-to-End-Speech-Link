import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import butter, sosfiltfilt

# Define the save function early so we can use it multiple times
def save_wav(filename, rate, data):
    # Normalize to 16-bit PCM range
    data_norm = np.int16((data / np.max(np.abs(data))) * 32767)
    wavfile.write(filename, rate, data_norm)

# 1. Load the original 44.1 kHz audio
fs_old, data_old = wavfile.read('voice.wav')
if len(data_old.shape) > 1:
    data_old = data_old.mean(axis=1) # Convert stereo to mono
data_old = data_old.astype(np.float64)

# Create time array
t_old = np.arange(len(data_old)) / fs_old

# (Optional but recommended) Inject a 6.5 kHz high-frequency tone.
# This ensures there is high-frequency energy to alias, making the mistake obvious.
high_freq_noise = np.sin(2 * np.pi * 6500 * t_old) * (np.max(np.abs(data_old)) * 0.05)
data_old_noisy = data_old + high_freq_noise

save_wav('voice_noisy.wav', fs_old, data_old_noisy)

# 2. Set up the downsampling indices
fs_new = 8000
downsample_factor = fs_old / fs_new
# Grab nearest samples for pure decimation (no interpolation smoothing)
indices = np.round(np.arange(0, len(data_old_noisy), downsample_factor)).astype(int)
indices = indices[indices < len(data_old_noisy)] # Prevent out-of-bounds

# 3. Path A: Deliberate Aliasing (No Filter)
data_aliased = data_old_noisy[indices]

# 4. Path B: Correct Anti-Aliasing (Order-8 Butterworth)
cutoff = 3400.0
nyquist = fs_old / 2.0
# FIXED: Using 'sos' (Second-Order Sections) for guaranteed numerical stability
sos = butter(8, cutoff / nyquist, btype='low', output='sos')
data_filtered = sosfiltfilt(sos, data_old_noisy)
data_clean = data_filtered[indices]

# 5. Save both files for the listening test
def save_wav(filename, rate, data):
    # Normalize to 16-bit PCM range
    data_norm = np.int16((data / np.max(np.abs(data))) * 32767)
    wavfile.write(filename, rate, data_norm)

save_wav('voice_8k_aliased.wav', fs_new, data_aliased)
save_wav('voice_8k_clean.wav', fs_new, data_clean)

# 6. Plotting Side-by-Side Spectrograms
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

# Spectrogram of Aliased Signal
Pxx1, freqs1, bins1, im1 = ax1.specgram(data_aliased, Fs=fs_new, NFFT=256, cmap='viridis')
ax1.set_title('Aliased Spectrum (No Filter)')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Frequency [Hz]')

# Spectrogram of Clean Signal
Pxx2, freqs2, bins2, im2 = ax2.specgram(data_clean, Fs=fs_new, NFFT=256, cmap='viridis')
ax2.set_title('Clean Spectrum (Order-8 Butterworth LPF at 3.4 kHz)')
ax2.set_xlabel('Time [s]')

fig.colorbar(im2, ax=[ax1, ax2], label='Intensity [dB]')
plt.show()
