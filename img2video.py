# hz_img2video.py
# @author: nyzhhd
import streamlit as st
import cv2
import numpy as np
import tempfile, os
from pathlib import Path
from natsort import natsorted

st.set_page_config(page_title="按频率图片→视频", layout="centered")
st.title("📺 图片按固定频率转视频（无特效）")

@st.cache_data(show_spinner=False)
def make_hz_video(file_list, hz):
    """hz = 每秒播放几张图（每张图重复 fps/hz 帧）"""
    tmpdir = Path(os.getenv("TEMP", "C:/temp")) / "hz_video"
    tmpdir.mkdir(exist_ok=True)
    avi_path = str(tmpdir / "hz_video.avi")

    # 拿尺寸
    img_bytes = file_list[0].getvalue()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    h, w = img.shape[:2]

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    vw = cv2.VideoWriter(avi_path, fourcc, 30, (w, h))   # 固定 30 fps 输出
    if not vw.isOpened():
        raise RuntimeError("VideoWriter 无法打开")

    frames_per_pic = int(30 / hz)          # 30 fps 下的帧数
    for file in file_list:
        img_bytes = file.getvalue()
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        for _ in range(frames_per_pic):
            vw.write(img)

    vw.release()
    return avi_path

# ---------------- 侧边栏 ----------------
with st.sidebar:
    hz = st.radio("播放频率 Hz（张/秒）", [10, 5, 3, "自定义"], horizontal=True)
    if hz == "自定义":
        hz = st.number_input("自定义 Hz", 0.5, 60.0, 2.0, 0.5)
    hz = float(hz)
    go = st.button("开始合成", type="primary")

# ---------------- 主界面 ----------------
uploaded = st.file_uploader("上传图片（可多选，按文件名排序）",
                            type=["jpg", "jpeg", "png"],
                            accept_multiple_files=True)

if go and uploaded:
    uploaded = natsorted(uploaded, key=lambda x: x.name)
    with st.spinner(f"正在生成 {hz} Hz 视频…"):
        avi_path = make_hz_video(uploaded, hz)
    st.success("完成！")
    with open(avi_path, "rb") as f:
        st.download_button(f"⬇ 下载 {hz}Hz.avi", data=f,
                          file_name=f"{hz}Hz.avi",
                          mime="video/x-msvideo")
else:
    st.info("上传图片 → 侧边栏选频率 → 点“开始合成”")