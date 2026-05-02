import streamlit as st
from gtts import gTTS
import base64
import time
import os
import random

# 1. ページ設定
st.set_page_config(page_title="これ なーんだ？", layout="wide")

# --- 音声生成・キャッシュ関数 ---
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

# --- 画像をBase64に変換 ---
def get_image_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- 音声入力用のJavaScriptコンポーネント ---
def speech_recognition_js():
    # ブラウザの音声認識を起動するJavaScript
    js_code = """
    <script>
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'ja-JP';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    const startSpeech = () => {
        recognition.start();
    };

    recognition.onresult = (event) => {
        const speechResult = event.results[0][0].transcript;
        // Streamlit側に値を返すための隠しボタンと入力欄
        const input = window.parent.document.querySelector('input[aria-label="speech_input"]');
        if (input) {
            input.value = speechResult;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    };
    </script>
    <button onclick="startSpeech()" style="background-color: #FF4B4B; color: white; border: none; padding: 10px 20px; border-radius: 10px; cursor: pointer; font-size: 18px; width: 100%;">
        🎤 おしたあと、こたえを おしえてね！
    </button>
    """
    st.components.v1.html(js_code, height=60)

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

st.markdown("<h1 style='text-align: center;'>これ なーんだ？</h1>", unsafe_allow_html=True)

if "shuffled_data" not in st.session_state:
    data = original_quiz_data.copy()
    random.shuffle(data)
    st.session_state.shuffled_data = data
    st.session_state.quiz_index = 0
    st.session_state.playing = False
    st.session_state.auto_start = False

current_quiz = st.session_state.shuffled_data[st.session_state.quiz_index]

col1, col2, col3 = st.columns([1, 10, 1])

with col2:
    st.write(f"### 第 {st.session_state.quiz_index + 1} 問 / 全 {len(original_quiz_data)} 問")

    if os.path.exists(current_quiz["file"]):
        img_base64 = get_image_base64(current_quiz["file"])
        
        # クイズ開始
        if st.button("クイズをスタート！", use_container_width=True) or st.session_state.auto_start:
            st.session_state.playing = True
            st.session_state.auto_start = False
            play_audio("これなーんだ？")
            
            placeholder = st.empty()
            blur_css = f"""
            <style>
            @keyframes reveal {{ from {{ filter: blur(60px); }} to {{ filter: blur(0px); }} }}
            .blur-image {{ width: 100%; height: 500px; object-fit: cover; border-radius: 25px; animation: reveal 10s linear forwards; }}
            </style>
            <img src="data:image/jpeg;base64,{img_base64}" class="blur-image">
            """
            placeholder.markdown(blur_css, unsafe_allow_html=True)
            time.sleep(10)

        # 出題中（回答待ち）の表示
        if st.session_state.playing:
            st.divider()
            st.write("### 🎤 こたえを いってね！")
            
            # 音声入力の結果を受け取るための隠し入力欄
            speech_val = st.text_input("speech_input", label_visibility="collapsed", key="speech_input_widget", placeholder="ここに おしゃべりした 文字が でるよ")

            # マイクボタンの表示
            speech_recognition_js()

            if speech_val:
                st.write(f"きみの こたえ: **{speech_val}**")
                
                # 正解判定（ひらがな・カタカナの揺れを考慮する場合はもっと複雑にできますが、まずはシンプルに一致判定）
                if speech_val in current_quiz["answer"]:
                    st.success("✨ すごい！ せいかい！！ ✨")
                    play_audio(f"せいかい！ {current_quiz['answer']} ですね！")
                else:
                    st.warning("おしい！ もういっかい いってみる？")

            st.divider()
            if st.session_state.quiz_index < len(st.session_state.shuffled_data) - 1:
                if st.button("つぎへ", use_container_width=True):
                    st.session_state.quiz_index += 1
                    st.session_state.playing = False
                    st.session_state.auto_start = True
                    st.rerun()
            else:
                if st.button("最初からあそぶ", use_container_width=True):
                    random.shuffle(st.session_state.shuffled_data)
                    st.session_state.quiz_index = 0
                    st.session_state.playing = False
                    st.session_state.auto_start = True
                    st.rerun()
    else:
        st.error(f"画像が見つかりません: {current_quiz['file']}")
