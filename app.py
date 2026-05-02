import streamlit as st
from gtts import gTTS
import base64
import time
import os

# ページ設定
st.set_page_config(page_title="連想クイズ・コレクション", layout="centered")

# --- 音声生成・キャッシュ関数 ---
@st.cache_data
def get_audio_base64(text):
    # 音声を生成してBase64で返す（一度作ったものは再利用する）
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

# --- クイズデータのリスト ---
quiz_data = [
    {"answer": "りんご", "file": "wide_thumbnail_large.jpg"},
    {"answer": "ばなな", "file": "banana.jpg"},
    {"answer": "もも", "file": "momo.jpg"},
    {"answer": "きうい", "file": "kiui.jpg"},
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

st.title("✨ なにかな？連想クイズ")

if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0
if "playing" not in st.session_state:
    st.session_state.playing = False

current_quiz = quiz_data[st.session_state.quiz_index]
st.subheader(f"第 {st.session_state.quiz_index + 1} 問 / 全 {len(quiz_data)} 問")

if os.path.exists(current_quiz["file"]):
    img_base64 = get_image_base64(current_quiz["file"])
    
    if st.button("クイズをスタート！"):
        st.session_state.playing = True
        # ① 問題音声
        play_audio("これなーんだ？")
        
        # ② 10秒アニメーション
        placeholder = st.empty()
        blur_css = f"""
        <style>
        @keyframes reveal {{ from {{ filter: blur(60px); }} to {{ filter: blur(0px); }} }}
        .blur-image {{ width: 100%; max-width: 600px; border-radius: 20px; animation: reveal 10s linear forwards; }}
        </style>
        <img src="data:image/jpeg;base64,{img_base64}" class="blur-image">
        """
        placeholder.markdown(blur_css, unsafe_allow_html=True)
        
        # ③ 10秒待機
        time.sleep(10)
        
        # ④ 正解
        ans_text = f"正解は、{current_quiz['answer']}です！"
        play_audio(ans_text)
        st.balloons()
        st.success(ans_text)

    # 次へ進むボタン
    if st.session_state.playing:
        if st.session_state.quiz_index < len(quiz_data) - 1:
            if st.button("次の問題へ 👉"):
                st.session_state.quiz_index += 1
                st.session_state.playing = False
                st.rerun()
        else:
            if st.button("最初から遊ぶ"):
                st.session_state.quiz_index = 0
                st.session_state.playing = False
                st.rerun()
else:
    st.error(f"画像 '{current_quiz['file']}' が見つかりません。")
