
import os
import string
import io
from PIL import Image

# --- CONFIGURATION ---
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"


# --- STEP 1: BITWISE & BLOCK UN-SHIFT FUNCTIONS ---
def bytes_to_blocks(data, block_size=4):
    """Converts raw binary byte stream into 32-bit integer blocks."""
    blocks = []
    for i in range(0, len(data), block_size):
        chunk = 0
        for b in data[i : i + block_size]:
            chunk = (chunk << 8) | b
        blocks.append(chunk)
    return blocks


def undo_shift(cipher_list, key, block_size=4):
    """Reverses bitwise block rotations."""
    message_list = []
    bit_max = block_size * 8
    mask = (1 << bit_max) - 1

    for chunk in cipher_list:
        number = ((chunk << key) & mask) | (chunk >> (bit_max - key))
        message_list.append(number)

    return message_list


def rebuild_message(message_list, block_size=4):
    """Reconstructs byte array from block list."""
    message = bytearray()
    for chunk in message_list:
        for j in range(block_size):
            number = (chunk >> (8 * (block_size - 1 - j))) % 256
            message.append(number)
    return bytes(message)


# --- STEP 2: CAESAR SHIFT DECODER ---
def decode_shift(encrypted_text):
    """Generates all 36 possible Caesar shift decoded variations."""
    attempts = []
    for key in range(len(ALPHABET)):
        shifted = ALPHABET[key:] + ALPHABET[:key]
        attempt = ""

        for char in encrypted_text:
            index = shifted.find(char)
            if index == -1:
                attempt += char
            else:
                attempt += ALPHABET[index]

        attempts.append((key, attempt))
    return attempts


# --- STEP 3: CONVERT DECRYPTED STRING TO IMAGE & OVERLAY ---
def overlay_string_data_on_image(
    text_data, original_path, output_path="final_overlay.png"
):
    """Converts the decrypted text payload into pixel bytes and overlays it on the flower image."""
    try:
        # Filter text to valid hex digits (A-F, 0-9)
        hex_digits = "0123456789ABCDEF"
        clean_hex = "".join([c for c in text_data.upper() if c in hex_digits])

        if len(clean_hex) % 2 != 0:
            clean_hex = clean_hex[:-1]

        raw_bytes = bytes.fromhex(clean_hex)

        # Try opening raw_bytes directly or building a bitmap
        try:
            dec_img = Image.open(io.BytesIO(raw_bytes)).convert("RGBA")
        except Exception:
            # If standard header is missing, map raw bytes onto a pixel grid
            grid_size = int((len(raw_bytes) // 3) ** 0.5) or 8
            dec_img = Image.frombytes(
                "RGB", (grid_size, grid_size), raw_bytes
            ).convert("RGBA")

        base_img = Image.open(original_path).convert("RGBA")

        # Handle resampling safely across older and newer Pillow versions
        resample_mode = getattr(
            getattr(Image, "Resampling", Image), "NEAREST", Image.NEAREST
        )

        # Resize decrypted pixel grid to cover original image
        dec_resized = dec_img.resize(base_img.size, resample_mode)

        # Blend images together (50% transparency overlay)
        blended = Image.blend(base_img, dec_resized, alpha=0.5)
        blended.save(output_path)
        print(f"✨ Overlaid image saved successfully as: '{output_path}'")

    except Exception as e:
        print(f"⚠️ Overlay error: {e}")


# --- STEP 4: MAIN EXECUTION ---
def main():
    print("=" * 50)
    print("🚀 STARTING DECRYPTION PIPELINE")
    print("=" * 50)

    # 1. READ FILE
    file_path = "encryption.bin"
    try:
        with open(file_path, "rb") as f:
            cipher = f.read()
        print(f"📁 Loaded file: '{file_path}'")
        print(f"📊 File size:   {len(cipher)} bytes")
    except FileNotFoundError:
        print(f"❌ Error: Could not find file '{file_path}'. Check path!")
        return

    print("\n--- STEP 1: CONVERTING TO BLOCK CIPHER LIST ---")
    cipher_list = bytes_to_blocks(cipher, block_size=4)
    print(f"✅ Generated {len(cipher_list)} block chunks.")

    print(
        "\n--- STEP 2: SEARCHING FOR BIT SHIFT & CAESAR KEYS (HEADER = 'C') ---"
    )
    found_bit_key = None
    found_caesar_key = None
    decrypted_text_result = None

    for bit_key in range(32):
        message_list = undo_shift(cipher_list, key=bit_key, block_size=4)
        bit_decrypted_bytes = rebuild_message(message_list, block_size=4)

        try:
            encrypted_text = bit_decrypted_bytes.decode("utf-8").strip()
        except UnicodeDecodeError:
            continue

        attempts = decode_shift(encrypted_text)

        for caesar_key, attempt_text in attempts:
            if attempt_text.startswith("C"):
                found_bit_key = bit_key
                found_caesar_key = caesar_key
                decrypted_text_result = attempt_text
                print(
                    f"🎯 MATCH FOUND! Bit Key = {bit_key} | Caesar Key = {caesar_key}"
                )
                break

        if decrypted_text_result:
            break

    if decrypted_text_result is None:
        print("❌ Could not find a decrypted text string starting with 'C'.")
        return

    print("\n--- STEP 3: DECRYPTED DETAILS ---")
    print(
        f"🔍 Decrypted Text Preview: {decrypted_text_result[:80]}...\n[Truncated]"
    )

    print("\n--- STEP 4: SAVING DECRYPTED TEXT ---")
    txt_filename = "decrypted_message.txt"
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(decrypted_text_result)
    print(f"💾 Text output saved as: '{txt_filename}'")

    print("\n--- STEP 5: OVERLAYING PIXELS ON FLOWER IMAGE ---")
    original_bg = "flower.jpg"
    overlay_string_data_on_image(
        text_data=decrypted_text_result,
        original_path=original_bg,
        output_path="final_overlay.png",
    )

    print("=" * 50)
    print("🎉 DECRYPTION PIPELINE COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()
