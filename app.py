
import streamlit as st

st.title("🧠 의미 일치율 계산기")

target_input = st.text_input("✅ Target 단어들 (쉼표로 구분)", "엄마, 밥, 먹다")
user_sentence = st.text_area("🗣️ 사용자가 말한 문장", "엄마가 밥을 먹었어요")

def calculate_match(target_str, response_str):
    target_set = set([w.strip() for w in target_str.split(",")])
    response_words = set(response_str.replace(" ", ""))
    matched = {w for w in target_set if w in response_words}
    score = round(len(matched) / len(target_set) * 100, 2) if target_set else 0
    return score, matched

if st.button("🎯 의미 일치율 계산하기"):
    score, matched = calculate_match(target_input, user_sentence)
    st.metric("일치율", f"{score}%")
    st.write("포함된 단어:", matched)
