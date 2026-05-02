import streamlit as st
from gtts import gTTS
import base64
import time
import os

# ページ設定
st.set_page_config(page_title="最強ぼかしりんごクイズ", layout="centered")

# --- 音声生成・取得関数 ---
def get_audio_html(text, filename):
    if not os.path.exists(filename):
        tts = gTTS(text=text, lang='ja')
        tts.save(filename)
    
    with open(filename, "rb") as f:
        audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    # 自動再生のためのHTML（隠しプレイヤー）
    return f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay>'

# --- 画像をBase64に変換 ---
def get_image_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

st.title("🍎 超・難問クイズ")
st.write("ボタンを押すと、超強力なぼかし画像が現れます。何かわかるかな？")

img_path = "wide_thumbnail_large.jpg"

if os.path.exists(img_path):
    img_base64 = get_image_base64(img_path)
    
    if st.button("クイズを始める！"):
        # ① 問題音声「これなーんだ」を流す
        st.components.v1.html(get_audio_html("これなーんだ？", "q.mp3"), height=0)
        
        # ② 10秒かけてボカシを消すアニメーション
        placeholder = st.empty()
        
        # === 【修正点】from { filter: blur(20px); } を (60px) に強化しました ===
        blur_css = f"""
        <style>
        @keyframes reveal {{
            from {{ filter: blur(60px); }}
            to {{ filter: blur(0px); }}
        }}
        .blur-image {{
            width: 100%;
            border-radius: 15px;
            animation: reveal 10s linear forwards;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); /* 少し見栄えを良く */
        }}
        </style>
        <img src="data:image/jpeg;base64,{img_base64}" class="blur-image">
        """
        placeholder.markdown(blur_css, unsafe_allow_html=True)
        
        # ③ 10秒待機
        time.sleep(10)
        
        # 正解音声「せいかいはりんごです」
        st.components.v1.html(get_audio_html("せいかいは、りんごです", "a.mp3"), height=0)
        st.balloons()
        st.success("正解はりんごです！")
else:
    st.error(f"画像 '{img_path}' が見つかりません。GitHubに画像をアップロードしてください。")
