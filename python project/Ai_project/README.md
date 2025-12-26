## Tokyo Real Estate AI Dashboard </br> AI活用型 東京都中古マンション不動産コンサルタント
- 本プロジェクトは、OpenAI APIを活用し、2025年東京都全域の中古マンション実取引データを基に、</br>
地域別相場を可視化するStreamlitベースのWebアプリケーションです。</br>
ユーザーが希望する条件に合致する物件をリストアップし、その物件をAIが推薦する理由を確認できます。</br>
OpenAIはGPT-4o miniを使用しました。
</br>

### 📊 データ処理
- データソースTokyo_20251_20252.csvから必要なカラムのみを抽出・整形し、filter_tokyo_real_estate.csvを作成しました。</br>
処理ファイル：filter_tokyo.ipynb（Jupyter Lab使用）</br>
</br>

### ✨ 主な機能
- 全体地域相場比較（Global View）
サイドバーフィルターとは独立して、東京都全体の区・市の平均価格を棒グラフで比較表示します。

- 動的フィルタリング（Dynamic Filtering）
地域（区・市）、間取りを選択し、該当データのみを抽出できます。

- データサマリー（Data Summary）
選択した条件に該当する物件数、平均取引価格、平均面積を一目で確認できる要約表を提供します。

- AI推薦機能
個人のOpenAI API Keyを活用するため、GitHubアップロード版ではKey入力部分のみを実装しています。</br>
ご自身のAPI Keyを入力することでサービスをご利用いただけます。
</br></br>

### スクリーンショット①
<img width="1920" height="2874" alt="image" src="https://github.com/user-attachments/assets/48c42313-38ae-4115-bba2-e54c7f41cb11" />
</br></br>

### スクリーンショット②
<img width="1920" height="2737" alt="image" src="https://github.com/user-attachments/assets/699659f2-61b2-4f05-8b51-50e162fef29d" />
</br></br>

### 🛠️ 技術スタック </br>
Language: Python </br>
Framework: Streamlit（Web UI）</br>
Data Analysis: Pandas </br>
Visualization: Plotly Express </br>
