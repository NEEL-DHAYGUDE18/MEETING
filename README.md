# Meeting Transcriber

## Overview
Meeting Transcriber is an AI-powered transcription and summarization tool designed to convert spoken content into text, extract key discussion points, and identify department-specific tasks. It leverages advanced NLP models to generate concise summaries and provides an option to send task updates via WhatsApp.

We have also provided a test audio file, which the user can download and check the functionality.

## Features
- **Real-time transcription** using Whisper AI.
- **Summarization** powered by BART NLP models.
- **Task extraction** for different departments based on meeting discussions.
- **PDF report generation** for meeting summaries and tasks.
- **Automated WhatsApp notifications** for department-specific task distribution.
- **Supports multiple input modes**: Audio, Video, and Live Recording.

## Technologies Used
- Python
- OpenAI Whisper for speech-to-text transcription
- Hugging Face Transformers (BART) for text summarization
- PyWhatKit for WhatsApp messaging
- Tkinter for GUI
- FPDF for PDF report generation

## Installation & Setup
### Prerequisites:
- Python 3.8+
- Install the required dependencies:
  ```bash
  pip install openai-whisper transformers fpdf pywhatkit tkinter pyaudio wave
  ```


## Usage
1. Launch the Meeting Transcriber App.
2. Enter the meeting name and list of departments attending.
3. Select the mode of audio input (Audio, Video, or Live Recording).
4. Click on "Start Process" to transcribe and summarize the meeting.
5. Generate and save the PDF report.
6. (Optional) Send department-specific tasks via WhatsApp.


## FUTURE DEVLOPMENTS
1. **Integration with Meeting Platforms** – Add APIs to connect with Zoom, Google Meet, or Microsoft Teams for automatic transcription.
2. **Cloud Storage and Sharing** – Enable users to store transcriptions and summaries in Google Drive, Dropbox, or send them via email.

## Team Members
- **Neel Dhaygude** (22BCE1052)
- **Govind** (22BRS1109)
- **Arya** (22BRS1106)
- **Swarna** (22BLC1172)


## Contact
NEEL DHAYGUDE
neel.dhaygude2022@vitstudent.ac.in
