import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# App title and NABLe copyright
st.set_page_config(page_title="Top-down Sentence Repetition Task", layout="centered")
st.title("Top-down Sentence Repetition Task")
st.markdown("""
**Copyright NABLe**
""")

# Load data
df = pd.read_excel("Echoh_scoring_with_word.xlsx")

# Sidebar: SET and ITEM selection
st.sidebar.header("문항 선택")
selected_set = st.sidebar.selectbox("SET 번호를 선택하세요", sorted(df["SET"].unique()))
selected_item = st.sidebar.selectbox("문항 번호를 선택하세요", list(range(1, 29)))

# Filter target sentence based on selection
filtered = df[(df["SET"] == selected_set) & (df["Item"] == selected_item)]
if not filtered.empty:
    target_sentence = filtered.iloc[0]["Target_sen"]
    st.subheader("📌 목표 문장")
    st.write(target_sentence)

    # Input: user response
    response_input = st.text_input("📝 반응 문장을 입력하세요")

    if response_input:
        # Match check functions
        def calc_matched_word(target, response):
            target_words = target.split()
            response_words = response.split()
            return round(sum(w in response_words for w in target_words) / len(target_words) * 100, 2)

        def calc_matched_syllable(target, response):
            target_syls = list(target.replace(" ", ""))
            response_syls = set(response.replace(" ", ""))
            return round(sum(s in response_syls for s in target_syls) / len(target_syls) * 100, 2)

        matched_word = calc_matched_word(target_sentence, response_input)
        matched_syllable = calc_matched_syllable(target_sentence, response_input)
        matched_sem = filtered.iloc[0]["Matched_sem%"]
        matched_syn = filtered.iloc[0]["Matched_syn%"]

        # Show results
        st.subheader("🔎 채점 결과")
        scores = {
            "Word": matched_word,
            "Syllable": matched_syllable,
            "Semantic": matched_sem,
            "Syntactic": matched_syn
        }

        st.write("**점수 요약:**")
        st.dataframe(pd.DataFrame(scores, index=["일치율 (%)"]).T)

        # Plot
        fig, ax = plt.subplots()
        ax.bar(scores.keys(), scores.values())
        ax.set_ylim(0, 100)
        ax.set_ylabel("일치율 (%)")
        ax.set_title("문장 채점 시각화")
        for i, v in enumerate(scores.values()):
            ax.text(i, v + 2, f"{v:.1f}%", ha='center')
        st.pyplot(fig)
else:
    st.warning("해당 SET과 문항 번호에 해당하는 목표 문장이 없습니다.")
