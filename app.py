import streamlit as st
from gtts import gTTS
import base64
import time
import os

# ページ設定
st.set_page_config(page_title="連想クイズ・コレクション", layout="centered")

# --- 音声生成・取得関数 ---
def get_audio_html(text, filename_prefix):
    # ファイル名が重複しないよう、テキストのハッシュなどを利用するのが理想ですが
    # 今回はシンプルに一時ファイルとして生成します
    filepath = f"{filename_prefix}.mp3"
    tts = gTTS(text=text, lang='ja')
    tts.save(filepath)
    
    with open(filepath, "rb") as f:
        audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    # 自動再生（autoplay）を有効にしたHTML
    return f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay style="display:none;">'

# --- 画像をBase64に変換 ---
def get_image_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- クイズデータのリスト ---
# ご指定の項目をすべて追加しました
quiz_data = [
    {"answer": "りんご", "file": "wide_thumbnail_large.jpg"},
    {"answer": "ばなな", "file": "banana.jpg"},
    {"answer": "もも", "file": "momo.jpg"},
    {"answer": "きうい", "file": "kiui.jpg"},
    {"answer": "ぶどう", "file": "budou.jpg"},
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

# セッション状態（現在の問題番号）の管理
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0

# 現在の問題を取得
current_quiz = quiz_data[st.session_state.quiz_index]

st.subheader(f"第 {st.session_state.quiz_index + 1} 問 / 全 {len(quiz_data)} 問")

if os.path.exists(current_quiz["file"]):
    img_base64 = get_image_base64(current_quiz["file"])
    
    # 画面レイアウト用のコンテナ
    container = st.container()
    
    if st.button("クイズをスタート！", key="start_btn"):
        # ① 問題音声の再生
        st.components.v1.html(get_audio_html("これなーんだ？", "q_sound"), height=0)
        
        # ② 10秒かけてボカシを消すアニメーション
        placeholder = st.empty()
        blur_css = f"""
        <style>
        @keyframes reveal {{
            from {{ filter: blur(60px); }}
            to {{ filter: blur(0px); }}
        }}
        .blur-image {{
            width: 100%;
            max-width: 600px;
            border-radius: 20px;
            animation: reveal 10s linear forwards;
            box-shadow: 0 8px 30px rgba(0,0,0,0.2);
        }}
        </style>
        <img src="data:image/jpeg;base64,{img_base64}" class="blur-image">
        """
        placeholder.markdown(blur_css, unsafe_allow_html=True)
        
        # ③ 10秒待機
        time.sleep(10)
        
        # ④ 正解発表
        ans_text = f"正解は、{current_quiz['answer']}です！"
        st.components.v1.html(get_audio_html(ans_text, "a_sound"), height=0)
        st.balloons()
        st.success(ans_text)
        
        # 次へ進むボタン
        if st.session_state.quiz_index < len(quiz_data) - 1:
            if st.button("次の問題へ 👉"):
                st.session_state.quiz_index += 1
                st.rerun()
        else:
            st.info("全問クリア！おめでとうございます！ 🎉")
            if st.button("最初から遊ぶ"):
                st.session_state.quiz_index = 0
                st.rerun()
else:
    st.error(f"画像ファイル '{current_quiz['file']}' が見つかりません。GitHubにアップロードしてください。")
