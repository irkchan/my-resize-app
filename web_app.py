import streamlit as st
from PIL import Image
import io
import os
import zipfile

# ページの設定
st.set_page_config(page_title="リサイズくん", page_icon="🖼️", layout="wide")

# --- 🎨 サイドバー：設定 ---
with st.sidebar:
    st.header("⚙️ 全体の設定")
    common_prefix = st.text_input("基本の管理番号：", "", placeholder="空欄なら個別設定が優先されます")
    new_width = st.number_input("リサイズしたい「幅」 (px)：", min_value=10, max_value=5000, value=640, step=1)
    
    st.divider()
    st.subheader("📦 まとめて保存")
    st.write("画像を選択した後にボタンが表示されます")
    
    # ボタンの置き場所を確保
    zip_placeholder = st.empty()
    
    st.divider()
    st.info("🐈 作業お疲れ様です！丁寧にリサイズしていきます。")

# --- 🏠 メイン画面 ---
st.title("🎨 画像リサイズ & リネームツール")

uploaded_files = st.file_uploader(
    "画像をえらんでね（複数OK）：", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.subheader(f"📝 1枚ずつの確認・設定 ({len(uploaded_files)}枚)")
    
    suffix_options = ["_after", "_before", "_main", "_s1", "_s2", "_s3", "_s4", "（なし）"]
    processed_images = []

    for i, file in enumerate(uploaded_files):
        with st.container(border=True):
            img = Image.open(file)
            ext = os.path.splitext(file.name)[1]
            original_name = file.name

            col_img, col_org, col_head, col_suffix = st.columns([1, 2, 2, 1.5])
            
            with col_img:
                st.image(img, use_container_width=True)
            with col_org:
                st.write("📎 **元の名前**")
                st.caption(original_name)
            
            with col_head:
                # 全体の設定があればそれを初期値に、なければ空にする
                indiv_prefix = st.text_input(
                    "新しい管理番号", 
                    value=common_prefix, 
                    key=f"head_{i}",
                    placeholder="空欄なら元の名前を使用"
                )
            
            with col_suffix:
                indiv_suffix = st.selectbox("ラベル", options=suffix_options, index=0, key=f"suffix_{i}")
            
            # --- 名前の組み立てルール ---
            if indiv_prefix == "":
                # 管理番号が空なら、ラベルも付けず元の名前
                final_full_name = original_name
            else:
                # 管理番号があるなら、ラベルと組み合わせる
                chosen_suffix = "" if indiv_suffix == "（なし）" else indiv_suffix
                final_full_name = f"{indiv_prefix}{chosen_suffix}{ext}"
            
            # --- リサイズ処理 ---
            old_width, old_height = img.size
            new_height = int(old_height * (new_width / old_width))
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            buf = io.BytesIO()
            img_resized.save(buf, format=img.format, quality=95)
            img_data = buf.getvalue()
            processed_images.append({"name": final_full_name, "data": img_data})

            # --- 個別保存ボタン ---
            res_col1, res_col2 = st.columns([3, 1])
            with res_col1:
                st.success(f"✅ 保存名: **{final_full_name}**")
            with res_col2:
                # keyを一意に固定（individual_save_0, 1...）
                st.download_button(
                    label="💾 保存", 
                    data=img_data, 
                    file_name=final_full_name, 
                    key=f"individual_save_{i}", 
                    use_container_width=True
                )

    # --- まとめて保存用のZIP作成（インデントは if uploaded_files の中） ---
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for image in processed_images:
            zip_file.writestr(image["name"], image["data"])
    
    # サイドバーのボタンを表示（keyを完全に別名にする）
    zip_placeholder.download_button(
        label="🚀 まとめてダウンロード (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="resized_images.zip",
        mime="application/zip",
        use_container_width=True,
        type="primary",
        key="bulk_zip_download_unique_final"
    )
