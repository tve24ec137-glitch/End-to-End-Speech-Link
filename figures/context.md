* **`voice.wav`**: The pristine, original 44.1 kHz continuous audio recording. This serves as the source file and the baseline for the final Segmental SNR calculations.


* **`voice_noisy.wav`**: The 44.1 kHz audio with a continuous high-frequency tone (6.5 kHz) artificially injected. This was used in Stage 1 to explicitly test the effects of Nyquist aliasing.


* **`voice_8k_aliased.wav`**: The Stage 1 decimation failure. This is the result of downsampling `voice_noisy.wav` directly to 8 kHz without prior filtering. The 6.5 kHz tone violated the 4 kHz Nyquist limit and folded back, creating a loud 1.5 kHz ringing distortion.


* **`voice_8k_clean.wav`**: The Stage 1 decimation success. The noisy audio was passed through a 3.4 kHz Butterworth Low-Pass Filter before downsampling. The filter stripped away the out-of-band energy, yielding clean telephone-bandwidth speech.


* **`voice_8bit_uniform.wav`**: The Stage 2 uniform quantization output. The clean 8 kHz signal was uniformly quantized to 8 bits, resulting in a poor SQNR and noticeable gritty background static due to the natural crest factor of human speech.


* **`voice_8bit_mulaw.wav`**: The Stage 2 companded quantization output. The signal was logarithmically compressed using $\mu$-law ($\mu=255$) before 8-bit quantization. This optimized the dynamic range, eliminated the gritty static, and became the binary payload for transmission.


* **`voice_rx_12dB.wav`, `voice_rx_6dB.wav`, `voice_rx_2dB.wav**`: The Stage 3 discrete transmission verification files. These represent the baseband 8 kHz $\mu$-law audio recovered after raw QPSK mapping and transmission through a discrete AWGN channel at 12 dB (error-free), 6 dB (minor clicks/pops from bit errors), and 2 dB (severe robotic static).


* **`voice_reconstructed_14dB.wav`, `voice_reconstructed_8dB.wav`, `voice_reconstructed_4dB.wav**`: The final Stage 6 end-to-end pipeline outputs. These represent the full continuous-time physical layer transmission. The bits were RRC pulse-shaped, transmitted through AWGN, matched-filtered, de-mapped, passed through the $\mu$-law inverse expander, and smoothly interpolated through a polyphase anti-imaging filter back to a 44.1 kHz acoustic waveform at 14 dB (clean), 8 dB (clicks), and 4 dB (link failure).
