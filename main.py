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

st.caption("여기에 자유롭게 작성해 보세요.")

st.text_area(
    "장르별 영화 수와 전체 영화에서 차지하는 비율을 알 수 있다.",
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
st.divider()

# 세 번째 그래프: 총 관객 히스토그램
st.header("3. 총 관객 분포")

hist_data = df[["movieNm", "total_audi"]].copy()
hist_data["total_audi"] = pd.to_numeric(
    hist_data["total_audi"],
    errors="coerce"
)

hist_data = hist_data.dropna(subset=["total_audi"])
hist_data = hist_data[hist_data["total_audi"] > 0]

fig3 = px.histogram(
    hist_data,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 분포",
    labels={
        "total_audi": "총 관객",
        "count": "영화 편수"
    }
)

fig3.update_layout(
    xaxis_title="총 관객",
    yaxis_title="영화 편수",
    bargap=0.05,
    margin=dict(t=70, b=30, l=20, r=20)
)

st.plotly_chart(fig3, use_container_width=True)

# 대부분의 영화가 몰려 있는 구간 계산
counts, bins = pd.cut(
    hist_data["total_audi"],
    bins=20,
    retbins=True
)

bin_counts = counts.value_counts().sort_index()
most_common_bin = bin_counts.idxmax()

lower_bound = most_common_bin.left
upper_bound = most_common_bin.right

# 총 관객이 가장 많은 영화
most_popular_movie = hist_data.loc[
    hist_data["total_audi"].idxmax()
]

movie_name = most_popular_movie["movieNm"]
movie_audience = int(most_popular_movie["total_audi"])

st.markdown("#### 💡 이 그래프로 알 수 있는 것")

st.write(
    f"대부분의 영화는 총 관객 약 "
    f"{lower_bound:,.0f}명~{upper_bound:,.0f}명 구간에 몰려 있습니다."
)

st.write(
    f"총 관객이 가장 많은 영화는 **{movie_name}**이며, "
    f"총 관객은 **{movie_audience:,}명**입니다."
)

st.text_area(
    "이 그래프를 보고 알게 된 점을 자유롭게 작성해 보세요.",
    placeholder="여기에 자유롭게 작성해 보세요.",
    height=140,
    key="histogram_graph_observation"
)
st.divider()

# 네 번째 그래프: 개봉일 스크린수와 총 관객의 관계
st.header("4. 개봉일 스크린수와 총 관객의 관계")

scatter_data = df[
    ["movieNm", "genre_first", "first_scrn", "total_audi"]
].copy()

scatter_data["first_scrn"] = pd.to_numeric(
    scatter_data["first_scrn"],
    errors="coerce"
)

scatter_data["total_audi"] = pd.to_numeric(
    scatter_data["total_audi"],
    errors="coerce"
)

scatter_data = scatter_data.dropna(
    subset=["first_scrn", "total_audi"]
)

fig4 = px.scatter(
    scatter_data,
    x="first_scrn",
    y="total_audi",
    color="genre_first",
    hover_name="movieNm",
    hover_data={
        "first_scrn": ":,",
        "total_audi": ":,",
        "genre_first": True
    },
    title="개봉일 스크린수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객",
        "genre_first": "장르"
    }
)

fig4.update_traces(
    marker=dict(size=10, opacity=0.7)
)

fig4.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객",
    margin=dict(t=70, b=30, l=20, r=20)
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("#### 💡 이 그래프로 알 수 있는 것")

st.write(
    "개봉일 스크린수와 총 관객 사이의 관계를 살펴보고, "
    "장르별 영화의 분포와 특성을 비교할 수 있습니다."
)

st.text_area(
    "이 그래프를 보고 알게 된 점을 자유롭게 작성해 보세요.",
    placeholder="여기에 자유롭게 작성해 보세요.",
    height=140,
    key="scatter_graph_observation"
)
