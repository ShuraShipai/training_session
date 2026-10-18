"""Independent Streamlit interface for the original rembg implementation."""
from io import BytesIO
import hashlib

import streamlit as st
from PIL import Image
from rembg import remove

st.set_page_config(page_title="Background Removal", page_icon="🖼️")
st.title("Background Removal")
st.write("Upload an image, remove its background, and download a transparent PNG.")

upload = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg", "webp"])
if upload is not None:
    try:
        original_bytes = upload.getvalue()
        with Image.open(BytesIO(original_bytes)) as image:
            image.load()
            st.image(image, caption="Original image", use_container_width=True)
    except Exception as exc:
        st.error(f"Could not open this image: {exc}")
        st.stop()

    image_key = hashlib.sha256(original_bytes).hexdigest()
    if st.button("Remove background", type="primary"):
        try:
            with st.spinner("Removing background…"):
                result = remove(original_bytes)
            st.session_state["background_result"] = (image_key, result)
        except Exception as exc:
            st.error(f"Background removal failed: {exc}")

    result = st.session_state.get("background_result")
    if result and result[0] == image_key:
        st.image(result[1], caption="Transparent result (checkerboard preview may vary)", use_container_width=True)
        st.download_button("Download PNG", result[1], "background-removed.png", "image/png")
