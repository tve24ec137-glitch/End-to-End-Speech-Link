import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

# 1. System Parameters
num_symbols = 50000
SPS = 8                  # Samples per symbol (Oversampling factor)
alpha = 0.35             # RRC Roll-off factor
Rs = 1.0                 # Symbol rate (Normalized to 1 symbol/sec for baseband)
Fs = SPS * Rs            # Sampling frequency
EbNo_dB = 10.0           # Target Eb/N0 in dB

# 2. QPSK Symbol Generation
bits = np.random.randint(0, 2, num_symbols * 2)
I = 1.0 - 2.0 * bits[0::2]
Q = 1.0 - 2.0 * bits[1::2]
symbols = (I + 1j * Q) / np.sqrt(2)  # Normalized to average energy Es = 1

# 3. Upsampling (Insert SPS-1 zeros between symbols)
upsampled = np.zeros(num_symbols * SPS, dtype=complex)
upsampled[0::SPS] = symbols

# 4. Root-Raised Cosine (RRC) Filter Design
def rrcosfilter(N, alpha, Ts, Fs):
    t = (np.arange(N) - N/2) / Fs
    t += 1e-12  # Tiny offset to prevent divide-by-zero at t=0 and t=Ts/(4*alpha)
    
    num = np.sin(np.pi * t / Ts * (1 - alpha)) + 4 * alpha * t / Ts * np.cos(np.pi * t / Ts * (1 + alpha))
    den = np.pi * t / Ts * (1 - (4 * alpha * t / Ts)**2)
    h = num / den
    
    # Normalize to unit energy so the filter doesn't amplify/attenuate signal power
    return h / np.sqrt(np.sum(h**2))

# Create filter with length spanning 6 symbols on each side
filt_len = 6 * 2 * SPS + 1
rrc_h = rrcosfilter(filt_len, alpha, Ts=1/Rs, Fs=Fs)

# 5. Pulse Shaping (Convolution)
tx_sig = np.convolve(upsampled, rrc_h, 'same')

# 6. AWGN Channel & Verification 1: Noise Variance Match
EbNo_lin = 10**(EbNo_dB / 10.0)
Es = 1.0                           # QPSK symbol energy
Eb = Es / 2.0                      # 2 bits per QPSK symbol
N0 = Eb / EbNo_lin                 # Required Noise Power Spectral Density

# In discrete time, complex noise variance (sigma^2) is N0 * Fs (where Fs = SPS * Rs)
theoretical_variance = N0 * Fs 

# Generate complex AWGN
noise = np.sqrt(theoretical_variance / 2) * (np.random.randn(len(tx_sig)) + 1j * np.random.randn(len(tx_sig)))
rx_sig = tx_sig + noise

measured_variance = np.var(noise)

print("--- VERIFICATION 1: NOISE VARIANCE ---")
print(f"Target Eb/N0:        {EbNo_dB} dB")
print(f"Theoretical Var:     {theoretical_variance:.6f}")
print(f"Actually Generated:  {measured_variance:.6f}")
print(f"Error Margin:        {abs(theoretical_variance - measured_variance)/theoretical_variance * 100:.4f}%\n")

# 7. Verification 2: Plot Transmit Spectrum and Confirm Bandwidth
f, Pxx = welch(tx_sig, fs=Fs, nperseg=2048, return_onesided=False)
f = np.fft.fftshift(f)
Pxx = np.fft.fftshift(Pxx)
Pxx_dB = 10 * np.log10(Pxx / np.max(Pxx))  # Normalize peak to 0 dB

theoretical_bw = (1 + alpha) * Rs
nyquist_bw = Rs  # (1 - alpha)*Rs to (1 + alpha)*Rs transitions around Rs/2

plt.figure(figsize=(10, 6))
plt.plot(f, Pxx_dB, 'b', label='Transmitted QPSK Spectrum (Baseband)')

# Draw boundary lines for (1+alpha)*Rs bandwidth
plt.axvline(theoretical_bw / 2, color='r', linestyle='--', label=f'Absolute Bandwidth Edge (±{(theoretical_bw/2):.3f} Hz)')
plt.axvline(-theoretical_bw / 2, color='r', linestyle='--')

# Draw boundary lines for Nyquist minimum bandwidth (Rs/2)
plt.axvline(nyquist_bw / 2, color='k', linestyle=':', label=f'Nyquist Bandwidth Edge (±{(nyquist_bw/2):.3f} Hz)')
plt.axvline(-nyquist_bw / 2, color='k', linestyle=':')

plt.title('Figure 7: Transmit Spectrum of RRC Pulse-Shaped QPSK')
plt.xlabel('Frequency (Hz) [Normalized to Symbol Rate]')
plt.ylabel('Power Spectral Density [dB/Hz]')
plt.ylim([-60, 5])
plt.xlim([-Fs/2, Fs/2])
plt.grid(True, alpha=0.5)
plt.legend(loc='upper right')
plt.tight_layout()
plt.show()