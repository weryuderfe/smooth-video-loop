import streamlit as st
from moviepy.editor import VideoFileClip, concatenate_videoclips
import tempfile
import os
import gdown
import ffmpeg

# --- Fungsi untuk membaca durasi akurat menggunakan ffmpeg ---
def get_accurate_duration(path):
    try:
        probe = ffmpeg.probe(path)
        return float(probe['format']['duration'])
    except Exception as e:
        return None

# --- Fungsi download dari Google Drive ---
def download_from_gdrive(gdrive_url_or_id):
    file_id = ""
    if "drive.google.com" in gdrive_url_or_id:
        if "id=" in gdrive_url_or_id:
            file_id = gdrive_url_or_id.split("id=")[-1]
        elif "/d/" in gdrive_url_or_id:
            file_id = gdrive_url_or_id.split("/d/")[1].split("/")[0]
    else:
        file_id = gdrive_url_or_id  # langsung ID

    output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    gdown.download(f"https://drive.google.com/uc?id={file_id}", output, quiet=False)
    return output

# --- Fungsi looping video ---
def create_loop_clip(clip, loop_count, transition_duration, reverse=False):
    clips = []
    for i in range(loop_count):
        loop_clip = clip if i % 2 == 0 else clip.fx(lambda c: c.reverse()) if reverse else clip
        if i == 0:
            clips.append(loop_clip)
        else:
            clips.append(loop_clip.crossfadein(transition_duration))
    final = concatenate_videoclips(clips, method="compose", padding=-transition_duration)
    return final

def create_smooth_loop(input_path, output_path, loop_count, transition_duration, trim_start, trim_end, reverse):
    clip = VideoFileClip(input_path, fps_source='fps')

    # Trimming
    clip_duration = clip.duration
    if trim_end > clip_duration:
        trim_end = clip_duration
    trimmed = clip.subclip(trim_start, trim_end)

    # Loop
    final_clip = create_loop_clip(trimmed, loop_count, transition_duration, reverse)
    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
    return output_path

# --- UI Streamlit ---
st.set_page_config(page_title="Smooth Video Loop Creator", layout="centered")
st.title("🔁 Smooth Video Loop Creator")
st.markdown("Buat video pendek dengan transisi halus, reverse loop, dan trimming. Bisa upload langsung atau dari Google Drive.")

# Opsi Upload
st.subheader("📥 Pilih Metode Upload Video")
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📂 Upload langsung (max ~200MB)", type=["mp4"])
with col2:
    gdrive_url = st.text_input("🔗 Atau masukkan Google Drive Share Link / File ID")

input_path = None
clip = None

# Proses upload
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_input:
        tmp_input.write(uploaded_file.read())
        input_path = tmp_input.name
        st.success("✅ Video berhasil diunggah langsung.")
        st.video(input_path)

elif gdrive_url:
    st.info("⬇️ Mengunduh video dari Google Drive...")
    try:
        input_path = download_from_gdrive(gdrive_url)
        st.success("✅ Video berhasil diunduh dari Google Drive.")
        st.video(input_path)
    except Exception as e:
        st.error(f"❌ Gagal mengunduh video: {e}")

# Hentikan jika belum ada video
if not input_path:
    st.warning("⚠️ Harap upload video atau masukkan link Google Drive terlebih dahulu.")
    st.stop()

# Ambil durasi akurat
real_duration = get_accurate_duration(input_path)
clip = VideoFileClip(input_path, fps_source='fps')

# --- Info Video ---
st.subheader("🎬 Informasi Video")
st.info(f"📏 Durasi video menurut moviepy: {clip.duration:.2f} detik")
if real_duration:
    st.info(f"🧠 Durasi akurat berdasarkan ffmpeg: {real_duration:.2f} detik")
st.info(f"🎞️ Info teknis: {clip.fps:.2f} fps, {clip.reader.nframes} frame")

# Durasi dan trimming
st.subheader("✂️ Potong Durasi Video")

min_trim = round(min(clip.duration - 0.01, 0.01), 2)
trim_start = st.number_input("Mulai dari detik", min_value=0.0, max_value=clip.duration, value=0.0)
trim_end = st.number_input(
    "Akhiri pada detik",
    min_value=trim_start + min_trim,
    max_value=clip.duration,
    value=clip.duration
)

# Opsi looping
st.subheader("🔁 Pengaturan Looping")
loop_count = st.number_input("Jumlah loop", min_value=1, max_value=10, value=3)
fade_duration = st.slider("Durasi transisi halus (detik)", 0.1, 2.0, 0.5, 0.1)
reverse_loop = st.checkbox("Gunakan efek bolak-balik (ping-pong)?", value=True)

# Tombol proses
if st.button("🚀 Proses dan Buat Video Loop"):
    with st.spinner("⏳ Memproses video..."):
        try:
            output_path = os.path.splitext(input_path)[0] + f"_looped_{loop_count}x.mp4"
            result = create_smooth_loop(
                input_path,
                output_path,
                loop_count,
                fade_duration,
                trim_start,
                trim_end,
                reverse_loop
            )
            st.success("✅ Video berhasil dibuat!")
            st.video(result)
            with open(result, "rb") as f:
                st.download_button("⬇️ Download Video", f, file_name=os.path.basename(result), mime="video/mp4")
        except Exception as e:
            st.error(f"❌ Gagal memproses video: {e}")
