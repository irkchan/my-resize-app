import streamlit as st
from PIL import Image
import io
import os
import zipfile

# ページの設定
st.set_page_config(page_title="命名＆リサイズくん Pro", page_icon="🖼️", layout="wide")

# キャッシュ掃除
st.cache_data.clear()

# --- 🎨 サイドバー：設定 ---
with st.sidebar:
    st.header("⚙️ 全体の設定")
    common_prefix = st.text_input("基本の管理番号：", "", placeholder="例: ABC-001")
    
    st.divider()
    # リサイズ機能のON/OFF
    no_resize = st.checkbox("リサイズしない（名前変更のみ）", value=False)
    
    if not no_resize:
        new_width = st.number_input("リサイズしたい「幅」 (px)：", min_value=10, max_value=5000, value=640, step=1)
    else:
        st.info("ℹ️ 元のサイズを維持してリネームします")
    
    st.divider()
    st.subheader("📦 まとめて保存")
    zip_placeholder = st.empty()

# --- 🏠 メイン画面 ---
st.title("🎨 画像リサイズ & 命名ツール")

uploaded_files = st.file_uploader(
    "画像をえらんでね（複数OK）：", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.subheader(f"📝 設定 ({len(uploaded_files)}枚)")
    
    # ラベルの選択肢をs10まで拡張＋自由入力を追加
    suffix_options = [
        "_after", "_before", "_main", 
        "_s1", "_s2", "_s3", "_s4", "_s5", 
        "_s6", "_s7", "_s8", "_s9", "_s10", 
        "（なし）", "（自由入力）"
    ]
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
                indiv_prefix = st.text_input(
                    "新しい管理番号", 
                    value=common_prefix, 
                    key=f"head_{i}",
                    placeholder="空欄なら元の名前を使用"
                )
            
            with col_suffix:
                indiv_suffix = st.selectbox("ラベル", options=suffix_options, index=0, key=f"suffix_{i}")
                
                # 「自由入力」が選ばれた時だけ入力欄を出す
                custom_suffix = ""
                if indiv_suffix == "（自由入力）":
                    custom_suffix = st.text_input("自由なラベルを入力：", key=f"custom_{i}", placeholder="例: _cut")
            
            # --- 命名処理のロジック ---
            if indiv_prefix == "":
                final_full_name = original_name
            else:
                if indiv_suffix == "（なし）":
                    actual_suffix = ""
                elif indiv_suffix == "（自由入力）":
                    actual_suffix = custom_suffix
                else:
                    actual_suffix = indiv_suffix
                
                final_full_name = f"{indiv_prefix}{actual_suffix}{ext}"
            
            # --- リサイズ処理 ---
            if no_resize:
                img_final = img
            else:
                old_width, old_height = img.size
                new_height = int(old_height * (new_width / old_width))
                img_final = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 保存用データ作成
            buf = io.BytesIO()
            img_final.save(buf, format=img.format, quality=95)
            img_data = buf.getvalue()
            processed_images.append({"name": final_full_name, "data": img_data})

            res_col1, res_col2 = st.columns([3, 1])
            with res_col1:
                st.success(f"✅ 保存名: **{final_full_name}**")
            with res_col2:
                st.download_button(
                    label="💾 保存", 
                    data=img_data, 
                    file_name=final_full_name, 
                    key=f"individual_save_{i}", 
                    use_container_width=True
                )

    # ZIP作成
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for image in processed_images:
            zip_file.writestr(image["name"], image["data"])
    
    zip_placeholder.download_button(
        label="🚀 まとめてダウンロード (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="resized_images.zip",
        mime="application/zip",
        use_container_width=True,
        type="primary",
        key="bulk_zip_download_final_pro"
    )
