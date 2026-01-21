import streamlit as st
from PIL import Image
import io
import os
import zipfile

# ページの設定
st.set_page_config(page_title="リサイズくん Pro", page_icon="🖼️", layout="wide")

# --- 🎨 サイドバー：設定と「ついてくる」一括保存ボタン ---
with st.sidebar:
    st.header("⚙️ 全体の設定")
    common_prefix = st.text_input("管理番号：", "")
    new_width = st.number_input("リサイズしたい「幅」 (px)：", min_value=10, max_value=5000, value=640, step=1)
    
    st.divider()
    
    # 💡 ここにメッセージとボタンを置くことで、スクロールしてもずっと左側にいます
    st.subheader("📦 まとめて保存")
    st.write("画像が複数枚ある時はまとめて保存が便利です。画像を選択した後に保存ボタンが表示されます")
    
    # 後で使うためにボタンの置き場所だけ確保しておく
    zip_placeholder = st.empty()
    
    st.divider()
    st.info("")

# --- 🏠 メイン画面 ---
st.title("🎨 画像リサイズ & リネームくん")

uploaded_files = st.file_uploader(
    "リサイズしたい画像をえらんでね（複数OK）：同じ管理番号の画像を入れるとリネームが便利です", 
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
                # 💡 ここがポイント！
                # 全体の設定(common_prefix)が空なら、個別に好きな文字を打てる。
                # 全体の設定に何か入っていれば、それが自動で入る。
                indiv_prefix = st.text_input(
                    "新しい管理番号", 
                    value=common_prefix, 
                    key=f"head_{i}",
                    placeholder="空欄なら元の名前を使用"
                )
            
            with col_suffix:
                indiv_suffix = st.selectbox("ラベル", options=suffix_options, index=0, key=f"suffix_{i}")
            
            # --- 💡 名前の組み立てルール ---
            if indiv_prefix == "":
                # 管理番号が空なら、ラベルも付けず「元の名前」のまま
                final_full_name = original_name
            else:
                # 管理番号があるなら、ラベルと組み合わせる
                chosen_suffix = "" if indiv_suffix == "（なし）" else indiv_suffix
                final_full_name = f"{indiv_prefix}{chosen_suffix}{ext}"
            
            # 以降、リサイズと保存ボタンの処理（今のコードと同じ）
            old_width, old_height = img.size
            new_height = int(old_height * (new_width / old_width))
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            buf = io.BytesIO()
            img_resized.save(buf, format=img.format, quality=95)
            img_data = buf.getvalue()
            processed_images.append({"name": final_full_name, "data": img_data})

            res_col1, res_col2 = st.columns([3, 1])
            with res_col1:
                st.success(f"✅ 保存名: **{final_full_name}**")
            with res_col2:
                st.download_button(label="💾 保存", data=img_data, file_name=final_full_name, key=f"individual_save_{i}, use_container_width=True)
            
         # --- 名前の組み立て（賢いバージョン） ---
            if indiv_prefix == "":
                # 💡 管理番号が空なら、ラベルも無視して「元の名前」をそのまま使う
                final_full_name = original_name
            else:
                # 管理番号が入っている時だけ、ラベルを組み合わせてリネームする
                chosen_suffix = "" if indiv_suffix == "（なし）" else indiv_suffix
                final_full_name = f"{indiv_prefix}{chosen_suffix}{ext}"
            
            # リサイズ処理
            old_width, old_height = img.size
            new_height = int(old_height * (new_width / old_width))
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            buf = io.BytesIO()
            img_resized.save(buf, format=img.format, quality=95)
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
                    key="all_zip_download",
                    use_container_width=True
                )

    # --- 💡 サイドバーに「一括保存ボタン」を出現させる ---
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for image in processed_images:
            zip_file.writestr(image["name"], image["data"])
    
   # サイドバーの確保しておいた場所にボタンを表示
    zip_placeholder.download_button(
        label="🚀 まとめてダウンロード (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="resized_images.zip",
        mime="application/zip",
        use_container_width=True,
        type="primary",
        key="all_zip_download_button" # 💡 ここを独自の固定名に変える
    )
    
