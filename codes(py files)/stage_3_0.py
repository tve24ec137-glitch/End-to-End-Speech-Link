import numpy as np
from scipy.io import wavfile

# 1. Load the quantized Stage 2 audio
fs, tx_audio = wavfile.read('voice_8bit_mulaw.wav')

# 2. Serialise to bits (MSB-first)
tx_bits = np.unpackbits(tx_audio)

# 3. Gray-map to QPSK
def modulate_qpsk(bits):
    if len(bits) % 2 != 0:
        bits = np.append(bits, 0)
    I = 1.0 - 2.0 * bits[0::2]
    Q = 1.0 - 2.0 * bits[1::2]
    return (I + 1j * Q) / np.sqrt(2)

tx_symbols = modulate_qpsk(tx_bits)

# --- NO CHANNEL (Zero Noise) ---
rx_symbols = tx_symbols 

# 4. Unmap QPSK back to bits
def demodulate_qpsk(rx_sym, num_bits):
    rx_bits = np.zeros(len(rx_sym) * 2, dtype=np.uint8)
    rx_bits[0::2] = (np.real(rx_sym) < 0).astype(np.uint8)
    rx_bits[1::2] = (np.imag(rx_sym) < 0).astype(np.uint8)
    return rx_bits[:num_bits]

rx_bits = demodulate_qpsk(rx_symbols, len(tx_bits))

# 5. Verify Bit-Identical Match
assert np.array_equal(tx_bits, rx_bits), "ERROR: Transmitted and received bits do not match!"
print("Verification Passed: The recovered bitstream is 100% bit-identical to the input.")

# 6. Reconstruct Audio
rx_audio = np.packbits(rx_bits)
assert np.array_equal(tx_audio, rx_audio), "ERROR: Audio arrays do not match!"
print("Verification Passed: The reconstructed WAV array is bit-identical to the quantised input.")