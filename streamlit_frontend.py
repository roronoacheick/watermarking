import io
import backend
import importlib
from pathlib import Path

import streamlit as st
from PIL import Image
import numpy as np

# Try to import the user's backend module (backend.py must be in the same folder)
# We'll import it as `backend` and access functions if present.
try:
    import backend as backend
    importlib.reload(backend)
    BACKEND_LOADED = True
except Exception as e:
    backend = None
    BACKEND_LOADED = False
    backend_import_error = e

st.set_page_config(page_title="Steganography — Encoder / Decoder", layout="centered")
st.title("Steganography — Encoder / Decoder (Streamlit frontend)")

st.markdown(
    """
    This frontend tries to use functions from your `backend.py` file (must be in the same folder).

    - Encoding uses `encode_lsb1(image_array, binary_message)` if available.
    - Decoding uses `decode_lsb1(image_array, message_length)` if available.
    - Conversion helpers `text_to_binary` / `binary_to_text` / `text_to_bits` are used when present.

    If those functions are not found in your backend, this app will fall back to its own (simple) implementations.
    """
)

# --------- Helpers (fallback implementations) ----------

def _pil_to_np(img: Image.Image) -> np.ndarray:
    return np.array(img.convert('RGB'))


def _np_to_pil(arr: np.ndarray) -> Image.Image:
    arr = np.clip(arr, 0, 255).astype('uint8')
    return Image.fromarray(arr)


def fallback_text_to_binary(text: str) -> str:
    # convert to bytes (utf-8) then to bitstring
    return ''.join(f"{b:08b}" for b in text.encode('utf-8'))


def fallback_binary_to_text(bits: str) -> str:
    # split into bytes and decode utf-8
    bytes_list = [int(bits[i:i+8], 2) for i in range(0, len(bits), 8)]
    try:
        return bytes(bytes_list).decode('utf-8', errors='replace')
    except Exception:
        return ''.join(chr(b) for b in bytes_list)


def fallback_encode_lsb1(image_array: np.ndarray, binary_message: str) -> np.ndarray:
    """Encode binary_message (string of '0'/'1') into least-significant bit of image_array (RGB).
    Simple LSB across pixels in row-major order, using R,G,B channels.
    Returns new image array (copy).
    """
    h, w, c = image_array.shape
    if c < 3:
        raise ValueError('Image must have at least 3 channels (RGB).')

    flat = image_array.flatten()
    needed_bits = len(binary_message)
    available_bits = flat.size
    if needed_bits > available_bits:
        raise ValueError(f'Message too long to encode: need {needed_bits} bits, have {available_bits} bits')

    out = flat.copy()
    for i, bit in enumerate(binary_message):
        out[i] = (out[i] & ~1) | int(bit)

    out = out.reshape(image_array.shape)
    return out


def fallback_decode_lsb1(image_array: np.ndarray, message_length_chars: int) -> str:
    bits_needed = message_length_chars * 8
    flat = image_array.flatten()
    bits = ''.join(str(int(flat[i] & 1)) for i in range(bits_needed))
    return fallback_binary_to_text(bits)


# --------- UI ----------

col1, col2 = st.columns([1, 2])
with col1:
    uploaded = st.file_uploader("Upload an image (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
    st.write("\n")
    mode = st.radio("Mode", ["Encode", "Decode"])  

with col2:
    if BACKEND_LOADED:
        st.success('backend.py loaded successfully')
    else:
        st.error('Could not import backend.py in this folder')
        st.caption(str(backend_import_error))

    st.markdown("**Options**")
    use_backend_funcs = st.checkbox("Prefer backend functions when available", value=True)


if uploaded is not None:
    try:
        image = Image.open(uploaded).convert('RGB')
    except Exception as e:
        st.error('Cannot open image file: ' + str(e))
        st.stop()

    st.image(image, caption='Original image', use_column_width=True)
    img_arr = _pil_to_np(image)

    if mode == 'Encode':
        message = st.text_area('Message to hide', height=150)
        st.caption('Tip: short messages are easier to encode and test')

        if st.button('Encode'):
            if message.strip() == '':
                st.warning('Please enter a message to encode')
            else:
                # prepare binary using backend or fallback
                try:
                    if use_backend_funcs and BACKEND_LOADED and hasattr(backend, 'text_to_binary'):
                        binary = backend.text_to_binary(message)
                    else:
                        binary = fallback_text_to_binary(message)

                    # call encode function
                    if use_backend_funcs and BACKEND_LOADED and hasattr(backend, 'encode_lsb1'):
                        # backend likely expects a numpy array and binary string
                        encoded_arr = backend.encode_lsb1(img_arr.copy(), binary)
                    else:
                        encoded_arr = fallback_encode_lsb1(img_arr.copy(), binary)

                    encoded_img = _np_to_pil(encoded_arr)

                    st.image(encoded_img, caption='Encoded image (result)', use_column_width=True)

                    # provide download
                    buf = io.BytesIO()
                    encoded_img.save(buf, format='PNG')
                    buf.seek(0)
                    st.download_button('Download encoded image (PNG)', data=buf, file_name='encoded.png', mime='image/png')

                except Exception as e:
                    st.error(f'Encoding failed: {e}')

    else:  # Decode
        st.caption('If you know the message length (in characters), provide it for a reliable decode.')
        message_len = st.number_input('Message length (characters) — optional', min_value=0, value=0)

        if st.button('Decode'):
            try:
                if use_backend_funcs and BACKEND_LOADED and hasattr(backend, 'decode_lsb1') and message_len > 0:
                    decoded = backend.decode_lsb1(img_arr.copy(), int(message_len))
                elif use_backend_funcs and BACKEND_LOADED and hasattr(backend, 'decode_lsb1') and hasattr(backend, 'binary_to_text') and message_len > 0:
                    decoded_bits = backend.decode_lsb1(img_arr.copy(), int(message_len))
                    decoded = backend.binary_to_text(decoded_bits)
                else:
                    if message_len <= 0:
                        st.warning('Please provide the approximate message length (in characters) or use a backend that can infer it.')
                        decoded = None
                    else:
                        decoded = fallback_decode_lsb1(img_arr.copy(), int(message_len))

                if decoded is not None:
                    st.subheader('Decoded message')
                    st.code(decoded)
            except Exception as e:
                st.error(f'Decoding failed: {e}')

else:
    st.info('Upload an image to get started.')


st.markdown('---')
st.markdown('**Developer notes**')
st.markdown(
    '- Put this file (`streamlit_frontend.py`) in the same folder as your `backend.py` and run: `streamlit run streamlit_frontend.py`\n'
    '- This frontend prefers to call functions from `backend.py` if they exist: `text_to_binary`, `binary_to_text`, `encode_lsb1`, `decode_lsb1`.\n'
    "- If your backend uses different function names or signatures, either adapt `backend.py` or edit this frontend to match."
)
