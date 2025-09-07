# Vocalite — Multilingual Translator

Vocalite is a Streamlit-powered, all-in-one multilingual assistant that blends translation, speech-to-text, text-to-speech, OCR, and grammar correction into a single, elegant app.

[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b?logo=streamlit&logoColor=white)](https://streamlit.io) [![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![License](https://img.shields.io/badge/License-MIT-2ea44f)](LICENSE)

---

## ✨ Features
- **Instant translation**: Powered by `googletrans` with support for many languages
- **Speech recognition**: Convert voice to text (uses your microphone)
- **OCR from images**: Extract text from photos or uploads using Tesseract
- **Smart cropping**: Crop images before OCR for better accuracy (`streamlit-cropper`)
- **Text-to-speech**: Hear results using `gTTS`
- **Grammar correction**: Improve input with `language_tool_python`
- **History & Auto-play**: Keep recent translations and auto-play audio
- **Themes**: Switch between multiple elegant themes

---

## 📦 Prerequisites
- Python 3.9+
- Internet connection (for translation, grammar, and TTS)
- Optional hardware: microphone (speech), camera (camera input)
- Tesseract OCR installed locally (for OCR)
  - Windows: download the installer from `https://github.com/tesseract-ocr/tesseract` (Releases)
  - macOS: `brew install tesseract`
  - Linux: `sudo apt install tesseract-ocr`

After installing Tesseract, if it’s not in your system PATH, set the executable path in the app:
```python
# In app (1).py
# pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```
Uncomment and adjust the path if needed.

Note (Windows microphone): You may need `PyAudio` for microphone input.
- Try: `pip install pyaudio` (or use prebuilt wheels if needed).

---

## 🚀 Quick Start
1) Clone the repo
```bash
git clone https://github.com/<selmatuscano>/Vocalite--Multilingual-Translator.git
cd Vocalite--Multilingual-Translator
```

2) Create a virtual environment (recommended)
```bash
python -m venv .venv
# Windows PowerShell
. .venv\\Scripts\\Activate.ps1
# macOS/Linux
# source .venv/bin/activate
```

3) Install dependencies (pinned via requirements.txt)
```bash
pip install --upgrade pip
pip install -r requirements.txt
# Optional for microphone input on some systems:
# pip install pyaudio
```

4) Run the app
```bash
streamlit run "app.py"
```

---

## 🧭 How to Use
- Select the source and target languages
- Choose input method: `Type`, `Speak`, `Camera`, or `Upload Image`
- Type text, speak into the mic, or provide an image and optionally crop it
- Click `Translate` to view and hear the result
- Click `Clear` to save the current translation into history
- Toggle features in the sidebar: Auto-play audio, Grammar correction, Theme

---

## 🔧 Troubleshooting
- "OCR Error" or no text extracted:
  - Ensure Tesseract is installed and accessible in PATH
  - Or set `pytesseract.pytesseract.tesseract_cmd` to the correct path
- Microphone not working:
  - Install `pyaudio` and check input device permissions
- gTTS playback issues:
  - Ensure you have internet access; try disabling auto-play in sidebar
- Grammar tool errors:
  - Check your internet connection; language tool initialization can fail offline

---

## 🗂 Tech Stack
- UI: `Streamlit`
- Translation: `googletrans`
- Speech-to-Text: `SpeechRecognition` (Google recognizer)
- OCR: `pytesseract` + `Tesseract`
- Text-to-Speech: `gTTS`
- Grammar: `language_tool_python`
- Image: `Pillow`, `streamlit-cropper`
