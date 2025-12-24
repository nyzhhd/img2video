# smooth_img2video_v1.py
import streamlit as st
import tempfile
from pathlib import Path
from natsort import natsorted
from moviepy.editor import ImageClip, concatenate_videoclips

st.set_page_config(page_title="丝滑图片→视频", layout="centered")
st.title("🎞️ 丝滑图片转视频（moviepy 1.0.3 版）")

@st.cache_data(show_spinner=False)
def make_smooth_video_v1(file_list, fps, duration_per_img):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        clips = []

        for idx, file in enumerate(file_list):
            img_path = tmpdir / f"{idx:03d}.jpg"
            img_path.write_bytes(file.getbuffer())

            # 基础片段
            clip = ImageClip(str(img_path), duration=duration_per_img)

            # 1. 轻微缩放动画（1.0 → 1.08）
            clip = clip.resize(lambda t: 1 + 0.08 * t / duration_per_img)

            # 2. 水平慢速平移（居中裁剪）
            w, h = clip.w, clip.h
            # 从 0 移到 0.08*w
            clip = clip.set_position(lambda t: (-0.08 * w * t / duration_per_img, 'center'))
            clip = clip.crop(x1=0, y1=0, width=w, height=h)  # 固定画幅

            # 3. 淡入淡出
            clip = clip.fadein(0.5).fadeout(0.5)

            clips.append(clip)

        final = concatenate_videoclips(clips, method="compose")
        out_path = tmpdir / "smooth_v1.mp4"
        final.write_videofile(str(out_path), fps=fps, codec="libx264", audio=False, logger=None)
        return str(out_path)

# ---------- UI 同之前 ----------
with st.sidebar:
    fps = st.number_input("帧率 fps", 1, 60, 24)
    duration = st.number_input("每张图片时长（秒）", 1.0, 10.0, 3.0, 0.5)
    go = st.button("开始合成", type="primary")

uploaded = st.file_uploader("上传图片（可多选）", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if go and uploaded:
    uploaded = natsorted(uploaded, key=lambda x: x.name)
    with st.spinner("正在生成丝滑视频…"):
        mp4_path = make_smooth_video_v1(uploaded, fps, duration)
    st.success("完成！")
    with open(mp4_path, "rb") as f:
        st.download_button("⬇ 下载 smooth_v1.mp4", data=f, file_name="smooth_v1.mp4", mime="video/mp4")
else:
    st.info("上传图片 → 侧边栏调参数 → 点“开始合成”")