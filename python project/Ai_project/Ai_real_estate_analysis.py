# =========================== #
# 日本不動産AI分析ダッシュボード 
# 2025.12.25 作成
# =========================== #


import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI


# title
st.set_page_config(page_title="AI 東京都 中古マンション 不動産 コンサルタント", page_icon="🏠", layout="wide")


# custom CSS
st.markdown(
    """
    <style>
    .main { background-color: #f8f9fa; }


    [data-testid="stSidebar"] 
    {
        background-color: #2c3e50 !important;
    }


    [data-testid="stSidebar"] h1 
    {
        color: white !important;
    }

    /* sidebar color */
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span 
    {
        color: white !important;
    }
    

    /* sidebar color 2 */
    [data-testid="stSidebar"] hr 
    {
        border-color: rgba(255, 255, 255, 0.2) !important;
    }


    /* font size */
    [data-testid="stMetricValue"]
    {
        font-size: 38px !important;
    }


    /* font size 2 */
    [data-testid="stMetricLabel"] p
    {
        font-size: 22px !important;
    }


    .stButton>button 
    {
        width: 100%; border-radius: 10px; height: 3.5em;
        background-color: #FF4B4B; color: white; font-weight: bold;
        border: none; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }


    div[data-testid="metric-container"] 
    {
        background-color: white; padding: 15px; border-radius: 10px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #efefef;
    }

    /* table size */
    [data-testid="stTable"] th, [data-testid="stDataFrame"] th 
    {
        white-space: nowrap !important;
        min-width: 100px !important;
    }

    /* date frame */
    [data-testid="stDataFrame"] div[data-testid="stTable"] div 
    {
        white-space: nowrap !important;
    }

    </style>
    """, unsafe_allow_html=True
    )


# OpenAI KEY
client = OpenAI(api_key="123456789")


# data load
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("filter_tokyo_real_estate.csv")
        df.columns = df.columns.str.strip()
        return df

    except Exception as e:
        st.error(f"データを読み込めません: {e}")
        return pd.DataFrame()

df = load_data()


# sidebar UI
if not df.empty:
    
    st.sidebar.title("🔍 検索")
    all_areas = sorted(df['市区町村名'].unique())
    selected_area = st.sidebar.selectbox("エリア選択", all_areas)

    space = sorted(df['間取り'].dropna().unique())
    selected_space = st.sidebar.selectbox("間取り選択", space)
    

    max_val = int(df['取引価格（総額）'].max() / 10000) if not df.empty else 20000
    max_price = st.sidebar.slider("💰 最大予算(万円)", 0, max_val, 10000)

    
    display_count = st.sidebar.slider("AI分析 物件数調整", min_value = 1, max_value = 10, value = 5, step = 1)


    filtered_df = df[(df['市区町村名'] == selected_area) & 
                     (df['取引価格（総額）'] <= max_price * 10000) &
                     (df['間取り'] == selected_space)]


    st.title("🏙️ 東京都 中古マンション 不動産 AI分析 ダッシュボード")
    

    # 統計
    m1, m2, m3 = st.columns(3)
    if not filtered_df.empty:
        m1.metric("検索された物件", f"{len(filtered_df)} 件")
        m2.metric("平均相場", f"{int(filtered_df['取引価格（総額）'].mean()/10000):,} 万円")

        area_col = '面積（㎡）' if '面積（㎡）' in filtered_df.columns else '面積（㎡）'
        m3.metric("平均面積", f"{int(filtered_df[area_col].mean())} ㎡")

        st.markdown("---")

        chart_col = st.columns(1)


        with chart_col[0]:
            st.subheader("📊 地域別 平均価格")
            all_region_avg = df.groupby('市区町村名')['取引価格（総額）'].mean().reset_index()

            all_region_avg = all_region_avg.sort_values('取引価格（総額）', ascending=False)
            all_region_avg['平均価格（万円）'] = all_region_avg['取引価格（総額）'] / 10000
  
            fig_all = px.bar(
                all_region_avg,
                x = '市区町村名',
                y = '平均価格（万円）',
                color = '平均価格（万円）',
                height = 1200,
            )

            fig_all.update_yaxes(tickangle=0, automargin=True)
            fig_all.update_layout(height = 800, xaxis_tickangle=-45)
            st.plotly_chart(fig_all, use_container_width = True)


        # 物件リスト
        st.markdown("### 📋 分析対象物件リスト")
        top_matches = filtered_df.head(display_count)
        st.dataframe(top_matches, use_container_width=True)


        # AI 分析
        st.subheader("🤖 AI専門家分析レポート")
        if st.button("GPT-4ominiに詳細分析を要請する"):
            with st.spinner('分析中···'):
                listing_summary = top_matches.to_string(index=False)
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "あなたは日本の不動産投資コンサルタントです。分析対象物件リストに選択された物件をなぜ選択したか理由を具体的に説明してください。分析対象物件リストの順番で説明したください。"},
                            {"role": "user", "content": f"分析データ:\n{listing_summary}"}
                        ],
                        temperature=0.3 # 創意性レベル設定 (0.1~0.5 : 保守的)
                    )
                    st.success("分析完了!")
                    st.markdown(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"エラー発生: {e}")
    else:
        st.error("条件に合う物件がありません。")
else:
    st.error("データを読み込めません。 ファイル名と拡張子を確認してください。")
