import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.write("1년간 박스오피스 10위권에 든 영화 중 해당 기간에 개봉한 216편의 데이터를 살펴봅니다.")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 숫자형 열 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column].astype(str).str.replace(",", "", regex=False),
                errors="coerce"
            )

    # 개봉일: 여덟 자리 숫자를 날짜로 변환
    if "openDt" in df.columns:
        df["openDt"] = pd.to_datetime(
            df["openDt"].astype(str),
            format="%Y%m%d",
            errors="coerce"
        )

    # 장르가 여러 개면 첫 번째 장르만 사용
    if "genre" in df.columns:
        df["genre_first"] = (
            df["genre"]
            .fillna("미상")
            .astype(str)
            .str.split("|")
            .str[0]
            .str.strip()
            .replace("", "미상")
        )
    else:
        df["genre_first"] = "미상"

    return df

try:
    df = load_data()

    st.subheader("데이터 미리보기")
    st.dataframe(df, use_container_width=True)

    st.divider()

    # 첫 번째 그래프: 장르별 영화 편수 도넛 그래프
    st.header("1. 장르별 영화 편수")

    genre_counts = (
        df["genre_first"]
        .value_counts()
        .rename_axis("장르")
        .reset_index(name="영화 편수")
    )

    fig = px.pie(
        genre_counts,
        names="장르",
        values="영화 편수",
        hole=0.48,
        title="장르별 영화 편수 분포",
        labels={"장르": "장르", "영화 편수": "영화 편수"},
        hover_data={"영화 편수": True}
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>"
    )

    fig.update_layout(
        legend_title_text="장르",
        margin=dict(t=70, b=30, l=20, r=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 이 그래프로 알 수 있는 것")
    st.info("장르별 영화 편수와 전체 영화에서 차지하는 비율을 비교할 수 있습니다.")

except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.code(str(e))
