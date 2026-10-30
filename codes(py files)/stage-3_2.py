import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

# 1. Load your 8-bit mu-law audio from Stage 2
fs, rx_audio_raw = wavfile.read('voice_8bit_mulaw.wav')

# 2. Convert Audio to Binary Bitstream
# np.unpackbits takes an array of 8-bit integers and turns it into a flat array of 1s and 0s
bitstream = np.unpackbits(rx_audio_raw)
print(f"Total bits to transmit: {len(bitstream)}")

# 3. QPSK Modulation
def modulate_qpsk(bits):
    # Ensure even number of bits for QPSK (2 bits per symbol)
    if len(bits) % 2 != 0:
        bits = np.append(bits, 0)
    I = 1.0 - 2.0 * bits[0::2]
    Q = 1.0 - 2.0 * bits[1::2]
    return (I + 1j * Q) / np.sqrt(2)

def demodulate_qpsk(rx_symbols, num_bits):
    rx_bits = np.zeros(len(rx_symbols) * 2, dtype=np.uint8)
    rx_bits[0::2] = (np.real(rx_symbols) < 0).astype(np.uint8)
    rx_bits[1::2] = (np.imag(rx_symbols) < 0).astype(np.uint8)
    return rx_bits[:num_bits] # Trim padded bit if any

# 4. AWGN Channel
def add_awgn(symbols, EbNo_dB, bits_per_symbol=2):
    EbNo_lin = 10**(EbNo_dB / 10.0)
    SNR_lin = EbNo_lin * bits_per_symbol
    noise_power = 1.0 / SNR_lin
    noise = np.sqrt(noise_power / 2) * (np.random.randn(len(symbols)) + 1j * np.random.randn(len(symbols)))
    return symbols + noise

# 5. mu-law Expansion Helper (to convert back to playable 16-bit PCM for standard players)
def mulaw_expand(signal_8bit, mu=255.0):
    # Convert 0-255 unsigned back to -1.0 to 1.0 float
    norm_sig = (signal_8bit.astype(np.float64) / 127.5) - 1.0
    return np.sign(norm_sig) * (((1 + mu)**np.abs(norm_sig) - 1) / mu)

# 6. Transmit at Different Noise Levels
test_EbNo_levels = [12, 6, 2] # 12 dB (Clear), 6 dB (Noisy), 2 dB (Heavy Corruption)

symbols_tx = modulate_qpsk(bitstream)

for EbNo in test_EbNo_levels:
    print(f"Simulating Transmission at Eb/No = {EbNo} dB...")
    
    # Pass through channel
    symbols_rx = add_awgn(symbols_tx, EbNo, bits_per_symbol=2)
    
    # Demodulate back to bits
    bits_rx = demodulate_qpsk(symbols_rx, len(bitstream))
    
    # Calculate actual BER for this run
    ber = np.sum(bitstream != bits_rx) / len(bitstream)
    print(f"  Measured BER: {ber:.5f}")
    
    # Pack bits back into 8-bit bytes
    audio_rx_8bit = np.packbits(bits_rx)
    
    # Expand mu-law back to 16-bit linear PCM so it sounds correct on all media players
    audio_expanded = mulaw_expand(audio_rx_8bit)
    audio_16bit_out = np.int16(audio_expanded * 32767)
    
    # Save the corrupted audio
    wavfile.write(f'voice_rx_{EbNo}dB.wav', fs, audio_16bit_out)

print("Transmission complete! Listen to the output WAV files.")