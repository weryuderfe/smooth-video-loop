import streamlit as st
from moviepy.editor import VideoFileClip, concatenate_videoclips
import tempfile
import os
import gdown

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
    clip = VideoFileClip(input_path)
    clip_duration = clip.duration

    # Trimming
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
        clip = VideoFileClip(input_path)
        st.success("✅ Video berhasil diunggah langsung.")
        st.video(input_path)

elif gdrive_url:
    st.info("⬇️ Mengunduh video dari Google Drive...")
    try:
        input_path = download_from_gdrive(gdrive_url)
        clip = VideoFileClip(input_path)
        st.success("✅ Video berhasil diunduh dari Google Drive.")
        st.video(input_path)
    except Exception as e:
        st.error(f"❌ Gagal mengunduh video: {e}")

# Hentikan jika belum ada video
if not input_path or not clip:
    st.warning("⚠️ Harap upload video atau masukkan link Google Drive terlebih dahulu.")
    st.stop()

# Durasi dan opsi trimming
st.subheader("✂️ Potong Durasi Video")
st.info(f"Durasi video asli: {clip.duration:.2f} detik")

trim_start = st.number_input("Mulai dari detik", min_value=0.0, max_value=clip.duration, value=0.0)
trim_end = st.number_input("Akhiri pada detik", min_value=trim_start + 0.1, max_value=clip.duration, value=clip.duration)

# Opsi looping
st.subheader("🔁 Pengaturan Looping")
loop_count = st.number_input("Jumlah loop", min_value=1, max_value=10, value=3)
fade_duration = st.slider("Durasi transisi halus (detik)", 0.01, 0.5, 0.1, 0.01)
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
