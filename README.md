# End-to-End-Speech-Link
End-to-End Speech LinkCourse Project: Analog & Digital Communication

Team Members
Vysakh P Chandran (69)Ujjwal Skandakumar P (68)Rohann Subhash (55)

Project Overview:
This project investigates the cumulative degradation of an analog speech signal as it passes through a complete digital communication pipeline. By capturing an analog voice recording and processing it through anti-aliasing, sampling, quantization, companding, modulation, and a noisy AWGN channel, we analyze where signal quality drops the most. The goal is to determine at what noise levels the audio becomes unintelligible, bridging mathematical bit-error rates with perceived human speech quality.

Stage 0: Acquisition and Analysis

Prerequisites
Ensure you have Python installed along with the required digital signal processing libraries. You can install the dependencies using 
pip:Bashpip install numpy scipy matplotlib

Input Audio Requirements
Place your audio recording in the root directory of this project. Ensure the file matches the following parameters:   
Filename: audio_1.wav
Format: Uncompressed PCM WAV
Bit Depth: 16-bit
Sampling Rate: 44.1 kHzChannels: Mono (script will auto-convert stereo if necessary)
Duration: 8 to 15 seconds of connected speech

Running the Analysis
Run the provided Stage 0 analysis script from your terminal:
python stage_0.py

Expected Outputs

1.Console Output: 
The script will print the file's sample rate, duration, and compute the Crest Factor (Peak-to-RMS ratio) in both linear and dB scales.

2.Visualizations: 
A figure will generate containing:

Time-Domain Waveform: Demonstrating speech amplitude over time.   
Spectrogram: Visualizing the frequency distribution (occupied bandwidth) over time to confirm the concentration of speech energy below 4 kHz


**Stage 1: Anti-Aliasing and Sampling**

**1. Objective and Methodology**
The objective of this stage was to downsample the original 44.1 kHz speech recording to the target transmission rate of 8 kHz. To explicitly demonstrate the effects of aliasing, we artificially injected a high-frequency continuous tone (6.5 kHz) into the original 44.1 kHz audio. The decimation process was then executed via two distinct paths:

* **Path A (Deliberate Aliasing):** Downsampling directly to 8 kHz without applying any prior filtering.
* **Path B (Correct Anti-Aliasing):** Pre-filtering the signal through an Order-8 Butterworth low-pass filter (LPF) with a cut-off frequency of 3.4 kHz before downsampling to 8 kHz.

**2. Theoretical Basics Applied**
According to the Nyquist-Shannon sampling theorem, when a continuous signal is sampled (or downsampled) at a rate fs, the maximum frequency it can accurately represent without distortion is the Nyquist limit (fs / 2). For our target sampling rate of 8 kHz, this limit is 4 kHz.

If frequencies above 4 kHz are present in the signal during sampling, they will "fold back" (alias) into the baseband (0–4 kHz) and cause irreversible distortion. An anti-aliasing filter is mathematically required to aggressively attenuate all frequency components above the Nyquist limit before the sampling takes place.

**3. Observations and Results**
The results of the decimation process were verified both visually through spectrograms and auditorily through listening tests.

* **Visual Evidence of Aliasing:** In the generated figure ("Aliased Spectrum"), a distinct, bright horizontal line of high intensity is visible at exactly 1.5 kHz. This confirms the mathematical reality of aliasing: the injected 6.5 kHz tone folded back into the audible spectrum because it exceeded the 4 kHz Nyquist limit (8000 Hz - 6500 Hz = 1500 Hz).
* **Visual Evidence of Successful Filtering:** The adjacent "Clean Spectrum" demonstrates the effectiveness of the Order-8 Butterworth LPF at 3.4 kHz. The high-frequency energy was successfully stripped away prior to decimation, resulting in a spectrum that is entirely free of the folded 1.5 kHz artifact.
* **Auditory Results:** Listening to the generated .wav files perfectly mirrors the visual data. The aliased audio track is heavily distorted by a loud, continuous ringing tone (the folded 1.5 kHz artifact) overlapping the voice. By contrast, the correct method successfully cancelled the out-of-band noise, yielding a clean, intelligible speech signal constrained to standard telephone bandwidth.
