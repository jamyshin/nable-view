import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt

# --- 페이지 설정 ---
st.set_page_config(page_title="Top-down Sentence Repetition Task", layout="centered")

# --- NABLe 로고 ---
logo = Image.open("nable_logo.jpg")
st.image(logo, width=500)

# --- 제목 & 설명 ---
st.title("Top-down Sentence Repetition Task")
st.markdown("---")

# --- 데이터 불러오기 ---
@st.cache_data
def load_answers():
    return pd.read_excel("Answers.xlsx")

df = load_answers()

# --- 세션 상태 초기화 ---
if "current_item" not in st.session_state:
    st.session_state.current_item = 1
if "responses" not in st.session_state:
    st.session_state.responses = {}

# --- SET 선택 (숫자 순 정렬) ---
set_options = sorted(df["set"].dropna().unique(), key=lambda x: int(str(x).split()[-1]))
selected_set = st.sidebar.selectbox("SET 번호를 선택하세요", set_options)

# --- 현재 문항 표시 ---
st.markdown(f"### ✔️ 현재 문항: {selected_set} - {st.session_state.current_item}/28")

# --- 정답 문항 불러오기 ---
def get_target_row(set_val, item_val):
    return df[(df["set"] == set_val) & (df["item"] == item_val)].iloc[0]

try:
    target_row = get_target_row(selected_set, st.session_state.current_item)
    target_sentence = target_row["Target_sen"]

    target_words = [target_row.get(f"Target_word{i+1}") for i in range(10) if pd.notna(target_row.get(f"Target_word{i+1}"))]
    target_syllables = [target_row.get(f"Target_syl{i+1}") for i in range(20) if pd.notna(target_row.get(f"Target_syl{i+1}"))]
    target_sem = [target_row.get(f"Target_sem{i+1}") for i in range(5) if pd.notna(target_row.get(f"Target_sem{i+1}"))]
    target_syn = [target_row.get(f"Target_syn{i+1}") for i in range(5) if pd.notna(target_row.get(f"Target_syn{i+1}"))]

    # --- 목표 문장 박스 (회색 톤온톤) ---
    st.markdown(
        f"""
        <div style='
            background-color: #f5f5f5;
            padding: 12px 16px;
            border-left: 6px solid #999999;
            border-radius: 6px;
            font-size: 20px;
            margin-top: 10px;
            margin-bottom: 10px;
        '>
            <strong></strong> {target_sentence}
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- 반응 입력 ---
    response = st.text_input("● 반응 문장을 입력하세요", key=f"response_{st.session_state.current_item}")

    
    # --- 채점 함수 ---
    def matched_word_score(target_words, response_words):
        matched = sum(1 for w in target_words if w in response_words)
        missing = [w for w in target_words if w not in response_words]
        missing_penalty = len(missing)

        extra = [w for w in response_words if w not in target_words]
        extra_penalty = 1 if extra else 0

        # 도치 감점 (정답 단어들끼리의 순서 비교)
        filtered_response = [w for w in response_words if w in target_words]
        order_penalty = 1 if filtered_response != [w for w in target_words if w in filtered_response] else 0

        total_penalty = missing_penalty + extra_penalty + order_penalty
        score = (len(target_words) - total_penalty) / len(target_words)
        return round(max(score, 0) * 100, 2)

    def matched_syllable_score(target_syllables, response_sentence):
        response_syllables = list(response_sentence.replace(" ", ""))
        target_set = set(target_syllables)
        response_set = set(response_syllables)
        matched = len(target_set.intersection(response_set))
        return round(matched / len(target_set) * 100, 2) if target_set else 0

    def matched_list_score(target_list, response_sentence):
        return round(sum(1 for tok in target_list if str(tok) in response_sentence) / len(target_list) * 100, 2) if target_list else 0

    # --- 점수 계산 ---
    if response:
        response_words = response.split()

        word_pct = matched_word_score(target_words, response_words)
        syl_pct = matched_syllable_score(target_syllables, response)
        sem_pct = matched_list_score(target_sem, response)
        syn_pct = matched_list_score(target_syn, response)

        st.session_state.responses[st.session_state.current_item] = {
            "Word": word_pct,
            "Syllable": syl_pct,
            "Semantic": sem_pct,
            "Syntactic": syn_pct
        }

        # --- 점수 테이블 ---
        st.markdown("#### ✏️ 본 문항의 점수")
        st.write(pd.DataFrame([{
            "Word": word_pct,
            "Syllable": syl_pct,
            "Semantic": sem_pct,
            "Syntactic": syn_pct
        }]))

        # --- 그래프 ---
        fig, ax = plt.subplots()
        labels = ["Word", "Syllable", "Semantic", "Syntactic"]
        scores = [word_pct, syl_pct, sem_pct, syn_pct]
        colors = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2']
        bars = ax.bar(labels, scores, color=colors)
        ax.set_ylim(0, 100)
        ax.set_ylabel("Score (%)")
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:.1f}%", ha='center')
        st.pyplot(fig)

        # --- 다음 문항으로 이동 ---
        if st.session_state.current_item < 28:
            if st.button("➡️ 다음 문항으로 이동"):
                st.session_state.current_item += 1
                st.rerun()
        else:
            st.markdown("✅ 모든 문항 입력이 완료되었습니다.")

    # --- 평균 점수 계산 ---
    if len(st.session_state.responses) == 28:
        st.markdown("---")
        st.markdown("### 📊 전체 검사 결과 (Average across all items)")
        df_avg = pd.DataFrame(st.session_state.responses).T
        avg_scores = df_avg.mean().round(2)
        st.dataframe(avg_scores.to_frame(name="Average (%)"))

        fig, ax = plt.subplots()
        bars = ax.bar(avg_scores.index, avg_scores.values, color=colors)
        ax.set_ylim(0, 100)
        ax.set_ylabel("Score (%)")
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:.1f}%", ha='center')
        st.pyplot(fig)

except IndexError:
    st.error("❌ 해당 SET과 ITEM에 대한 정답 정보가 없습니다.")

# --- 저작권 안내 문구 (화면 하단 고정 스타일) ---
st.markdown("---")
st.markdown(
    """
    <div style='font-size: 14px; color: gray; text-align: center;'>
        © 2025 NABLe. All rights reserved. <br>
        본 검사도구는 NABLe 연구팀에 의해 개발되었으며, 무단 복제 및 사용을 금합니다. <br>
        <i>Top-down Sentence Repetition Task™</i> is the intellectual property of NABLe. Unauthorized commercial use or redistribution is prohibited.
    </div>
    """,
    unsafe_allow_html=True
)
