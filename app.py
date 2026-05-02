import streamlit as st
from gtts import gTTS
import base64
import time
import os
import random

# 1. ページ設定：ワイドモードにして、タイトルを「これ なーんだ？」に設定
st.set_page_config(page_title="これ なーんだ？", layout="wide")

# --- 音声生成・キャッシュ関数 ---
@st.cache_data
def get_audio_base64(text):
    """音声を生成し、Base64形式でキャッシュする（処理高速化のため）"""
    tts = gTTS(text=text, lang='ja')
    tts.save("temp.mp3")
    with open("temp.mp3", "rb") as f:
        audio_bytes = f.read()
    return base64.b64encode(audio_bytes).decode()

def play_audio(text):
    """指定したテキストを音声としてブラウザで自動再生する"""
    audio_base64 = get_audio_base64(text)
    audio_html = f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay style="display:none;">'
    st.components.v1.html(audio_html, height=0)

# --- 画像をBase64に変換 ---
def get_image_base64(path):
    """ローカルの画像をBase64形式に変換してHTMLで表示可能にする"""
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- クイズデータのリスト ---
# 画像ファイル名と答えのセット
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

# タイトル（表題）の中央表示
st.markdown("<h1 style='text-align: center;'>これ なーんだ？</h1>", unsafe_allow_html=True)

# セッション状態（アプリ内の記憶）の初期化
if "shuffled_data" not in st.session_state:
    # 最初に一度だけリストをランダムに並び替える
    data = original_quiz_data.copy()
    random.shuffle(data)
    st.session_state.shuffled_data = data

if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0
if "playing" not in st.session_state:
    st.session_state.playing = False

# 現在の問題を取得
current_quiz = st.session_state.shuffled_data[st.session_state.quiz_index]

# 画面中央に配置するためのカラム設定
col1, col2, col3 = st.columns([1, 10, 1])

with col2:
    st.write(f"### 第 {st.session_state.quiz_index + 1} 問 / 全 {len(original_quiz_data)} 問")

    if os.path.exists(current_quiz["file"]):
        img_base64 = get_image_base64(current_quiz["file"])
        
        # スタートボタン
        if st.button("クイズをスタート！", use_container_width=True):
            st.session_state.playing = True
            play_audio("これなーんだ？")
            
            placeholder = st.empty()
            # CSSで画像を画面いっぱいに拡大し、ぼかしアニメーションを適用
            # height: 600px と object-fit: cover で、小さい画像も大きく表示させます
            blur_css = f"""
            <style>
            @keyframes reveal {{ from {{ filter: blur(60px); }} to {{ filter: blur(0px); }} }}
            .blur-image {{ 
                width: 100%; 
                height: 600px; 
                object-fit: cover; 
                border-radius: 25px; 
                animation: reveal 10s linear forwards; 
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            }}
            </style>
            <img src="data:image/jpeg;base64,{img_base64}" class="blur-image">
            """
            placeholder.markdown(blur_css, unsafe_allow_html=True)
            
            # 10秒間のアニメーション待ち
            time.sleep(10)
            
            # 正解発表
            ans_text = f"正解は、{current_quiz['answer']}です！"
            play_audio(ans_text)
            st.balloons()
            st.success(f"## {ans_text}")

        # 次へ進むボタン
        if st.session_state.playing:
            if st.session_state.quiz_index < len(st.session_state.shuffled_data) - 1:
                if st.button("次の問題へ 👉", use_container_width=True):
                    st.session_state.quiz_index += 1
                    st.session_state.playing = False
                    st.rerun()
            else:
                st.info("すべての問題が終わりました！")
                if st.button("もう一度（順番をかえて）遊ぶ", use_container_width=True):
                    # データを再シャッフルしてリセット
                    new_data = original_quiz_data.copy()
                    random.shuffle(new_data)
                    st.session_state.shuffled_data = new_data
                    st.session_state.quiz_index = 0
                    st.session_state.playing = False
                    st.rerun()
    else:
        st.error(f"画像 '{current_quiz['file']}' が見つかりません。GitHubに正しくアップロードされているか確認してください。")
