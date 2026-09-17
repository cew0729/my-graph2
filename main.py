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

    if "openDt" in df.columns:
        df["openDt"] = pd.to_datetime(
            df["openDt"].astype(str),
            format="%Y%m%d",
            errors="coerce"
        )

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
        labels={
            "장르": "장르",
            "영화 편수": "영화 편수"
        }
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "편수: %{value}편<br>"
            "비율: %{percent}<extra></extra>"
        )
    )

    fig.update_layout(
        legend_title_text="장르",
        margin=dict(t=70, b=30, l=20, r=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 💡 이 그래프로 알 수 있는 것")

    st.text_area(
        "이 그래프를 보고 알게 된 점을 자유롭게 작성해 보세요.",
        placeholder="여기에 자유롭게 작성해 보세요.",
        height=140,
        key="genre_graph_observation"
    )

except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.code(str(e))
    st.divider()

# 두 번째 그래프: 장르별 영화 트리맵
st.header("2. 장르별 영화 총 관객 트리맵")

treemap_data = df[
    ["genre_first", "movieNm", "total_audi"]
].copy()

treemap_data["movieNm"] = (
    treemap_data["movieNm"]
    .fillna("영화명 미상")
    .astype(str)
)

treemap_data["total_audi"] = pd.to_numeric(
    treemap_data["total_audi"],
    errors="coerce"
)

treemap_data = treemap_data.dropna(subset=["total_audi"])
treemap_data = treemap_data[treemap_data["total_audi"] > 0]

fig2 = px.treemap(
    treemap_data,
    path=["genre_first", "movieNm"],
    values="total_audi",
    color="genre_first",
    title="장르 안에 포함된 영화별 총 관객 규모",
    labels={
        "genre_first": "장르",
        "movieNm": "영화명",
        "total_audi": "총 관객"
    },
    custom_data=["movieNm", "total_audi"]
)

fig2.update_traces(
    hovertemplate=(
        "<b>영화명: %{customdata[0]}</b><br>"
        "총 관객: %{customdata[1]:,}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    margin=dict(t=70, b=30, l=20, r=20)
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("#### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "이 그래프를 보고 알게 된 점을 자유롭게 작성해 보세요.",
    placeholder="여기에 자유롭게 작성해 보세요.",
    height=140,
    key="treemap_graph_observation"
)
