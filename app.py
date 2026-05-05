import streamlit as st
from gtts import gTTS
import base64
import time
import os
import random
import re

# 1. ページ設定
st.set_page_config(page_title="これ なーんだ？", layout="wide")

# --- 便利関数 ---
def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def prepare_audio_files():
    if not os.path.exists("correct.mp3"):
        gTTS(text="ピンポーン！ せいかいです！ やったね！", lang='ja').save("correct.mp3")
    if not os.path.exists("wrong.mp3"):
        gTTS(text="ざんねん！ もっかい いってみて！", lang='ja').save("wrong.mp3")
    if not os.path.exists("intro.mp3"):
        gTTS(text="これ なーんだ？", lang='ja').save("intro.mp3")

prepare_audio_files()

# --- クイズデータ ---
original_quiz_data = [
    
    {"answer": "ばす", "file": "bus.jpg"},
    {"answer": "ちかてつ", "file": "cikatetsu.jpg"},
    
    {"answer": "へりこぷたー", "file": "heri.jpg"},
    {"answer": "かぴばら", "file": "kapibara.jpg"},
    {"answer": "きりん", "file": "kirin.jpg"},
    {"answer": "らま", "file": "rama.jpg"},
    {"answer": "れっさーぱんだ", "file": "ressapanda.jpg"},
    {"answer": "ろけっと", "file": "roketto.jpg"},
    {"answer": "あざらし", "file": "azarashi.jpg"},
    {"answer": "ばなな", "file": "banana.jpg"},
    {"answer": "ぶどう", "file": "budou.jpg"},
    {"answer": "はりねずみ", "file": "harinezumi.jpg"},
    {"answer": "いちご", "file": "ichigo.jpg"},
    {"answer": "きうい", "file": "kiui.jpg"},
    {"answer": "めろん", "file": "meron.jpg"},
    {"answer": "みかん", "file": "mikan.jpg"},
    
    {"answer": "ぱんだ", "file": "panda.jpg"},
    {"answer": "れもん", "file": "remon.jpg"},
    {"answer": "しまえなが", "file": "simaenaga.jpg"},
    {"answer": "りんご", "file": "ringo.jpg"},
    {"answer": "すいか", "file": "suika.jpg"},
    {"answer": "うさぎ", "file": "usagi.jpg"},
    {"answer": "ふぇれっと", "file": "feretto.jpg"},
    
    {"answer": "みつき", "file": "mitsuki.jpg"},
    
    {"answer": "ぱぱ", "file": "papa.jpg"},
    {"answer": "とうご", "file": "pengintogo.jpg"},
    
    {"answer": "すらっくすさん", "file": "surakkusu.jpg"},
    
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
    .main {{ background-color: #FFF5F5; }}
    .image-container {{
        width: 100%; max-width: 500px; height: 350px; margin: 10px auto;
        border: 8px solid #FF4B4B; border-radius: 20px; overflow: hidden;
        cursor: pointer;
    }}
    .quiz-img {{ width: 100% !important; height: 100% !important; object-fit: cover !important; }}
    div.stButton > button {{
        width: 100% !important; height: 70px !important; 
        font-size: 24px !important; font-weight: bold !important;
        border-radius: 15px !important; margin-bottom: 5px !important;
    }}
    div.stButton > button[kind="primary"] {{ background-color: #FF4B4B; color: white; }}
    .st-emotion-cache-zt5igj {{ display: none; }} 
</style>
<audio id="audio-correct" src="data:audio/mp3;base64,{get_base64('correct.mp3')}"></audio>
<audio id="audio-wrong" src="data:audio/mp3;base64,{get_base64('wrong.mp3')}"></audio>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; font-size: 40px; color: #FF4B4B; margin-bottom: 0;'>これ なーんだ？</h1>", unsafe_allow_html=True)

current_quiz = st.session_state.shuffled_data[st.session_state.quiz_index]
ans = current_quiz["answer"]

if st.button("▶️ はじめる！", type="primary", use_container_width=True):
    st.session_state.status = "playing"
    st.session_state.start_time = time.time()
    st.rerun()

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

    st.markdown(f"""
        <div class="image-container" onclick="Array.from(window.parent.document.querySelectorAll('button')).find(el => el.innerText.includes('stop_btn')).click();">
            <img src="data:image/jpeg;base64,{img_base64}" class="quiz-img" style="filter: blur({calc_blur}px);">
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("stop_btn", key="stop_hidden_button"):
        if st.session_state.status == "playing":
            st.session_state.elapsed = time.time() - st.session_state.start_time
            st.session_state.status = "stop"
            st.rerun()

    if st.session_state.status == "playing":
        st.components.v1.html(f'<audio autoplay><source src="data:audio/mp3;base64,{get_base64("intro.mp3")}" type="audio/mp3"></audio>', height=0)
        time.sleep(0.1); st.rerun()

if st.session_state.status == "stop":
    st.markdown("<p style='text-align:center; font-weight:bold; font-size:20px;'>わかったかな？</p>", unsafe_allow_html=True)
    
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
    <button onclick="recognition.start()" style="width:100%; height:70px; background-color:#4CAF50; color:white; border:none; border-radius:15px; font-size:24px; font-weight:bold; cursor:pointer;">🎤 おしゃべりして こたえる</button>
    """, height=80)

    st.text_input("こたえ", key="speech_input", label_visibility="collapsed")

    # ★最強の「おまけ」判定ロジック★
    st.components.v1.html(f"""
    <script>
    function checkAnswer() {{
        const inputRaw = window.parent.document.querySelector('input[type="text"]').value;
        const answer = "{ans}";
        
        // カタカナをひらがなに変換する関数
        const toHira = (str) => str.replace(/[ァ-ン]/g, s => String.fromCharCode(s.charCodeAt(0) - 0x60));
        
        // 判定用のクリーニング（ひらがな化、空白削除、。の削除、伸ばし棒の統一）
        const clean = (str) => toHira(str).trim().replace(/[ 　。、]/g, "").replace(/[ー－―ー]/g, "ー");
        
        const cleanInput = clean(inputRaw);
        const cleanAnswer = clean(answer);

        // 部分一致を許可（「ひこうき」に対して「ひこうきだよ」でもOKにする）
        if (cleanInput.includes(cleanAnswer) || cleanAnswer.includes(cleanInput)) {{
            window.parent.document.getElementById('audio-correct').play();
            const img = window.parent.document.querySelector('.quiz-img');
            if(img) img.style.filter = "blur(0px)";
        }} else {{
            window.parent.document.getElementById('audio-wrong').play();
        }}
    }}
    </script>
    <button onclick="checkAnswer()" style="width:100%; height:70px; background-color:#FF9800; color:white; border:none; border-radius:15px; font-size:24px; font-weight:bold; cursor:pointer;">⭕ せいかいチェック！</button>
    """, height=80)

st.write("") 
if st.button("👉 つぎの問題へ", use_container_width=True):
    if st.session_state.quiz_index < len(st.session_state.shuffled_data) - 1:
        st.session_state.quiz_index += 1
        st.session_state.status = "playing"
        st.session_state.start_time = time.time()
        st.rerun()
    else:
        st.balloons()
        st.success("ぜんぶ おわったよ！ すごいね！")
