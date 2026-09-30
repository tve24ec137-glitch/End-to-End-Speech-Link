import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import butter, sosfiltfilt, welch

def save_wav(filename, rate, data):
    # Normalize to 16-bit PCM range to prevent clipping
    data_norm = np.int16((data / np.max(np.abs(data))) * 32767)
    wavfile.write(filename, rate, data_norm)

# 1. Load 44.1 kHz audio
fs_old, data_old = wavfile.read('voice.wav')
if len(data_old.shape) > 1:
    data_old = data_old.mean(axis=1)
data_old = data_old.astype(np.float64)

# Inject 6.5 kHz high-frequency tone & save
t_old = np.arange(len(data_old)) / fs_old
high_freq_noise = np.sin(2 * np.pi * 6500 * t_old) * (np.max(np.abs(data_old)) * 0.05)
data_old_noisy = data_old + high_freq_noise

save_wav('voice_44k_noisy.wav', fs_old, data_old_noisy)

# 2. Downsampling setup (44.1 kHz -> 8 kHz)
fs_new = 8000
downsample_factor = fs_old / fs_new
indices = np.round(np.arange(0, len(data_old_noisy), downsample_factor)).astype(int)
indices = indices[indices < len(data_old_noisy)]

# 3. Path A: Deliberate Aliasing (No Filter)
data_aliased = data_old_noisy[indices]

# 4. Path B: Correct Anti-Aliasing (Order-8 Butterworth LPF at 3.4 kHz)
cutoff = 3400.0
sos = butter(8, cutoff / (fs_old / 2.0), btype='low', output='sos')
data_filtered = sosfiltfilt(sos, data_old_noisy)
data_clean = data_filtered[indices]

# Save both 8 kHz outputs for listening comparison
save_wav('voice_8k_aliased.wav', fs_new, data_aliased)
save_wav('voice_8k_clean.wav', fs_new, data_clean)

# 5. Plot 1D Power Spectrum + Fixed-Contrast Spectrograms (Fixed Colorbar Layout)
fig = plt.figure(figsize=(14, 9))
# Create 3 columns: Left Plot, Right Plot, and a thin 3rd column strictly for the Colorbar
gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.3], width_ratios=[1, 1, 0.03])

# Top Plot (spanning all columns): 1D Power Spectral Density Comparison
ax_psd = fig.add_subplot(gs[0, :])
f_alias, Pxx_alias = welch(data_aliased, fs=fs_new, nperseg=1024)
f_clean, Pxx_clean = welch(data_clean, fs=fs_new, nperseg=1024)

ax_psd.plot(f_alias, 10 * np.log10(Pxx_alias), color='crimson', alpha=0.85, label='Aliased (No Filter) — Note 1.5 kHz Folded Spike & High-Freq Energy')
ax_psd.plot(f_clean, 10 * np.log10(Pxx_clean), color='royalblue', alpha=0.9, label='Clean (Order-8 Butterworth @ 3.4 kHz)')
ax_psd.axvline(3400, color='black', linestyle='--', label='Filter Cutoff (3.4 kHz)')
ax_psd.axvline(1500, color='crimson', linestyle=':', alpha=0.7, label='Aliased Tone (8000 - 6500 = 1500 Hz)')
ax_psd.set_title('1D Power Spectral Density (PSD): Aliased vs. Clean Decimation')
ax_psd.set_xlabel('Frequency [Hz]')
ax_psd.set_ylabel('Power/Frequency [dB/Hz]')
ax_psd.legend()
ax_psd.grid(True, alpha=0.4)

# Bottom Left: Aliased Spectrogram
ax1 = fig.add_subplot(gs[1, 0])
Pxx1, freqs1, bins1, im1 = ax1.specgram(data_aliased, Fs=fs_new, NFFT=256, cmap='viridis', vmin=-45, vmax=40)
ax1.axhline(3400, color='r', linestyle='--', alpha=0.7)
ax1.set_title('Aliased Spectrogram (No Filter)')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Frequency [Hz]')

# Bottom Middle: Clean Spectrogram
ax2 = fig.add_subplot(gs[1, 1], sharey=ax1)
Pxx2, freqs2, bins2, im2 = ax2.specgram(data_clean, Fs=fs_new, NFFT=256, cmap='viridis', vmin=-45, vmax=40)
ax2.axhline(3400, color='r', linestyle='--', alpha=0.7)
ax2.set_title('Clean Spectrogram (LPF @ 3.4 kHz — Note Dark Band Above 3.4 kHz)')
ax2.set_xlabel('Time [s]')

# Bottom Right: Dedicated Colorbar Axis (No Overlap)
cax = fig.add_subplot(gs[1, 2])
fig.colorbar(im2, cax=cax, label='Intensity [dB]')

plt.tight_layout()
plt.show()
