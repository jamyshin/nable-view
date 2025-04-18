import streamlit as st

# ✅ 반드시 가장 위에 있어야 함!
st.set_page_config(page_title="Top-down Sentence Repetition Task", layout="centered")

# 이후에 나머지 import
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

# NABLe 로고 불러오기
logo = Image.open("nable_logo.jpg")  # 파일명은 너가 올린 이름에 맞게
st.image(logo, width=180)  # 사이즈 조정 가능

# --- 제목 & 설명 ---
st.title("Top-down Sentence Repetition Task")
st.markdown("© NABLe | 문장 따라말하기 검사 결과 확인 도구입니다.")
st.markdown("---")

# --- 데이터 불러오기 ---
@st.cache_data
def load_targets():
    df = pd.read_excel("Target_sentences_only.xlsx")
    return df

df = load_targets()

# --- 사이드바 입력 ---
st.sidebar.header("📂 문항 선택")
selected_set = st.sidebar.selectbox("SET 번호", sorted(df["set"].unique()))
filtered_df = df[df["set"] == selected_set]

selected_item = st.sidebar.selectbox("문항 번호", sorted(filtered_df["item"].unique()))
target_sentence = filtered_df.loc[filtered_df["item"] == selected_item, "Target_sen"].values[0]

# --- 본문: 반응 입력 ---
st.subheader(f"SET {selected_set} - ITEM {selected_item}")
st.markdown(f"**🟩 목표 문장:** {target_sentence}")

response_input = st.text_input("📝 반응 문장 입력", placeholder="예: 마트에서 채소를 엄마가 사다")

# --- 점수 계산 함수들 ---
def calc_matched_word(target, response):
    target_words = target.split()
    response_words = response.split()
    if not target_words:
        return 0.0
    match_count = sum([1 for word in target_words if word in response_words])
    return round((match_count / len(target_words)) * 100, 2)

def calc_matched_syllable(target, response):
    target_syls = list(target.replace(" ", ""))
    response_syls = set(response.replace(" ", ""))
    if not target_syls:
        return 0.0
    match_count = sum([1 for syl in target_syls if syl in response_syls])
    return round((match_count / len(target_syls)) * 100, 2)

# 의미 일치율 및 형식 일치율은 예시용 (실제 자동 계산 아니고 임시값)
def dummy_sem_syn():
    return 80.0, 65.0  # 나중에 의미/형식 분석 로직 들어갈 자리

# --- 반응 입력 후 점수 계산 ---
if response_input:
    word_score = calc_matched_word(target_sentence, response_input)
    syl_score = calc_matched_syllable(target_sentence, response_input)
    sem_score, syn_score = dummy_sem_syn()

    # 결과 표
    st.markdown("### ✅ 자동 채점 결과")
    score_data = {
        "Score Type": ["Matched_word%", "Matched_syllable%", "Matched_sem%", "Matched_syn%"],
        "Score": [word_score, syl_score, sem_score, syn_score]
    }
    score_df = pd.DataFrame(score_data)
    st.table(score_df)

    # 막대그래프
    fig, ax = plt.subplots()
    ax.bar(score_data["Score Type"], score_data["Score"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("일치율 (%)")
    ax.set_title("문장 채점 시각화")
    st.pyplot(fig)
