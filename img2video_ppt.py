# cv_img2video_ok.py
# @author: nyzhhd
import streamlit as st
import cv2
import numpy as np
import tempfile, os
from pathlib import Path
from natsort import natsorted

st.set_page_config(page_title=" 图片→视频", layout="centered")
st.title("📷 图片转视频工具（幻灯片版）")

@st.cache_data(show_spinner=False)
def make_avi(file_list, fps, dur):
    """返回生成的 avi 绝对路径"""
    # 1. 固定纯英文临时目录，避免中文/空格
    tmpdir = Path(os.getenv("TEMP", "C:/temp")) / "img2video"
    tmpdir.mkdir(exist_ok=True)
    out_path = str(tmpdir / "smooth.avi")

    # 2. 预读一张拿尺寸
    img_bytes = file_list[0].getvalue()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    h, w = img.shape[:2]

    # 3. 最稳的 fourcc：XVID + avi
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    vw = cv2.VideoWriter(out_path, fourcc, fps, (w, h))

    if not vw.isOpened():
        raise RuntimeError("VideoWriter 打开失败，fourcc 或路径问题")

    frames_per_img = int(fps * dur)
    fade = int(fps * 0.5)   # 淡入淡出 0.5s

    for file in file_list:
        img_bytes = file.getvalue()
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        for t in range(frames_per_img):
            # 淡入淡出 alpha
            if t < fade:
                alpha = t / fade
            elif t > frames_per_img - fade:
                alpha = (frames_per_img - t) / fade
            else:
                alpha = 1.0

            # 缩放 1.0 -> 1.08
            zoom = 1.0 + 0.08 * t / frames_per_img
            M = cv2.getRotationMatrix2D((w / 2, h / 2), 0, zoom)
            M[0, 2] -= 0.04 * w * t / frames_per_img   # 水平平移
            res = cv2.warpAffine(img, M, (w, h))
            res = cv2.convertScaleAbs(res, alpha=alpha, beta=0)
            vw.write(res)

    vw.release()          # 必须释放，否则文件句柄占着
    return out_path

# ---------------- UI ----------------
with st.sidebar:
    fps = st.number_input("帧率 fps", 10, 60, 24)
    dur = st.number_input("每张图片时长（秒）", 1.0, 10.0, 3.0, 0.5)
    go = st.button("开始合成", type="primary")

uploaded = st.file_uploader("上传图片（可多选）", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if go and uploaded:
    uploaded = natsorted(uploaded, key=lambda x: x.name)
    with st.spinner("正在生成视频…"):
        avi_path = make_avi(uploaded, fps, dur)
    st.success("完成！")
    with open(avi_path, "rb") as f:
        st.download_button("⬇ 下载 smooth.avi", data=f, file_name="smooth.avi", mime="video/x-msvideo")
else:
    st.info("上传图片 → 侧边栏调参数 → 点“开始合成”")