import streamlit as st
from googletrans import Translator, LANGUAGES
from gtts import gTTS
import speech_recognition as sr
import pytesseract
from PIL import Image
import os
import time
import base64
import datetime
import language_tool_python  # For grammar checking
from streamlit_cropper import st_cropper  # For cropping images


# Initialize translator and grammar tool
translator = Translator()

@st.cache_resource
def init_grammar_tool():
    """Initializes the grammar checking tool and caches it."""
    try:
        return language_tool_python.LanguageTool('en-US')
    except Exception as e:
        st.error(f"Error initializing grammar tool: {e}. Please check your internet connection and try again.")
        return None

tool = init_grammar_tool()

def get_lang_code(lang_name):
    """Gets the language code from the language name."""
    for code, name in LANGUAGES.items():
        if name.lower() == lang_name.lower():
            return code
    return 'en'

# Language tool mapping for grammar correction
LANG_TOOL_MAPPING = {
    'english': 'en-US',
    'german': 'de-DE',
    'french': 'fr-FR',
    'spanish': 'es-ES',
    'portuguese': 'pt-PT',
    'italian': 'it-IT',
    'dutch': 'nl-NL',
    'polish': 'pl-PL',
    'russian': 'ru-RU',
    'arabic': 'ar',
    'chinese': 'zh-CN',
    'japanese': 'ja-JP',
}

def correct_grammar(text, lang_name):
    """Corrects grammar for the given text using LanguageTool."""
    if not text or not text.strip() or not tool:
        return text
    
    lang_code = LANG_TOOL_MAPPING.get(lang_name.lower(), 'en-US')
    
    try:
        # Check if the tool's language needs to be changed
        if tool._language != lang_code:
            try:
                # Create a local instance for a different language to avoid a cached mix-up
                local_tool = language_tool_python.LanguageTool(lang_code)
                corrected = local_tool.correct(text)
                local_tool.close()
                return corrected
            except:
                # Fallback to the default English tool if the specific language tool fails
                return tool.correct(text)
        else:
            return tool.correct(text)
    except Exception as e:
        st.error(f"Grammar correction failed: {str(e)}")
        return text

# ---- Session State Initialization ----
if "spoken_text" not in st.session_state:
    st.session_state.spoken_text = ""
if "corrected_text" not in st.session_state:
    st.session_state.corrected_text = ""
if "show_popup" not in st.session_state:
    st.session_state.show_popup = True
if "history" not in st.session_state:
    st.session_state.history = []
if "show_grammar_correction" not in st.session_state:
    st.session_state.show_grammar_correction = False
if "last_src" not in st.session_state:
    st.session_state.last_src = "english"
if "last_dest" not in st.session_state:
    st.session_state.last_dest = "spanish"
if "last_translated" not in st.session_state:
    st.session_state.last_translated = ""
if "cropped_image" not in st.session_state:
    st.session_state.cropped_image = None
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False
if "input_method" not in st.session_state:
    st.session_state.input_method = "Type"
if "camera_photo_key" not in st.session_state:
    st.session_state.camera_photo_key = 0
if "uploaded_file_key" not in st.session_state:
    st.session_state.uploaded_file_key = 0
    
# Theme initialization
if "theme" not in st.session_state:
    st.session_state.theme = "Ocean"
# Theme colors
theme_colors = {
    "Ocean": {"bg": "#0A1929", "text": "#E0E0E0", "primary": "#00B4D8", "border_color": "#1E3A5F", "input_text_color": "#E0E0E0"},
    "Lavender": {"bg": "#d1d1f6", "text": "#483D8B", "primary": "#9370DB", "border_color": "#A9A9D9", "input_text_color": "#483D8B"},
    "Minty": {"bg": "#ccf2f2", "text": "#004D40", "primary": "#00897B", "border_color": "#80CBC4", "input_text_color": "#004D40"},
    "Grape": {"bg": "#ebd3ee", "text": "#4A148C", "primary": "#673AB7", "border_color": "#B39DDB", "input_text_color": "#4A148C"},
    "Pink": {"bg": "#f9cddc", "text": "#AD1457", "primary": "#FF4081", "border_color": "#F48FB1", "input_text_color": "#AD1457"},
}

# ----------------- FUNCTIONS -----------------
def save_to_history():
    """Saves the last successful translation to the history list."""
    input_text = st.session_state.spoken_text.strip()
    corrected_text = st.session_state.corrected_text.strip() if st.session_state.corrected_text else ""

    if input_text and st.session_state.last_translated:
        history_item = {
            "original": input_text,
            "src_lang": st.session_state.last_src,
            "translated": st.session_state.last_translated,
            "dest_lang": st.session_state.last_dest,
            "time": datetime.datetime.now().strftime("%H:%M:%S")
        }
        # Only add corrected field if grammar correction was applied
        if corrected_text and corrected_text != input_text:
            history_item["corrected"] = corrected_text

        st.session_state.history.append(history_item)
        if len(st.session_state.history) > 10:
            st.session_state.history.pop(0)
            
def clear_inputs():
    """Clears the input text and related session states."""
    save_to_history()
    st.session_state.spoken_text = ""
    st.session_state.corrected_text = ""
    st.session_state.show_grammar_correction = False
    if "typed_text" in st.session_state:
        st.session_state.typed_text = ""
    st.session_state.cropped_image = None
    # Reset the keys of the camera and file uploader widgets
    st.session_state.camera_photo_key += 1
    st.session_state.uploaded_file_key += 1
    # Rerun the script to apply the changes
    st.rerun()
# ----------------- END FUNCTIONS -----------------

# ----------------- Splash Screen -----------------
if st.session_state.show_popup:
    st.markdown(
        """
        <style>
        @keyframes fadeIn {
            0% {opacity: 0;}
            100% {opacity: 1;}
        }
        @keyframes pulse {
            0% {transform: scale(1);}
            50% {transform: scale(1.05);}
            100% {transform: scale(1);}
        }
        .splash-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: fixed; /* Crucial for full-screen */
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(135deg, #0a0f29, #1b2a49, #283e6c);
            color: #e6f0ff;
            text-align: center;
            font-family: 'Segoe UI', sans-serif;
            animation: fadeIn 2s ease-in-out;
            z-index: 9999; /* Ensure it's on top */
        }
        .splash-title {
            font-size: 72px;
            font-weight: bold;
            margin-bottom: 10px;
            animation: fadeIn 2s ease-in-out;
            color: #4dabf7;
            text-shadow: 0px 0px 15px rgba(77,171,247,0.6);
        }
        .splash-subtitle {
            font-size: 26px;
            margin-bottom: 20px;
            opacity: 0.9;
            color: #a5baff;
        }
        .splash-footer {
            margin-top: 30px;
            font-size: 16px;
            opacity: 0.7;
            color: #89a1d6;
        }
        </style>

        <div class="splash-container">
            <div class="splash-title">Vocalite</div>
            <div class="splash-subtitle">Seamless Multilingual Translator</div>
            <div style="font-size:20px; margin-top:15px; color:#cfd9f7;">
                ⚡ Translate • 🎙 Speak • 📷 OCR • 🔊 Listen
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    time.sleep(2.5)
    st.session_state.show_popup = False
    st.rerun()



# Apply selected theme
selected_theme = theme_colors.get(st.session_state.theme, theme_colors["Ocean"])

st.markdown(f"""
<style>
.stApp {{
    background-color: {selected_theme['bg']};
    color: {selected_theme['text']};
}}
.stSidebar {{
    background-color: {selected_theme['bg']};
    color: {selected_theme['text']};
}}
h1, h2, h3, h4, h5, h6 {{
    color: {selected_theme['primary']};
}}
div.stTextInput > div > div > input,
div.stTextArea > div > textarea {{
    border: 2px solid {selected_theme['border_color']};
    border-radius: 8px;
    background-color: transparent !important;
    color: {selected_theme['input_text_color']} !important;
}}
div.stTextInput > div > div > input:focus,
div.stTextArea > div > textarea:focus {{
    border: 2px solid {selected_theme['primary']};
}}
.stButton>button {{
    background-color: {selected_theme['primary']};
    color: white;
    border: 2px solid {selected_theme['primary']};
    border-radius: 8px;
}}
.stButton>button:hover {{
    background-color: {selected_theme['text']};
    color: {selected_theme['primary']};
    border-color: {selected_theme['primary']};
}}
.method-btn {{
    border-color: {selected_theme['primary']} !important;
}}
.method-selected {{
    background-color: {selected_theme['primary']} !important;
}}
.how-to-use-box {{
    border-left: 5px solid {selected_theme['primary']};
    padding: 10px;
    margin-bottom: 10px;
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 5px;
}}
.no-history-box {{
    background-color: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid {selected_theme['primary']};
    color: {selected_theme['input_text_color']};
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    font-size: 14px;
    margin-top: 10px;
}}
</style>
""", unsafe_allow_html=True)

# ----------------- Sidebar -----------------
# Sidebar "How to Use" as an expander with styled boxes
with st.sidebar.expander("📘 How to Use"):
    st.markdown(
        f"""
        <div class="how-to-use-box">
            1. Select input and output languages
        </div>
        <div class="how-to-use-box">
            2. Choose input method: Type / Speak / Camera / Upload Image
        </div>
        <div class="how-to-use-box">
            3. Enter text, speak, or capture/upload image
        </div>
        <div class="how-to-use-box">
            4. Press Translate to see and hear the result
        </div>
        <div class="how-to-use-box">
            5. Press Clear to save the translation into history
        </div>
        """,
        unsafe_allow_html=True
    )

st.sidebar.markdown("### ⚙ Settings")
auto_play = st.sidebar.checkbox("🔊 Auto-play Audio after Translate", value=True)
grammar_check = st.sidebar.checkbox("✅ Enable Grammar Correction", value=True)

# Theme selection
theme_choice = st.sidebar.selectbox("🎨 Choose Theme", list(theme_colors.keys()), 
                                   index=list(theme_colors.keys()).index(st.session_state.theme), 
                                   key="theme_selector")

if theme_choice != st.session_state.theme:
    st.session_state.theme = theme_choice
    st.rerun()


# ----------------- Sidebar History -----------------
st.sidebar.markdown("### 📜 Translation History")

if st.session_state.history:
    for item in reversed(st.session_state.history):  # latest first
        with st.sidebar.expander(f"{item['src_lang']} → {item['dest_lang']} | {item['time']}"):
            if "corrected" in item:
                st.markdown(f"Corrected ({item['src_lang']}):")
                st.info(item['corrected'])
            else:
                st.markdown(f"Original ({item['src_lang']}):")
                st.info(item['original'])

            st.markdown(f"Translated ({item['dest_lang']}):")
            st.success(item['translated'])

    if st.sidebar.button("🧹 Clear History"):
        st.session_state.history = []
        st.rerun()  
else:
    st.sidebar.markdown(
        f"""
        <div class="no-history-box">
            No translation history yet. Press Clear after translating to save.
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------- App UI -----------------
st.markdown(
    f"""
    <div style="text-align: center; margin-top: 5px; margin-bottom: 15px;">
        <h1 style="font-size: 45px; font-weight: bold; color: {selected_theme['primary']};
                    text-shadow: 1px 1px 8px rgba(0,0,0,0.3);">
            Vocalite
        </h1>
        <p style='text-align: center;'>Translate text, speech, or images instantly!</p>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

st.subheader("🌐 Language Selection")
col1, col_swap, col2 = st.columns([2, 0.3, 2])

with col1:
    input_lang = st.selectbox(
        "From", 
        sorted(list(LANGUAGES.values())), 
        index=sorted(list(LANGUAGES.values())).index(st.session_state.last_src),
        key="input_lang_select",
        help="Select the language of your input text"
    )

with col_swap:
    st.write("")
    st.write("")
    if st.button("🔄", help="Swap languages"):
        temp_lang = st.session_state.last_src
        st.session_state.last_src = st.session_state.last_dest
        st.session_state.last_dest = temp_lang
        st.rerun()

with col2:
    output_lang = st.selectbox(
        "To", 
        sorted(list(LANGUAGES.values())), 
        index=sorted(list(LANGUAGES.values())).index(st.session_state.last_dest), 
        key="output_lang_select",
        help="Select the language you want to translate to"
    )

st.session_state.last_src = input_lang
st.session_state.last_dest = output_lang


# ----------------- CUSTOM UI BUTTONS FOR INPUT METHOD -----------------
st.subheader("📥 Input Method")
st.markdown("Choose Input Method")
cols = st.columns(4)
methods = ["Type", "Speak", "Camera", "Upload Image"]
emojis = ["⌨", "🎤", "📷", "🖼"]

for i, method in enumerate(methods):
    with cols[i]:
        if st.button(f"{emojis[i]} {method}", key=f"method_{method}"):
            st.session_state.input_method = method
            st.rerun()
input_method = st.session_state.input_method

# ---------- INPUT LOGIC ----------
if input_method == "Type":
    st.session_state.spoken_text = st.text_area("💬 Type your message here", key="typed_text", height=150,placeholder="Type or paste text here to translate...")

elif input_method == "Speak":
    if st.button("🎙 Speak Now"):
        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                st.info("🎧 Listening... Speak clearly into your microphone.")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, timeout=5)
                spoken_text = r.recognize_google(audio)
                st.session_state.spoken_text = spoken_text
                st.success(f"✅ You said: {spoken_text}")
        except Exception as e:
            st.error(f"⚠ Error: {str(e)}")

elif input_method == "Camera":
    camera_photo = st.camera_input("📷 Capture a photo with text", key=st.session_state.camera_photo_key)
    if camera_photo:
        image = Image.open(camera_photo)
        st.markdown("✂ Crop the area with text before OCR")
        cropped_img = st_cropper(image, aspect_ratio=None, box_color="#4CAF50")
        st.image(cropped_img, caption="Cropped Image", use_column_width=True)
        if st.button("Extract Text from Cropped Image"):
            with st.spinner("🔍 Extracting text from image..."):
                try:
                    extracted_text = pytesseract.image_to_string(cropped_img).strip()
                    if extracted_text:
                        st.session_state.spoken_text = extracted_text
                        st.success(f"✅ Extracted Text: {st.session_state.spoken_text}")
                    else:
                        st.warning("⚠ No text detected. Try cropping more accurately.")
                except Exception as e:
                    st.error(f"❌ OCR Error: {str(e)}")

elif input_method == "Upload Image":
    uploaded_file = st.file_uploader("📂 Upload an image (JPG, PNG, etc.)", type=["jpg", "jpeg", "png"], key=st.session_state.uploaded_file_key)
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.markdown("✂ Crop the area with text before OCR")
        cropped_img = st_cropper(image, aspect_ratio=None, box_color="#4CAF50")
        st.image(cropped_img, caption="Cropped Image", use_column_width=True)
        if st.button("Extract Text from Cropped Image"):
            with st.spinner("🔍 Extracting text from image..."):
                try:
                    extracted_text = pytesseract.image_to_string(cropped_img).strip()
                    if extracted_text:
                        st.session_state.spoken_text = extracted_text
                        st.success(f"✅ Extracted Text: {st.session_state.spoken_text}")
                    else:
                        st.warning("⚠ No text detected. Try cropping more accurately.")
                except Exception as e:
                    st.error(f"❌ OCR Error: {str(e)}")

# Grammar correction
if st.session_state.spoken_text and grammar_check:
    st.markdown("### ✏ Grammar Correction")
    st.write("Original text:")
    st.info(st.session_state.spoken_text)
    
    if st.button("Check Grammar"):
        with st.spinner("Checking grammar..."):
            st.session_state.corrected_text = correct_grammar(st.session_state.spoken_text, input_lang)
            st.session_state.show_grammar_correction = True
    
    if st.session_state.show_grammar_correction and st.session_state.corrected_text:
        st.write("Corrected text:")
        st.success(st.session_state.corrected_text)
        if st.button("Use Corrected Text"):
            st.session_state.spoken_text = st.session_state.corrected_text
            st.rerun()


# ----------------- BUTTONS -----------------
col_translate, col_clear, _ = st.columns([2, 2, 6])
with col_translate:
    translate_clicked = st.button("🌐 Translate", use_container_width=True)
with col_clear:
    clear_clicked = st.button("🧹 Clear", use_container_width=True, on_click=clear_inputs)

# ----------------- TRANSLATION LOGIC -----------------
if translate_clicked:
    # Save the previous translation to history before starting a new one
    save_to_history()  
    
    input_text = st.session_state.spoken_text.strip()
    if not input_text:
        st.warning("⚠ Please enter, speak, or capture/upload some text first.")
    else:
        src_lang = get_lang_code(input_lang)
        dest_lang = get_lang_code(output_lang)
        
        with st.spinner(f"🌐 Translating from {input_lang} to {output_lang}..."):
            try:
                final_input = st.session_state.corrected_text if (
                    st.session_state.corrected_text and 
                    st.session_state.corrected_text != input_text and
                    grammar_check
                ) else input_text
                
                translation = translator.translate(final_input, src=src_lang, dest=dest_lang)
                st.session_state.last_translated = translation.text

                st.markdown("### 📝 Translation Result")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"##### {input_lang.capitalize()}")
                    st.info(final_input)
                with col2:
                    st.markdown(f"##### {output_lang.capitalize()}")
                    translated_text = translation.text
                    st.success(translated_text)
                    

                st.markdown("### 🔊 Audio Output")
                
                with st.spinner("🔊 Generating audio..."):
                    tts = gTTS(translated_text, lang=dest_lang)
                    audio_file = f"translation_{int(time.time())}.mp3"
                    tts.save(audio_file)
                    audio_bytes = open(audio_file, 'rb').read()
                    b64 = base64.b64encode(audio_bytes).decode()
                    
                    st.audio(audio_bytes, format='audio/mp3')
                    
                    if auto_play:
                        audio_html = f"""
                            <audio autoplay>
                                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                            </audio>
                        """
                        st.markdown(audio_html, unsafe_allow_html=True)
                    os.remove(audio_file)

            except Exception as e:
                st.error(f"❌ Translation failed. Error: {str(e)}")

# Add the "Features Overview" section from the image
st.markdown("---")
st.markdown("#### ✨ Features Overview")

feature_col1, feature_col2, feature_col3 = st.columns(3)

with feature_col1:
    st.markdown(
        """
        <div style="text-align:left; font-size:25px;">🗣</div>
        <h5 style="text-align:left;">Speech Recognition</h5>
        <p style="text-align:left; font-size:17px; color:#888;">
            Convert spoken words to text in multiple languages with high accuracy
        </p>
        """,
        unsafe_allow_html=True
    )

with feature_col2:
    st.markdown(
        """
        <div style="text-align:left; font-size:25px;">📷</div>
        <h5 style="text-align:left;">OCR Technology</h5>
        <p style="text-align:left; font-size:17px; color:#888;">
            Extract text from images using advanced optical character recognition
        </p>
        """,
        unsafe_allow_html=True
    )

with feature_col3:
    st.markdown(
        """
        <div style="text-align:left; font-size:25px;">🔊</div>
        <h5 style="text-align:left;">Text-to-Speech</h5>
        <p style="text-align:left; font-size:17px; color:#888;">
            Listen to your translations with natural sounding voice output
        </p>
        """,
        unsafe_allow_html=True
    )

# Footer
st.markdown("---")
st.markdown(
    """
    <p style="text-align: center; font-size: 15px; color: #555;">
        Made with ❤ using Streamlit, Google Translate, gTTS, and Tesseract OCR
    </p> 
    """,
    unsafe_allow_html=True
)
