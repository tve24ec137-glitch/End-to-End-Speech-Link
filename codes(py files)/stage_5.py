import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc

# 1. System Parameters
N_syms = 200000          # Number of symbols to simulate
SPS = 8                  # Samples per symbol
alpha = 0.35             # RRC Roll-off factor
span = 6                 # Filter span in symbols (each side)
EbNo_dB_range = np.arange(0, 15, 1)

# 2. Modulator Definitions (Gray Coded, Normalized to average power = 1)
def modulate_bpsk(bits):
    return 1.0 - 2.0 * bits

def modulate_qpsk(bits):
    I = 1.0 - 2.0 * bits[0::2]
    Q = 1.0 - 2.0 * bits[1::2]
    return (I + 1j * Q) / np.sqrt(2)

def modulate_16qam(bits):
    mapping = {(0,0): -3, (0,1): -1, (1,1): 1, (1,0): 3}
    syms = np.zeros(len(bits)//4, dtype=complex)
    for i in range(len(syms)):
        I = mapping[tuple(bits[4*i : 4*i+2])]
        Q = mapping[tuple(bits[4*i+2 : 4*i+4])]
        syms[i] = I + 1j * Q
    return syms / np.sqrt(10)

# 3. Demodulator Definitions (Decision Boundaries)
def demodulate_bpsk(rx_sym):
    return (np.real(rx_sym) < 0).astype(int)

def demodulate_qpsk(rx_sym):
    rx_bits = np.zeros(len(rx_sym) * 2, dtype=int)
    rx_bits[0::2] = (np.real(rx_sym) < 0).astype(int)
    rx_bits[1::2] = (np.imag(rx_sym) < 0).astype(int)
    return rx_bits

def demodulate_16qam(rx_sym):
    rx_sym = rx_sym * np.sqrt(10) # Denormalize
    rx_bits = np.zeros(len(rx_sym) * 4, dtype=int)
    for i, sym in enumerate(rx_sym):
        I, Q = np.real(sym), np.imag(sym)
        rx_bits[4*i:4*i+2] = [0,0] if I < -2 else [0,1] if I < 0 else [1,1] if I < 2 else [1,0]
        rx_bits[4*i+2:4*i+4] = [0,0] if Q < -2 else [0,1] if Q < 0 else [1,1] if Q < 2 else [1,0]
    return rx_bits

# 4. RRC Filter Design
def rrcosfilter(N, alpha, Ts, Fs):
    t = (np.arange(N) - N/2) / Fs
    t += 1e-12 
    num = np.sin(np.pi * t / Ts * (1 - alpha)) + 4 * alpha * t / Ts * np.cos(np.pi * t / Ts * (1 + alpha))
    den = np.pi * t / Ts * (1 - (4 * alpha * t / Ts)**2)
    h = num / den
    return h / np.sqrt(np.sum(h**2)) # Normalize to unit energy

filt_len = 2 * span * SPS + 1
h_rrc = rrcosfilter(filt_len, alpha, Ts=1.0, Fs=SPS)
filter_delay = span * SPS * 2 # Total delay after TX and RX convolution

# 5. Generate Data and Modulate
bits_bpsk = np.random.randint(0, 2, N_syms)
bits_qpsk = np.random.randint(0, 2, N_syms * 2)
bits_16qam = np.random.randint(0, 2, N_syms * 4)

sym_tx_bpsk = modulate_bpsk(bits_bpsk)
sym_tx_qpsk = modulate_qpsk(bits_qpsk)
sym_tx_16qam = modulate_16qam(bits_16qam)

# 6. Upsample and TX Pulse Shaping
def tx_pipeline(syms):
    up = np.zeros(len(syms) * SPS, dtype=complex)
    up[0::SPS] = syms
    return np.convolve(up, h_rrc, 'full')

sig_tx_bpsk = tx_pipeline(sym_tx_bpsk)
sig_tx_qpsk = tx_pipeline(sym_tx_qpsk)
sig_tx_16qam = tx_pipeline(sym_tx_16qam)

# 7. Simulation Loop
ber_bpsk, ber_qpsk, ber_16qam = [], [], []
scatter_data = {4: {}, 8: {}, 14: {}} # Store symbols for scatter plots

for EbNo in EbNo_dB_range:
    EbNo_lin = 10**(EbNo / 10.0)
    
    # Calculate noise variance directly (since filters have unit energy, variance passes through 1:1)
    N0_bpsk = 1.0 / (EbNo_lin * 1)
    N0_qpsk = 1.0 / (EbNo_lin * 2)
    N0_16qam = 1.0 / (EbNo_lin * 4)
    
    def channel_and_rx(sig_tx, N0, num_syms):
        # AWGN Channel
        noise = np.sqrt(N0 / 2) * (np.random.randn(len(sig_tx)) + 1j * np.random.randn(len(sig_tx)))
        sig_rx = sig_tx + noise
        
        # RX Matched Filter
        sig_rx_filtered = np.convolve(sig_rx, h_rrc, 'full')
        
        # Symbol-rate sampling (Downsample taking delay into account)
        sym_rx = sig_rx_filtered[filter_delay : filter_delay + num_syms * SPS : SPS]
        return sym_rx

    # Process all three modulation schemes
    sym_rx_bpsk = channel_and_rx(sig_tx_bpsk, N0_bpsk, N_syms)
    sym_rx_qpsk = channel_and_rx(sig_tx_qpsk, N0_qpsk, N_syms)
    sym_rx_16qam = channel_and_rx(sig_tx_16qam, N0_16qam, N_syms)
    
    # Save scatter plot data at specific Eb/N0 values
    if EbNo in scatter_data:
        scatter_data[EbNo]['BPSK'] = sym_rx_bpsk[:2000]
        scatter_data[EbNo]['QPSK'] = sym_rx_qpsk[:2000]
        scatter_data[EbNo]['16-QAM'] = sym_rx_16qam[:2000]
        
    # Demodulate and calculate BER
    ber_bpsk.append(np.sum(bits_bpsk != demodulate_bpsk(sym_rx_bpsk)) / len(bits_bpsk))
    ber_qpsk.append(np.sum(bits_qpsk != demodulate_qpsk(sym_rx_qpsk)) / len(bits_qpsk))
    ber_16qam.append(np.sum(bits_16qam != demodulate_16qam(sym_rx_16qam)) / len(bits_16qam))

# 8. Theoretical Math Verification
EbNo_lin_sweep = 10**(EbNo_dB_range / 10.0)
theory_bpsk_qpsk = 0.5 * erfc(np.sqrt(EbNo_lin_sweep))
theory_16qam = (3.0 / 8.0) * erfc(np.sqrt(0.4 * EbNo_lin_sweep))

# 9. Plot 1: BER Waterfall Curves
plt.figure(figsize=(9, 6))
plt.semilogy(EbNo_dB_range, theory_bpsk_qpsk, 'k-', lw=2, label='Theory (BPSK/QPSK): $Q(\sqrt{2E_b/N_0})$')
plt.semilogy(EbNo_dB_range, theory_16qam, 'k--', lw=2, label='Theory (16-QAM): erfc expression')
plt.semilogy(EbNo_dB_range, ber_bpsk, 'ro', markersize=6, label='Simulated BPSK')
plt.semilogy(EbNo_dB_range, ber_qpsk, 'bx', markersize=8, label='Simulated QPSK')
plt.semilogy(EbNo_dB_range, ber_16qam, 'g^', markersize=6, label='Simulated 16-QAM')

plt.title('Figure 8: End-to-End Pulse-Shaped BER vs $E_b/N_0$')
plt.xlabel('$E_b/N_0$ (dB)')
plt.ylabel('Bit Error Rate (BER)')
plt.ylim([1e-5, 1])
plt.grid(True, which='both', linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()

# 10. Plot 2: Constellation Scatter Plots (3x3 Grid)
fig, axes = plt.subplots(3, 3, figsize=(12, 12))
schemes = ['BPSK', 'QPSK', '16-QAM']
levels = [4, 8, 14]
colors = ['firebrick', 'teal', 'darkmagenta']

for i, scheme in enumerate(schemes):
    for j, level in enumerate(levels):
        ax = axes[i, j]
        syms = scatter_data[level][scheme]
        ax.scatter(np.real(syms), np.imag(syms), s=2, alpha=0.5, color=colors[i])
        ax.axhline(0, color='black', lw=0.5)
        ax.axvline(0, color='black', lw=0.5)
        ax.set_aspect('equal', 'box')
        ax.set_title(f'{scheme} at $E_b/N_0 = {level}$ dB')
        ax.set_xlim([-1.5, 1.5])
        ax.set_ylim([-1.5, 1.5])
        if scheme == '16-QAM':
            ax.set_xlim([-1.5, 1.5])
            ax.set_ylim([-1.5, 1.5])
            
plt.tight_layout()
plt.show()