import streamlit as st
from gtts import gTTS
import base64
import time
import os
import random

# 1. ページ設定
st.set_page_config(page_title="これ なーんだ？", layout="wide")

# --- 便利関数（音声・画像・JavaScript） ---
@st.cache_data
def get_audio_base64(text):
    tts = gTTS(text=text, lang='ja')
    tts.save("temp.mp3")
    with open("temp.mp3", "rb") as f:
        audio_bytes = f.read()
    return base64.b64encode(audio_bytes).decode()

def play_audio(text):
    audio_base64 = get_audio_base64(text)
    audio_html = f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay style="display:none;">'
    st.components.v1.html(audio_html, height=0)

def get_image_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def speech_recognition_js():
    js_code = """
    <script>
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'ja-JP';
    recognition.onresult = (event) => {
        const speechResult = event.results[0][0].transcript;
        const input = window.parent.document.querySelector('input[aria-label="speech_input"]');
        if (input) {
            input.value = speechResult;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    };
    const startSpeech = () => { recognition.start(); };
    </script>
    <button onclick="startSpeech()" style="background-color: #FF4B4B; color: white; border: none; padding: 12px; border-radius: 10px; width: 100%; font-size: 18px;">
        🎤 こたえを おしえてね！（おしてから おしゃべり）
    </button>
    """
    st.components.v1.html(js_code, height=70)

# --- クイズデータ ---
original_quiz_data = [
    {"answer": "りんご", "file": "wide_thumbnail_large.jpg"},
    {"answer": "ばなな", "file": "banana.jpg"},
    {"answer": "もも", "file": "momo.jpg"},
    {"answer": "きうい", "file": "kiwi.jpg"},
    {"answer": "ぶどう", "file": "budo.jpg"},
    {"answer": "いちご", "file": "ichigo.jpg"},
    {"answer": "あざらし", "file": "azarashi.jpg"},
    {"answer": "めろん", "file": "melon.jpg"},
    {"answer": "ぱんだ", "file": "panda.jpg"},
    {"answer": "れもん", "file": "lemon.jpg"},
    {"answer": "すいか", "file": "suika.jpg"},
    {"answer": "うさぎ", "file": "usagi.jpg"},
    {"answer": "はりねずみ", "file": "harinezumi.jpg"},
    {"answer": "しまえなが", "file": "shimaenaga.jpg"},
]

# --- セッション管理 ---
if "shuffled_data" not in st.session_state:
    data = original_quiz_data.copy()
    random.shuffle(data)
    st.session_state.shuffled_data = data
    st.session_state.quiz_index = 0
    st.session_state.status = "waiting" # waiting, playing, stop

# --- 画面レイアウト ---
st.markdown("<h1 style='text-align: center; font-size: 60px;'>これ なーんだ？</h1>", unsafe_allow_html=True)

# 上部ボタンエリア
btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    if st.button("▶ スタート", use_container_width=True):
        st.session_state.status = "playing"
        st.rerun()

with btn_col2:
    if st.button("💡 わかった！", use_container_width=True):
        if st.session_state.status == "playing":
            st.session_state.status = "stop"
            st.rerun()

with btn_col3:
    if st.button("👉 つぎへ", use_container_width=True):
        if st.session_state.quiz_index < len(st.session_state.shuffled_data) - 1:
            st.session_state.quiz_index += 1
            st.session_state.status = "playing"
            st.rerun()
        else:
            st.warning("おわりだよ！「最初から」ボタンが出るまで待ってね。")

st.divider()

# --- メインコンテンツ ---
current_quiz = st.session_state.shuffled_data[st.session_state.quiz_index]
col_main = st.columns([1, 8, 1])[1]

with col_main:
    st.write(f"### 第 {st.session_state.quiz_index + 1} 問")

    if os.path.exists(current_quiz["file"]):
        img_base64 = get_image_base64(current_quiz["file"])
        
        # 状態に応じた画像表示
        if st.session_state.status == "playing":
            play_audio("これなーんだ？")
            placeholder = st.empty()
            blur_css = f"""
            <style>
            @keyframes reveal {{ from {{ filter: blur(50px); }} to {{ filter: blur(0px); }} }}
            .blur-image {{ width: 100%; height: 500px; object-fit: cover; border-radius: 25px; animation: reveal 10s linear forwards; }}
            </style>
            <img src="data:image/jpeg;base64,{img_base64}" class="blur-image">
            """
            placeholder.markdown(blur_css, unsafe_allow_html=True)
            # 10秒経ったら自動でstop状態へ
            time.sleep(10)
            st.session_state.status = "stop"
            st.rerun()

        elif st.session_state.status == "stop":
            # ぼかしなしの画像を表示
            st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" style="width:100%; height:500px; object-fit:cover; border-radius:25px;">', unsafe_allow_html=True)
            
            st.divider()
            st.write("### 🎤 こたえを いってね！")
            speech_val = st.text_input("speech_input", label_visibility="collapsed", key="speech_input_widget")
            speech_recognition_js()

            if speech_val:
                st.write(f"きみの こたえ: **{speech_val}**")
                if speech_val in current_quiz["answer"]:
                    st.success("✨ せいかい！！ ✨")
                    play_audio(f"せいかい！ {current_quiz['answer']} ですね！")
                else:
                    st.warning("おしい！ もういっかい いってみる？")
    else:
        st.error("がぞうが ないよ！")

# 全問終了時
if st.session_state.quiz_index == len(st.session_state.shuffled_data) - 1 and st.session_state.status == "stop":
    if st.button("最初からあそぶ"):
        random.shuffle(st.session_state.shuffled_data)
        st.session_state.quiz_index = 0
        st.session_state.status = "waiting"
        st.rerun()
