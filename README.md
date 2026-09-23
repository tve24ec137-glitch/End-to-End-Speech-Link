# End-to-End-Speech-Link
End-to-End Speech LinkCourse Project: Analog & Digital Communication
Team MembersVysakh P Chandran (69)Ujjwal Skandakumar P (68)Rohann Subhash (55)
Project Overview:
This project investigates the cumulative degradation of an analog speech signal as it passes through a complete digital communication pipeline. By capturing an analog voice recording and processing it through anti-aliasing, sampling, quantization, companding, modulation, and a noisy AWGN channel, we analyze where signal quality drops the most. The goal is to determine at what noise levels the audio becomes unintelligible, bridging mathematical bit-error rates with perceived human speech quality.
Stage 0: Acquisition and Analysis
Prerequisites
Ensure you have Python installed along with the required digital signal processing libraries. You can install the dependencies using 
pip:Bashpip install numpy scipy matplotlib
Input Audio Requirements
Place your audio recording in the root directory of this project. Ensure the file matches the following parameters:   
Filename: voice.wav
Format: Uncompressed PCM WAV
Bit Depth: 16-bit
Sampling Rate: 44.1 kHzChannels: Mono (script will auto-convert stereo if necessary)
Duration: 8 to 15 seconds of connected speech
