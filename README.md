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
