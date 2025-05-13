import streamlit as st
from moviepy.editor import VideoFileClip, concatenate_videoclips
import tempfile
import os

st.set_page_config(page_title="Smooth Video Looper", layout="centered")
st.title("🔁 Smooth Video Looper")
st.write("Unggah video berdurasi **minimal 4 detik**, dan kami akan membuat versi looping yang halus.")

uploaded_file = st.file_uploader("🎞️ Unggah file MP4:", type=["mp4"])

crossfade_duration = st.slider("🎚️ Durasi crossfade (detik)", 0.1, 2.0, 1.0, 0.1)
loop_count = st.slider("🔁 Jumlah loop", 1, 10, 3)

if uploaded_file:
    # Simpan file sementara
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
        tmp_file.write(uploaded_file.read())
        video_path = tmp_file.name

    # Validasi durasi video
    clip = VideoFileClip(video_path)
    duration = clip.duration

    st.subheader("📽️ Preview Video Asli")
    st.video(video_path)
    st.info(f"Durasi video: **{duration:.2f} detik**")

    if duration < 4:
        st.error("❌ Video terlalu pendek! Minimal 4 detik diperlukan.")
    else:
        if st.button("🔄 Proses dan Buat Loop"):
            with st.spinner("Membuat video looping..."):
                with tempfile.TemporaryDirectory() as tmpdir:
                    output_path = os.path.join(tmpdir, "looped.mp4")

                    # Ambil 4 detik pertama
                    base_clip = clip.subclip(0, 4)

                    loop_clips = []
                    for i in range(loop_count):
                        if i == 0:
                            loop_clips.append(base_clip)
                        else:
                            loop_clips.append(base_clip.crossfadein(crossfade_duration))

                    final_clip = concatenate_videoclips(
                        loop_clips,
                        method="compose",
                        padding=-crossfade_duration
                    )

                    final_duration = final_clip.duration

                    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)

                    st.success("✅ Video looping berhasil dibuat!")
                    st.subheader("📼 Preview Video Looping")
                    st.video(output_path)
                    st.info(f"🎬 Durasi akhir hasil looping: **{final_duration:.2f} detik**")

                    with open(output_path, "rb") as f:
                        st.download_button("⬇️ Unduh Video", f, file_name="smooth_loop.mp4", mime="video/mp4")
