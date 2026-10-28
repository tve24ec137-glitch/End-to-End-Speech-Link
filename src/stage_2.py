import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

# 1. Load the Clean 8 kHz Signal
fs, data = wavfile.read('voice_8k_clean.wav')
x = data.astype(np.float64)
x = x / np.max(np.abs(x))  # Normalize strictly to [-1.0, 1.0]

# 2. Define DSP Functions
def quantize(signal, n_bits):
    """Symmetric mid-tread uniform quantiser"""
    L = 2**(n_bits - 1)
    q_sig = np.floor(signal * L + 0.5)  # Round to nearest quantization level
    q_sig = np.clip(q_sig, -L, L - 1)   # Enforce n-bit binary limits
    return q_sig / L                    # Map back to analog [-1.0, 1.0]

def mulaw_compress(signal, mu=255.0):
    """Logarithmic compression"""
    return np.sign(signal) * (np.log(1 + mu * np.abs(signal)) / np.log(1 + mu))

def mulaw_expand(signal, mu=255.0):
    """Inverse logarithmic expansion"""
    return np.sign(signal) * (((1 + mu)**np.abs(signal) - 1) / mu)

def calc_sqnr(sig, noise):
    # Add a small epsilon to prevent log10(0) if noise is zero
    return 10 * np.log10(np.mean(sig**2) / (np.mean(noise**2) + 1e-12))

# 3. Perform the Sweep (3 to 12 bits)
bits = np.arange(3, 13)
sqnr_theory = 6.02 * bits + 1.76
sqnr_uniform = []
sqnr_companded = []

mu = 255.0

for n in bits:
    # Path A: Uniform Quantisation
    x_q_uni = quantize(x, n)
    noise_uni = x - x_q_uni
    sqnr_uniform.append(calc_sqnr(x, noise_uni))
    
    # Path B: mu-law Companding
    x_comp = mulaw_compress(x, mu)       # 1. Compress
    x_comp_q = quantize(x_comp, n)       # 2. Quantise the compressed signal
    x_exp = mulaw_expand(x_comp_q, mu)   # 3. Expand back to normal scale
    
    noise_comp = x - x_exp
    sqnr_companded.append(calc_sqnr(x, noise_comp))

# 4. Save 8-bit versions for auditory comparison (Standard Telephony)
wavfile.write('voice_8bit_uniform.wav', fs, np.uint8((quantize(x, 8) + 1) * 127.5))
x_8bit_mu = mulaw_expand(quantize(mulaw_compress(x, mu), 8), mu)
wavfile.write('voice_8bit_mulaw.wav', fs, np.uint8((x_8bit_mu + 1) * 127.5))

# 5. Plotting Figure 3: SQNR vs Bit Depth
plt.figure(figsize=(10, 6))
plt.plot(bits, sqnr_theory, 'k--', label='Theoretical Sine Wave ($6.02n + 1.76$ dB)')
plt.plot(bits, sqnr_uniform, 'ro-', label='Measured Speech (Uniform)')
plt.plot(bits, sqnr_companded, 'bs-', label='Measured Speech ($\mu$-law, $\mu=255$)')

# Annotate the Crest Factor Penalty Gap
gap_x = 7
gap_y_theory = 6.02 * gap_x + 1.76
gap_y_measured = sqnr_uniform[gap_x - 3]
plt.annotate('', xy=(gap_x, gap_y_theory), xytext=(gap_x, gap_y_measured),
             arrowprops=dict(arrowstyle='<->', color='purple', lw=2))
plt.text(gap_x + 0.2, (gap_y_theory + gap_y_measured)/2, 
         f"Crest Factor Penalty\n(~15.5 dB drop)", color='purple', va='center')

plt.title('Figure 3: SQNR vs Bit Depth (Uniform vs. $\mu$-law)')
plt.xlabel('Resolution (bits)')
plt.ylabel('SQNR [dB]')
plt.xticks(bits)
plt.grid(True, alpha=0.5)
plt.legend()
plt.tight_layout()
plt.show()

# 6. Plotting Figure 4: The Companding Effect (Histograms)
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

# Plot the transfer function
sig_range = np.linspace(-1, 1, 1000)
ax1.plot(sig_range, mulaw_compress(sig_range, mu), 'b')
ax1.plot(sig_range, sig_range, 'k--', alpha=0.5)
ax1.set_title('$\mu$-law Transfer Function ($\mu=255$)')
ax1.set_xlabel('Input Amplitude')
ax1.set_ylabel('Compressed Amplitude')
ax1.grid(True)

# Original Histogram
ax2.hist(x, bins=100, color='red', alpha=0.7, density=True)
ax2.set_title('Original Speech Histogram\n(Clustered near zero)')
ax2.set_xlim([-1, 1])
ax2.grid(True, alpha=0.4)

# Compressed Histogram
ax3.hist(mulaw_compress(x, mu), bins=100, color='blue', alpha=0.7, density=True)
ax3.set_title('Compressed Speech Histogram\n(Pushed outward to use all bits)')
ax3.set_xlim([-1, 1])
ax3.grid(True, alpha=0.4)

plt.tight_layout()
plt.show()