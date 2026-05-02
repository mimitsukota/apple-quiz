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
            # 押した瞬間の経過時間を保存
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
col_main = st.columns([1, 8, 1])[1]

with col_main:
    st.write(f"### 第 {st.session_state.quiz_index + 1} 問")

    if os.path.exists(current_quiz["file"]):
        img_base64 = get_image_base64(current_quiz["file"])
        
        # --- クイズ進行中 ---
        if st.session_state.status == "playing":
            play_audio("これなーんだ？")
            placeholder = st.empty()
            # 10秒かけて blur(50px) から blur(0px) になる設定
            blur_css = f"""
            <style>
            @keyframes reveal {{ from {{ filter: blur(50px); }} to {{ filter: blur(0px); }} }}
            .blur-image {{ width: 100%; height: 500px; object-fit: cover; border-radius: 30px; animation: reveal 10s linear forwards; border: 5px solid #FF4B4B; }}
            </style>
            <img src="data:image/jpeg;base64,{img_base64}" class="blur-image">
            """
            placeholder.markdown(blur_css, unsafe_allow_html=True)
            
            # 0.1秒ごとにチェックし、10秒経ったら自動停止
            while st.session_state.status == "playing":
                current_elapsed = time.time() - st.session_state.start_time
                if current_elapsed >= 10:
                    st.session_state.elapsed = 10
                    st.session_state.status = "stop"
                    st.rerun()
                time.sleep(0.1)

        # --- 停止状態（回答待ち） ---
        elif st.session_state.status == "stop":
            # 経過時間から現在のぼかし量を計算 (50pxから1秒間に5pxずつ減る計算)
            # 10秒以上経っていたら 0px 固定
            calc_blur = max(0, 50 - (st.session_state.elapsed * 5))
            
            st.markdown(f"""
                <img src="data:image/jpeg;base64,{img_base64}" 
                style="width:100%; height:500px; object-fit:cover; border-radius:30px; border: 5px solid #FF4B4B; filter: blur({calc_blur}px);">
                """, unsafe_allow_html=True)
            
            st.divider()
            st.write("### 🎤 こたえを いってね！")
            speech_val = st.text_input("speech_input", label_visibility="collapsed", key="speech_input_widget")
            speech_recognition_js()

            if speech_val:
                st.write(f"きみの こたえ: **{speech_val}**")
                if speech_val in current_quiz["answer"]:
                    # 正解ならぼかしを消して答えを見せる
                    st.markdown('<style>img { filter: blur(0px) !important; transition: filter 0.5s; }</style>', unsafe_allow_html=True)
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
