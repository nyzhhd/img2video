# img2video.py
# 图片→视频工具
# @author: nyzhhd
# 1. 安装依赖（一次性）
# pip install streamlit opencv-python-headless natsort
# 2. 运行
# streamlit run img2video_simpy.py

import streamlit as st
import cv2
import os
import tempfile
import zipfile
from natsort import natsorted
from pathlib import Path

st.set_page_config(page_title="图片→视频工具", layout="centered")
st.title("📁 图片转视频 + 下载")

# 参数侧边栏
with st.sidebar:
    fps = st.number_input("帧率 fps", min_value=0.1, max_value=60.0, value=1.0, step=0.1)
    ext = st.multiselect("图片后缀", ["jpg", "png", "jpeg"], default=["jpg", "png"])
    start_button = st.button("开始合成", type="primary")

# 上传图片（支持拖拽整个文件夹）
uploaded = st.file_uploader(
    "上传图片（可多选，按文件名排序）",
    type=ext,
    accept_multiple_files=True
)

if start_button and uploaded:
    # 按文件名自然排序
    uploaded = natsorted(uploaded, key=lambda x: x.name)

    # 临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        video_path = tmpdir / "output.mp4"

        # 先全部写到磁盘（cv2 需要文件路径）
        img_paths = []
        for file in uploaded:
            p = tmpdir / file.name
            p.write_bytes(file.getbuffer())
            img_paths.append(str(p))

        # 读第一张拿尺寸
        frame = cv2.imread(img_paths[0])
        h, w, _ = frame.shape
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        vw = cv2.VideoWriter(str(video_path), fourcc, fps, (w, h))

        for p in img_paths:
            vw.write(cv2.imread(p))
        vw.release()

        # 提供下载
        st.success("合成完成！")
        with open(video_path, "rb") as f:
            st.download_button(
                label="⬇ 下载 video.mp4",
                data=f,
                file_name="video.mp4",
                mime="video/mp4"
            )
else:
    st.info("请先上传图片，再点侧边栏“开始合成”")