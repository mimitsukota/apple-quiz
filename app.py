import streamlit as st
from gtts import gTTS
import base64
import time
import os
import random
import re

# 1. ページ設定
st.set_page_config(page_title="これ なーんだ？", layout="wide")

# --- 音声・判定の便利関数 ---
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def prepare_audio_files():
    if not os.path.exists("correct.mp3"):
        gTTS(text="ピンポーン！ 正解です！ やったね！", lang='ja').save("correct.mp3")
    if not os.path.exists("wrong.mp3"):
        gTTS(text="残念！ もっかい言ってみて！", lang='ja').save("wrong.mp3")
    if not os.path.exists("intro.mp3"):
        gTTS(text="これなーんだ？", lang='ja').save("intro.mp3")

prepare_audio_files()

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

if "shuffled_data" not in st.session_state:
    data = original_quiz_data.copy()
    random.shuffle(data)
    st.session_state.shuffled_data = data
    st.session_state.quiz_index = 0
    st.session_state.status = "waiting"
    st.session_state.start_time = 0
    st.session_state.elapsed = 0

# --- CSS設定 ---
st.markdown(f"""
<style>
    .image-container {{
        width: 100%; max-width: 800px; height: 500px; margin: 0 auto;
        border: 5px solid #FF4B4B; border-radius: 30px; overflow: hidden;
    }}
    .quiz-img {{ width: 100% !important; height: 100% !important; object-fit: cover !important; }}
    div.stButton > button {{ height: 80px; font-size: 20px !important; font-weight: bold; border-radius: 15px; }}
</style>
<audio id="audio-correct" src="data:audio/mp3;base64,{get_base64('correct.mp3')}"></audio>
<audio id="audio-wrong" src="data:audio/mp3;base64,{get_base64('wrong.mp3')}"></audio>
""", unsafe_allow_html=True)

# --- 画面表示 ---
st.markdown("<h1 style='text-align: center; font-size: 60px; color: #FF4B4B;'>これ なーんだ？</h1>", unsafe_allow_html=True)

current_quiz = st.session_state.shuffled_data[st.session_state.quiz_index]
ans_hira = current_quiz["answer"]

# カタカナへの変換（判定用）
def hira_to_kata(text):
    return "".join([chr(ord(c) + 96) if "ぁ" <= c <= "ん" else c for c in text])
ans_kata = hira_to_kata(ans_hira)

cols = st.columns(5)

with cols[0]:
    if st.button("▶️スタート", use_container_width=True):
        st.session_state.status = "playing"
        st.session_state.start_time = time.time()
        st.rerun()

with cols[1]:
    if st.button("💡わかった", use_container_width=True):
        if st.session_state.status == "playing":
            st.session_state.elapsed = time.time() - st.session_state.start_time
            st.session_state.status = "stop"
            st.rerun()

with cols[2]:
    # 🎤 こたえる
    st.components.v1.html(f"""
    <script>
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'ja-JP';
    recognition.onresult = (e) => {{
        const text = e.results[0][0].transcript;
        const input = window.parent.document.querySelector('input[type="text"]');
        input.value = text;
        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
    }};
    </script>
    <button onclick="recognition.start()" style="width:100%; height:80px; background-color:#f0f2f6; border:1px solid #d3d3d3; border-radius:15px; font-size:20px; font-weight:bold; cursor:pointer;">🎤こたえる</button>
    """, height=85)

with cols[3]:
    # ⭕️ チェック（超・柔軟判定版）
    st.components.v1.html(f"""
    <script>
    function checkAnswer() {{
        const input = window.parent.document.querySelector('input[type="text"]').value;
        const ansHira = "{ans_hira}";
        const ansKata = "{ans_kata}";
        
        // ひらがな、またはカタカナのどちらかが含まれていれば正解！
        if (input.includes(ansHira) || input.includes(ansKata)) {{
            window.parent.document.getElementById('audio-correct').play();
            const img = window.parent.document.querySelector('.quiz-img');
            if(img) img.style.filter = "blur(0px)";
        }} else {{
            window.parent.document.getElementById('audio-wrong').play();
        }}
    }}
    </script>
    <button onclick="checkAnswer()" style="width:100%; height:80px; background-color:#f0f2f6; border:1px solid #d3d3d3; border-radius:15px; font-size:20px; font-weight:bold; cursor:pointer;">⭕️チェック</button>
    """, height=85)

with cols[4]:
    if st.button("👉つぎへ", use_container_width=True):
        if st.session_state.quiz_index < len(st.session_state.shuffled_data) - 1:
            st.session_state.quiz_index += 1
            st.session_state.status = "playing"
            st.session_state.start_time = time.time()
            st.rerun()

st.divider()

if os.path.exists(current_quiz["file"]):
    with open(current_quiz["file"], "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()
    
    if st.session_state.status == "playing":
        current_elapsed = time.time() - st.session_state.start_time
        if current_elapsed >= 10:
            st.session_state.elapsed = 10; st.session_state.status = "stop"; st.rerun()
        calc_blur = max(0, 50 - (current_elapsed * 5))
    elif st.session_state.status == "stop":
        calc_blur = max(0, 50 - (st.session_state.elapsed * 5))
    else:
        calc_blur = 50

    st.markdown(f'<div class="image-container"><img src="data:image/jpeg;base64,{img_base64}" class="quiz-img" style="filter: blur({calc_blur}px);"></div>', unsafe_allow_html=True)
    
    if st.session_state.status == "playing":
        st.components.v1.html(f'<audio autoplay><source src="data:audio/mp3;base64,{get_base64("intro.mp3")}" type="audio/mp3"></audio>', height=0)
        time.sleep(0.1); st.rerun()

    if st.session_state.status == "stop":
        st.write(f"### 第 {st.session_state.quiz_index + 1} 問")
        st.text_input("こたえを入力", key="speech_input", placeholder="マイクでおしゃべりしてね")
