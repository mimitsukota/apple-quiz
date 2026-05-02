import streamlit as st
from gtts import gTTS
import base64
import time
import os
import random

# 1. ページ設定
st.set_page_config(page_title="これ なーんだ？", layout="wide")

# --- 便利関数 ---
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
    <div style="display: flex; justify-content: center;">
        <button onclick="startSpeech()" style="background-color: #FF4B4B; color: white; border: none; padding: 15px; border-radius: 15px; width: 80%; font-size: 20px; font-weight: bold; cursor: pointer;">
            🎤 おして、こたえを おしえてね！
        </button>
    </div>
    """
    st.components.v1.html(js_code, height=100)

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
    st.session_state.status = "waiting"
    st.session_state.start_time = 0
    st.session_state.elapsed = 0

# --- 全体共通のCSS（ここでサイズを強制固定） ---
st.markdown("""
<style>
    /* 画像を囲う額縁のサイズを完全に固定 */
    .image-container {
        width: 100%;
        max-width: 800px; /* パソコンで見ても大きくなりすぎないように */
        height: 500px;
        margin: 0 auto;
        border: 5px solid #FF4B4B;
        border-radius: 30px;
        overflow: hidden;
        position: relative;
    }
    /* 画像そのものの設定 */
    .quiz-img {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
        display: block;
    }
    /* ボタンの高さ揃え */
    div.stButton > button { height: 60px; font-size: 20px !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 画面表示 ---
st.markdown("<h1 style='text-align: center; font-size: 70px; color: #FF4B4B;'>これ なーんだ？</h1>", unsafe_allow_html=True)

btn_col1, btn_col2, btn_col3 = st.columns(3)
with btn_col1:
    if st.button("▶ スタート", use_container_width=True):
        st.session_state.status = "playing"
        st.session_state.start_time = time.time()
        st.rerun()
with btn_col2:
    if st.button("💡 わかった！", use_container_width=True):
        if st.session_state.status == "playing":
            st.session_state.elapsed = time.time() - st.session_state.start_time
            st.session_state.status = "stop"
            st.rerun()
with btn_col3:
    if st.button("👉 つぎへ", use_container_width=True):
        if st.session_state.quiz_index < len(st.session_state.shuffled_data) - 1:
            st.session_state.quiz_index += 1
            st.session_state.status = "playing"
            st.session_state.start_time = time.time()
            st.rerun()

st.divider()

current_quiz = st.session_state.shuffled_data[st.session_state.quiz_index]

# メイン表示エリア
if os.path.exists(current_quiz["file"]):
    img_base64 = get_image_base64(current_quiz["file"])
    
    # ぼかしの計算
    if st.session_state.status == "playing":
        current_elapsed = time.time() - st.session_state.start_time
        if current_elapsed >= 10:
            st.session_state.elapsed = 10
            st.session_state.status = "stop"
            st.rerun()
        calc_blur = max(0, 50 - (current_elapsed * 5))
    elif st.session_state.status == "stop":
        calc_blur = max(0, 50 - (st.session_state.elapsed * 5))
    else:
        calc_blur = 50

    # 【重要】playingでもstopでも全く同じHTML構造を使う
    st.markdown(f"""
        <div class="image-container">
            <img src="data:image/jpeg;base64,{img_base64}" class="quiz-img" style="filter: blur({calc_blur}px);">
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.status == "playing":
        play_audio("これなーんだ？")
        time.sleep(0.1)
        st.rerun()

    if st.session_state.status == "stop":
        st.divider()
        st.write(f"### 第 {st.session_state.quiz_index + 1} 問： 🎤 こたえを いってね！")
        speech_val = st.text_input("speech_input", label_visibility="collapsed", key="speech_input_widget")
        speech_recognition_js()

        if speech_val:
            st.write(f"きみの こたえ: **{speech_val}**")
            if speech_val in current_quiz["answer"]:
                # 正解なら額縁の中の画像だけぼかしを消す
                st.markdown('<style>.quiz-img { filter: blur(0px) !important; transition: filter 0.5s !important; }</style>', unsafe_allow_html=True)
                st.success("## ✨ せいかい！！ ✨")
                play_audio("ピンポーン！ 正解です。やったね！")
            else:
                st.warning("## おしい！")
                play_audio("残念！")
else:
    st.error("がぞうが ないよ！")

# 全問終了
if st.session_state.quiz_index == len(st.session_state.shuffled_data) - 1 and st.session_state.status == "stop":
    if st.button("最初からあそぶ", use_container_width=True):
        random.shuffle(st.session_state.shuffled_data)
        st.session_state.quiz_index = 0
        st.session_state.status = "waiting"
        st.rerun()
