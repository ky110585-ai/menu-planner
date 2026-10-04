import streamlit as st
import google.generativeai as genai

# ページ基本設定
st.set_page_config(page_title="家族の節約・献立プランナー", page_icon="🍳", layout="centered")

# SecretsまたはサイドバーからAPIキーを取得
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        st.header("設定")
        api_key = st.text_input("Gemini API Key", type="password")

st.title("🍳 家族の節約・献立プランナー")
st.caption("人数や好みに合わせて、無駄のない献立と買い物リストを自動作成します")

# 入力フォーム
col1, col2 = st.columns(2)
with col1:
    adults = st.number_input("大人の人数", min_value=1, max_value=10, value=2, step=1)
with col2:
    children = st.number_input("子どもの人数", min_value=0, max_value=10, value=0, step=1)

col3, col4 = st.columns(2)
with col3:
    budget = st.number_input("今回の買い出し予算（円）", min_value=1000, max_value=50000, value=6000, step=500)
with col4:
    days = st.slider("日数", min_value=1, max_value=7, value=3)

preferences = st.multiselect(
    "献立のこだわり・重視したいこと（複数選択可）",
    ["子どもが喜ぶ味付け", "野菜たっぷり・栄養バランス", "調理時間20分以内（時短）", "作り置き・お弁当に回せる", "ボリューム重視（ガッツリ系）", "和食中心", "胃腸にやさしい・あっさり"],
    default=["野菜たっぷり・栄養バランス"]
)

ingredients = st.text_input("使いたい食材・冷蔵庫の余り物（任意）", placeholder="例：キャベツ1玉、豚こま、豆腐、大根")

# 作成ボタン
if st.button("献立と買い物リストを作成", type="primary"):
    if not api_key:
        st.error("APIキーが設定されていません。サイドバーから入力するか、Secretsに登録してください。")
    else:
        with st.spinner("栄養バランスと予算を計算しながら献立を作成中..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash-latest")

                pref_text = "、".join(preferences) if preferences else "特になし"
                ing_text = ingredients if ingredients else "特になし（自由に必要な食材を提案してください）"

                prompt = f"""
あなたはプロの料理研究家であり、家計管理と献立設計のエキスパートです。
以下の条件に合わせて、【{days}日分の家族向け献立】と、スーパーでそのまま買える【分類別 買い物リスト】を作成してください。

【条件】
- 家族構成: 大人 {adults}人、子ども {children}人
- 買い出し予算: 約 {budget}円以内
- 日数: {days}日分（夕食メイン）
- 重視したいポイント: {pref_text}
- 使いたい食材・余り物: {ing_text}

【出力フォーマット】
1. 予算と構成のポイント（ひとこと）
2. {days}日分の献立（日付ごとに主菜・副菜・汁物、簡単な調理のコツや使い回しポイントを明記）
3. スーパー買い出しリスト（野菜類・肉魚類・日配品/大豆製品・その他/調味料に分類し、目安量とおおよその概算金額を記載）
4. 食材を無駄にしない保存・仕込みアドバイス
"""

                response = model.generate_content(prompt)
                st.markdown(response.text)

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
