import streamlit as st
from google import genai

st.set_page_config(page_title="献立＆買い物リスト生成", layout="centered")

st.title("🍳 節約・献立プランナー")

if "GEMINI_API_KEY" in st.secrets:
  api_key = st.secrets["GEMINI_API_KEY"]
else:
  with st.sidebar:
    st.header("設定")
    api_key = st.text_input("Gemini API Key", type="password")

budget = st.number_input("今回の買い出し予算 (円)", min_value=1000, max_value=50000, value=3500, step=500)
days = st.slider("日数", min_value=1, max_value=7, value=4)
main_ingredients = st.text_input("使いたい食材・余り物（任意）", placeholder="例：鶏むね肉、キャベツ、豆腐")

if st.button("献立と買い物リストを作成", type="primary"):
    if not api_key:
        st.warning("左側のサイドバーにGemini APIキーを入力してください。")
    else:
        with st.spinner("コスパ献立を計算中..."):
            try:
                client = genai.Client(api_key=api_key)
                
                prompt = f"""
                あなたは優秀な節約料理アドバイザーです。
                以下の条件で、無駄のない献立プランと買い物リストを作成してください。

                【条件】
                - 期間: {days}日分（夕食）
                - 買い出し予算: {budget}円以内
                - 使いたい食材: {main_ingredients if main_ingredients else "特になし（コスパ重視で選定）"}

                【出力構成】
                1. **買い出しリスト**: 予算内に収まる食材名と概算価格
                2. **{days}日間の夕食献立**: 
                   - 各日の主菜・副菜・汁物
                   - 食材の使い回しポイント（食材ロスが出ない工夫）
                3. **節約ワンポイントメモ**
                """

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt
                )

                st.success("献立が完成しました！")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
