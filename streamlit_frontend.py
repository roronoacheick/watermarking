import io
import streamlit as st
from PIL import Image
import numpy as np
import backend  

st.set_page_config(page_title="Steganography", layout="centered")
st.title("Steganography — Simple Encoder / Decoder")

# --- Helpers ---
def pil_to_np(img):
    return np.array(img.convert('RGB'))

def np_to_pil(arr):
    return Image.fromarray(arr.astype('uint8'))

# --- UI ---
uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
mode = st.radio("Mode", ["Encode", "Decode"], horizontal=True)

if uploaded:
    img = Image.open(uploaded).convert('RGB')
    arr = pil_to_np(img)

    st.image(img, caption="Image loaded", use_column_width=True)

    if mode == "Encode":
        message = st.text_area("Message to hide")
        if st.button("Encode message"):
            binary = backend.text_to_binary(message)
            encoded = backend.encode_lsb1(arr.copy(), binary)
            encoded_img = np_to_pil(encoded)

            st.image(encoded_img, caption="Encoded image", use_column_width=True)

            buf = io.BytesIO()
            encoded_img.save(buf, format="PNG")
            st.download_button("Download encoded image", buf.getvalue(), "encoded.png", "image/png")

    else:  # Decode
        length = st.number_input("Message length (characters)", min_value=1, step=1)
        if st.button("Decode message"):
            decoded_bits = backend.decode_lsb1(arr.copy(), int(length))
            text = backend.binary_to_text(decoded_bits)
            st.code(text)
else:
    st.info("Upload an image to begin.")