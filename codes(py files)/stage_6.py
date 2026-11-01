import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
import warnings
warnings.filterwarnings("ignore")

# 1. System Parameters
SPS = 8
alpha = 0.35
span = 6
EbNo_dB_levels = [4, 8, 14]  # The SNR points requested in Stage 5

# Load original 44.1 kHz audio (for Segmental SNR comparison)
fs_orig, original_audio = wavfile.read('voice.wav')

# FIX: If the original audio is stereo (2 channels), convert it to mono
if original_audio.ndim > 1:
    original_audio = original_audio[:, 0]

original_audio = original_audio / np.max(np.abs(original_audio)) # Normalize

# Load Stage 2 quantised audio to get the bits
fs_8k, tx_audio_8bit = wavfile.read('voice_8bit_mulaw.wav')
bitstream = np.unpackbits(tx_audio_8bit)

# 2. Modulate & Pulse Shape (Re-using Stage 4/5 logic)
def modulate_qpsk(bits):
    if len(bits) % 2 != 0: bits = np.append(bits, 0)
    I = 1.0 - 2.0 * bits[0::2]
    Q = 1.0 - 2.0 * bits[1::2]
    return (I + 1j * Q) / np.sqrt(2)

def rrcosfilter(N, alpha, Ts, Fs):
    t = (np.arange(N) - N/2) / Fs + 1e-12 
    num = np.sin(np.pi * t / Ts * (1 - alpha)) + 4 * alpha * t / Ts * np.cos(np.pi * t / Ts * (1 + alpha))
    den = np.pi * t / Ts * (1 - (4 * alpha * t / Ts)**2)
    h = num / den
    return h / np.sqrt(np.sum(h**2))

h_rrc = rrcosfilter(2 * span * SPS + 1, alpha, 1.0, SPS)
filter_delay = span * SPS * 2

syms_tx = modulate_qpsk(bitstream)
up = np.zeros(len(syms_tx) * SPS, dtype=complex)
up[0::SPS] = syms_tx
sig_tx = np.convolve(up, h_rrc, 'full')

# 3. Expansion and Segmental SNR Helpers
def mulaw_expand(signal_8bit, mu=255.0):
    norm_sig = (signal_8bit.astype(np.float64) / 127.5) - 1.0
    return np.sign(norm_sig) * (((1 + mu)**np.abs(norm_sig) - 1) / mu)

def calculate_segmental_snr(ref, deg, fs, frame_len_ms=20):
    # Align lengths
    min_len = min(len(ref), len(deg))
    ref = ref[:min_len]
    deg = deg[:min_len]
    
    frame_len = int((frame_len_ms / 1000.0) * fs)
    num_frames = min_len // frame_len
    
    seg_snr = []
    for i in range(num_frames):
        start = i * frame_len
        end = start + frame_len
        ref_frame = ref[start:end]
        deg_frame = deg[start:end]
        
        noise_frame = ref_frame - deg_frame
        ref_power = np.sum(ref_frame**2)
        noise_power = np.sum(noise_frame**2)
        
        if noise_power > 0 and ref_power > 0:
            snr = 10 * np.log10(ref_power / noise_power)
            # Bound the SNR to prevent silent frames from skewing the average
            snr = max(-10, min(snr, 35)) 
            seg_snr.append(snr)
            
    return np.mean(seg_snr) if seg_snr else 0.0

# 4. Receiver, Demap, and Interpolate Loop
print("--- STAGE 6: AUDIO RECONSTRUCTION & SEGMENTAL SNR ---")

for EbNo in EbNo_dB_levels:
    print(f"\nProcessing Eb/No = {EbNo} dB...")
    EbNo_lin = 10**(EbNo / 10.0)
    N0 = 1.0 / (EbNo_lin * 2) # QPSK
    
    # Channel & Matched Filter
    noise = np.sqrt(N0 / 2) * (np.random.randn(len(sig_tx)) + 1j * np.random.randn(len(sig_tx)))
    sig_rx = sig_tx + noise
    sig_rx_filtered = np.convolve(sig_rx, h_rrc, 'full')
    
    # Downsample and Demap
    syms_rx = sig_rx_filtered[filter_delay : filter_delay + len(syms_tx) * SPS : SPS]
    
    rx_bits = np.zeros(len(syms_rx) * 2, dtype=np.uint8)
    rx_bits[0::2] = (np.real(syms_rx) < 0).astype(np.uint8)
    rx_bits[1::2] = (np.imag(syms_rx) < 0).astype(np.uint8)
    rx_bits = rx_bits[:len(bitstream)] # Trim padding
    
    # Pack bits to bytes and Expand
    rx_audio_8bit = np.packbits(rx_bits)
    rx_audio_expanded = mulaw_expand(rx_audio_8bit)
    
    # Interpolate from 8 kHz to 44.1 kHz (Up by 441, Down by 80)
    # resample_poly automatically applies the anti-imaging low-pass filter!
    rx_audio_44k = resample_poly(rx_audio_expanded, 441, 80)
    
    # Calculate Segmental SNR against original 44.1 kHz audio
    seg_snr = calculate_segmental_snr(original_audio, rx_audio_44k, fs=44100)
    print(f"Segmental SNR: {seg_snr:.2f} dB")
    
    # Write to WAV
    rx_audio_out = np.int16(rx_audio_44k / np.max(np.abs(rx_audio_44k)) * 32767)
    filename = f'voice_reconstructed_{EbNo}dB.wav'
    wavfile.write(filename, 44100, rx_audio_out)
    print(f"Saved: {filename}")

print("\nStage 6 complete! Audio files rendered.")