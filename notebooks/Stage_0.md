**Stage 0: Acquisition and Analysis**

**1. Objective and What We Did**
In Stage 0, we recorded an uncompressed 11.99-second mono speech sample at a 48 kHz sampling rate (16-bit PCM WAV). We loaded the raw audio signal into Python to analyze its time-domain behavior (Speech Waveform), examine its frequency distribution over time (Spectrogram), and calculate its Crest Factor to justify our design choices for the upcoming sampling and quantization stages.

---

**2. What is the Amplitude in the First Figure?**

* **16-Bit Digital Sample Values:** Because the audio is recorded in 16-bit signed PCM format, the Y-axis ("Amplitude") in the first figure does not show volts directly; instead, it shows the raw 16-bit integer quantization levels ranging from -32,768 to +32,767.
* **Signal Range and Headroom:** In our waveform plot, the loudest speech peaks reach approximately +28,000 on the positive side and -21,000 on the negative side. This confirms a strong, clear recording that uses most of the 16-bit dynamic range without hitting the 32,767 limit (which would cause audio clipping/distortion).


* **Spiky Nature of Speech:** While the peaks hit ~28,000, the majority of the normal speech vibrations sit much lower (between -5,000 and +5,000), with near-zero flat regions during pauses.



---

**3. Crest Factor (Peak-to-RMS Ratio)**

* **Measured Values:**
* **Sampling Rate:** 44,100 Hz
* **Duration:** 11.99 seconds


* **Crest Factor (Linear):** 8.51
* **Crest Factor (dB):** 18.59 dB

**Crest Factor** is the **Peak-to-RMS ratio** of a signal, which measures how extreme a signal's loudest spikes are compared to its average (RMS) power:

$$\text{CF}_{\text{linear}} = \frac{A_{\text{peak}}}{A_{\text{rms}}} \quad \text{and} \quad \text{CF}_{\text{dB}} = 20 \log_{10}\left(\frac{A_{\text{peak}}}{A_{\text{rms}}}\right)$$

In Stage 0 waveform, brief consonant bursts spike all the way up to **~28,000**, while the majority of your voice vibrations sit much lower (below **5,000**) alongside silent pauses. Because the peaks are **8.51 times** larger than the average level, your speech is "spiky" and has a high crest factor of **18.59 dB**—unlike a continuous, full-scale sine wave, which has a low crest factor of $\sqrt{2} \approx 1.414$ (**3.01 dB**).


---

**4. Observations from Comparing the Two Plots (Waveform vs. Spectrogram)**
When looking at the **Speech Waveform (top)** directly aligned with the **Spectrogram (bottom)** across the same 12-second timeline, we observe three key behaviors:

* **Time Alignment of Speech Bursts and Silence:** Every time a word is spoken (between 0.8–4.2 seconds and 5.5–11.5 seconds), the waveform shows sharp amplitude spikes, which correspond directly to bright yellow vertical lines of high intensity (up to +40 dB) in the spectrogram below it. Conversely, during the silent pause between 4.2 and 5.5 seconds, the waveform flattens out near 0, and the spectrogram turns a uniform dark green/blue (around -40 to -60 dB), showing only low background noise.


* **Where the Voice Energy Lives (Occupied Bandwidth):** Looking vertically at the spectrogram during the active speech bursts, the brightest yellow regions (highest acoustic intensity) are heavily concentrated at the bottom of the plot, below 3,400 Hz (and especially dense below 2,000 Hz).


* **High-Frequency Drop-Off:** Above 4,000 Hz, the intensity fades mostly into green (-20 to -40 dB), with only occasional faint vertical streaks during sharp consonant sounds (like "s" or "t").



---

**5. Stage 0 Conclusion (Why 8 kHz is Enough)**
Comparing both plots proves that nearly all the meaningful energy of our recorded voice sits below 4,000 Hz. By the Nyquist-Shannon sampling theorem (fs >= 2 * f_max), downsampling our 48 kHz recording to an **8 kHz target sampling rate** (which captures frequencies up to 4 kHz) will preserve full speech intelligibility while cutting the required data rate by a factor of 6.
