import streamlit as st
from moviepy.editor import VideoFileClip, concatenate_videoclips
import tempfile
import os

# Konfigurasi halaman
st.set_page_config(page_title="Pengulang Video Halus", layout="centered")
st.title("🔁 Pengulang Video Halus")
st.write("Unggah video berdurasi **minimal 4 detik**, dan aplikasi ini akan membuat video berulang (looping) dengan transisi yang halus menggunakan efek crossfade.")

# Upload video
uploaded_file = st.file_uploader("🎞️ Unggah video MP4 (durasi minimal 4 detik):", type=["mp4"])

# Atur jumlah pengulangan
loop_count = st.slider("🔁 Jumlah pengulangan", min_value=1, max_value=10, value=3)

if uploaded_file:
    # Simpan video ke file sementara
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
        tmp_file.write(uploaded_file.read())
        video_path = tmp_file.name

    # Ambil informasi durasi
    clip = VideoFileClip(video_path)
    duration = clip.duration

    # Tampilkan pratinjau video asli
    st.subheader("📽️ Pratinjau Video Asli")
    st.video(video_path)
    st.info(f"⏱️ Durasi video asli: **{duration:.2f} detik**")

    if duration < 4.0:
        st.error("❌ Durasi video kurang dari 4 detik. Silakan unggah video yang lebih panjang.")
    else:
        # Durasi crossfade otomatis disesuaikan dengan durasi video yang diunggah
        crossfade_duration = st.slider(
            "🎚️ Atur durasi transisi crossfade (dalam detik)",
            min_value=0.1,
            max_value=duration - 0.1,  # Durasi crossfade tidak boleh lebih panjang dari durasi video
            value=duration - 0.1,  # Set awal crossfade menjadi hampir maksimal
            step=0.1
        )

        if st.button("🔄 Proses dan Buat Video Looping"):
            with st.spinner("Sedang memproses video..."):
                with tempfile.TemporaryDirectory() as tmpdir:
                    output_path = os.path.join(tmpdir, "video_loop.mp4")

                    # Potong 4 detik pertama sebagai dasar pengulangan
                    base_clip = clip.subclip(0, 4)

                    # Buat daftar klip untuk digabung
                    loop_clips = []
                    for i in range(loop_count):
                        if i == 0:
                            loop_clips.append(base_clip)
                        else:
                            loop_clips.append(base_clip.crossfadein(crossfade_duration))

                    # Gabungkan dengan transisi
                    final_clip = concatenate_videoclips(
                        loop_clips,
                        method="compose",
                        padding=-crossfade_duration
                    )

                    # Simpan video hasil akhir
                    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)

                    final_duration = final_clip.duration
                    # Menampilkan durasi video hasil
                    st.success("✅ Video berhasil dibuat!")
                    st.subheader("📼 Pratinjau Video Hasil Looping")
                    st.video(output_path)
                    st.info(f"🎬 Durasi video hasil: **{final_duration:.2f} detik**")

                    # Menyediakan tombol unduh video
                    with open(output_path, "rb") as f:
                        st.download_button("⬇️ Unduh Video", f, file_name="video_loop.mp4", mime="video/mp4")
