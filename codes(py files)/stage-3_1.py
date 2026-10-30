import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc

# 1. Configuration
N_bits = 3 * 10**6  # 3 million bits for smooth statistics at high SNR
EbNo_dB_range = np.arange(0, 15, 1)  # Sweep from 0 to 14 dB
bits = np.random.randint(0, 2, N_bits)

# 2. Modulator Definitions (Gray Coded)
def modulate_bpsk(bits):
    return 1.0 - 2.0 * bits  # 0 -> +1, 1 -> -1

def modulate_qpsk(bits):
    # Map bits to QPSK (Gray coded: 00, 01, 11, 10)
    I = 1.0 - 2.0 * bits[0::2]
    Q = 1.0 - 2.0 * bits[1::2]
    return (I + 1j * Q) / np.sqrt(2) # Normalize average power to 1

def modulate_16qam(bits):
    # Map 4 bits per symbol using Gray coding
    mapping = {
        (0,0): -3, (0,1): -1, (1,1): 1, (1,0): 3
    }
    symbols = np.zeros(len(bits)//4, dtype=complex)
    for i in range(len(symbols)):
        b0, b1, b2, b3 = bits[4*i:4*i+4]
        I = mapping[(b0, b1)]
        Q = mapping[(b2, b3)]
        symbols[i] = I + 1j * Q
    return symbols / np.sqrt(10) # Normalize average power to 1 (sqrt(10) since avg power of +/-1, +/-3 is 10)

# 3. AWGN Channel & Demodulation Helpers
def add_awgn(symbols, snr_linear):
    noise_power = 1.0 / snr_linear
    noise = np.sqrt(noise_power / 2) * (np.random.randn(len(symbols)) + 1j * np.random.randn(len(symbols)))
    return symbols + noise

def demodulate_bpsk(rx_symbols):
    return (np.real(rx_symbols) < 0).astype(int)

def demodulate_qpsk(rx_symbols):
    rx_bits = np.zeros(len(rx_symbols) * 2, dtype=int)
    rx_bits[0::2] = (np.real(rx_symbols) < 0).astype(int)
    rx_bits[1::2] = (np.imag(rx_symbols) < 0).astype(int)
    return rx_bits

def demodulate_16qam(rx_symbols):
    # Scale back from normalized power
    rx_symbols = rx_symbols * np.sqrt(10)
    rx_bits = np.zeros(len(rx_symbols) * 4, dtype=int)
    
    for i, sym in enumerate(rx_symbols):
        # I-channel decision boundaries
        I = np.real(sym)
        if I < -2:   rx_bits[4*i:4*i+2] = [0, 0]
        elif I < 0:  rx_bits[4*i:4*i+2] = [0, 1]
        elif I < 2:  rx_bits[4*i:4*i+2] = [1, 1]
        else:        rx_bits[4*i:4*i+2] = [1, 0]
        
        # Q-channel decision boundaries
        Q = np.imag(sym)
        if Q < -2:   rx_bits[4*i+2:4*i+4] = [0, 0]
        elif Q < 0:  rx_bits[4*i+2:4*i+4] = [0, 1]
        elif Q < 2:  rx_bits[4*i+2:4*i+4] = [1, 1]
        else:        rx_bits[4*i+2:4*i+4] = [1, 0]
        
    return rx_bits

# 4. Perform the BER Simulation
ber_bpsk, ber_qpsk, ber_16qam = [], [], []

sym_bpsk = modulate_bpsk(bits)
sym_qpsk = modulate_qpsk(bits)
sym_16qam = modulate_16qam(bits)

for EbNo in EbNo_dB_range:
    EbNo_lin = 10**(EbNo / 10.0)
    
    # BPSK (1 bit/symbol) => SNR = EbNo
    rx_bpsk = add_awgn(sym_bpsk, EbNo_lin * 1)
    ber_bpsk.append(np.sum(bits != demodulate_bpsk(rx_bpsk)) / N_bits)
    
    # QPSK (2 bits/symbol) => SNR = EbNo * 2
    rx_qpsk = add_awgn(sym_qpsk, EbNo_lin * 2)
    ber_qpsk.append(np.sum(bits != demodulate_qpsk(rx_qpsk)) / N_bits)
    
    # 16-QAM (4 bits/symbol) => SNR = EbNo * 4
    rx_16qam = add_awgn(sym_16qam, EbNo_lin * 4)
    ber_16qam.append(np.sum(bits != demodulate_16qam(rx_16qam)) / N_bits)

# Theoretical Curves
EbNo_lin_sweep = 10**(EbNo_dB_range / 10.0)
theory_bpsk_qpsk = 0.5 * erfc(np.sqrt(EbNo_lin_sweep))
theory_16qam = (3.0 / 8.0) * erfc(np.sqrt(0.4 * EbNo_lin_sweep))

# 5. Plotting Figure 5: BER Waterfall Curves
plt.figure(figsize=(9, 6))
plt.semilogy(EbNo_dB_range, theory_bpsk_qpsk, 'k-', lw=2, label='Theory (BPSK/QPSK)')
plt.semilogy(EbNo_dB_range, theory_16qam, 'k--', lw=2, label='Theory (16-QAM)')
plt.semilogy(EbNo_dB_range, ber_bpsk, 'ro', markersize=6, label='Simulated BPSK')
plt.semilogy(EbNo_dB_range, ber_qpsk, 'bx', markersize=8, label='Simulated QPSK')
plt.semilogy(EbNo_dB_range, ber_16qam, 'g^', markersize=6, label='Simulated 16-QAM')

plt.title('Figure 5: BER vs $E_b/N_0$ over AWGN Channel')
plt.xlabel('$E_b/N_0$ (dB)')
plt.ylabel('Bit Error Rate (BER)')
plt.ylim([1e-5, 1])
plt.grid(True, which='both', linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()

# 6. Plotting Figure 6: Constellation Diagrams (at Eb/No = 10 dB)
EbNo_const_lin = 10**(10 / 10.0)
rx_const_bpsk = add_awgn(sym_bpsk[:2000], EbNo_const_lin * 1)
rx_const_qpsk = add_awgn(sym_qpsk[:2000], EbNo_const_lin * 2)
rx_const_16qam = add_awgn(sym_16qam[:2000], EbNo_const_lin * 4)

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

def plot_const(ax, rx_sym, title):
    ax.scatter(np.real(rx_sym), np.imag(rx_sym), s=5, alpha=0.5, c='teal')
    ax.axhline(0, color='black', lw=1, alpha=0.5)
    ax.axvline(0, color='black', lw=1, alpha=0.5)
    ax.set_aspect('equal', 'box')
    ax.set_title(title)
    ax.set_xlim([-1.5, 1.5])
    ax.set_ylim([-1.5, 1.5])
    ax.grid(True, alpha=0.4)

plot_const(ax1, rx_const_bpsk, 'BPSK Constellation\n($E_b/N_0 = 10$ dB)')
plot_const(ax2, rx_const_qpsk, 'QPSK Constellation\n($E_b/N_0 = 10$ dB)')
plot_const(ax3, rx_const_16qam, '16-QAM Constellation\n($E_b/N_0 = 10$ dB)')

plt.tight_layout()
plt.show()