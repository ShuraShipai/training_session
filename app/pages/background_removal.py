import hashlib
import streamlit as st
from app.components.services import read_image, remove_background

st.title("Background Removal")
st.write("Upload a photo and download the subject on a transparent background.")
upload = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg", "webp"], key="bg_upload")
st.caption("Up to 10 MB and 12 megapixels. The first removal may take longer while the model loads.")
if upload is not None:
    data = upload.getvalue()
    key = hashlib.sha256(data).hexdigest()
    try:
        original = read_image(data)
    except Exception:
        st.error("This image could not be opened. Choose a valid image within the size limits.")
        st.stop()
    left, right = st.columns(2)
    with left:
        st.subheader("Original")
        st.image(original, width="stretch")
    if st.button("Remove background", type="primary"):
        st.session_state.pop("bg_result", None)
        try:
            with st.spinner("Removing the background…"):
                st.session_state.bg_result = (key, remove_background(data))
        except Exception:
            st.error("Background removal is unavailable. Check the server's rembg installation and model access, then retry.")
    result = st.session_state.get("bg_result")
    if result and result[0] == key:
        with right:
            st.subheader("Transparent result")
            st.image(result[1], width="stretch")
            st.download_button("Download PNG", result[1], "output.png", "image/png", on_click="ignore")
