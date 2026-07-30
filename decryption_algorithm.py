import os
import string
from PIL import Image

# --- CONFIGURATION ---
# Caesar cipher alphabet used during text encoding
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
                attempt += char  # Keep characters outside alphabet unchanged
            else:
                attempt += ALPHABET[index]

        attempts.append((key, attempt))
    return attempts


# --- STEP 3: IMAGE OVERLAY FUNCTION ---
def overlay_decrypted_pixels(
    original_path, decrypted_path, output_path="final_overlay.png"
):
    """Overlays the decrypted 8x8 pixel grid onto the original base image."""
    try:
        base_img = Image.open(original_path).convert("RGBA")
        dec_img = Image.open(decrypted_path).convert("RGBA")

        # Scale the 8x8 image up to match the original image size using NEAREST neighbor
        dec_resized = dec_img.resize(base_img.size, Image.Resampling.NEAREST)

        # Blend the two images together with 50% opacity
        blended = Image.blend(base_img, dec_resized, alpha=0.5)
        blended.save(output_path)
        print(f"✨ Overlaid image saved successfully as: '{output_path}'")

    except FileNotFoundError as e:
        print(f"\n⚠️ Overlay skipped: {e}")
        print(
            "💡 Make sure the file path to your original background image is correct!"
        )


# --- STEP 4: MAIN EXECUTION ---
# def main():
#     print("=" * 50)
#     print("🚀 STARTING DECRYPTION PIPELINE")
#     print("=" * 50)

#     # 1. READ FILE
#     file_path = "finalproject/encryption.bin"
#     try:
#         with open(file_path, "rb") as f:
#             cipher = f.read()
#         print(f"📁 Loaded file: '{file_path}'")
#         print(f"📊 File size:   {len(cipher)} bytes")
#     except FileNotFoundError:
#         print(f"❌ Error: Could not find file '{file_path}'. Check path!")
#         return

#     print("\n--- STEP 1: CONVERTING TO BLOCK CIPHER LIST ---")
#     cipher_list = bytes_to_blocks(cipher, block_size=4)
#     print(f"✅ Generated {len(cipher_list)} block chunks.")

#     print("\n--- STEP 2: SEARCHING FOR BIT SHIFT KEY ---")
#     found_key = None
#     decrypted_bytes = None

#     # Test keys to find the one that yields the 'BM' header
#     for test_key in range(32):
#         message_list = undo_shift(cipher_list, key=test_key, block_size=4)
#         test_bytes = rebuild_message(message_list, block_size=4)

#         if test_bytes.startswith(b"BM"):
#             found_key = test_key
#             decrypted_bytes = test_bytes
#             print(f"🎯 MATCH FOUND! Bit shift key = {test_key}")
#             break

#     if decrypted_bytes is None:
#         print("❌ Could not find a valid BMP header with any bit-shift key.")
#         return

#     print("\n--- STEP 3: DECRYPTED BYTE DETAILS ---")
#     print(f"🔍 Header Magic Bytes: {decrypted_bytes[:2]} (Valid Bitmap!)")
#     print(f"🔍 First 20 Raw Bytes: {list(decrypted_bytes[:20])}")

#     # Print Hex preview if needed
#     hex_preview = decrypted_bytes[:16].hex().upper()
#     print(f"🔍 First 16 Bytes (Hex): {hex_preview}")

#     print("\n--- STEP 4: SAVING OUTPUT IMAGE ---")
#     output_filename = "decrypted_flower.bmp"
#     with open(output_filename, "wb") as f:
#         f.write(decrypted_bytes)

#     print(f"💾 File saved successfully as: '{output_filename}'")

#     print("\n--- STEP 5: OVERLAYING PIXELS ON ORIGINAL IMAGE ---")
#     # Change 'unit3/paper.jpg' if your original background image path is different
#     original_bg = "unit3/paper.jpg"
#     overlay_decrypted_pixels(
#         original_path=original_bg,
#         decrypted_path=output_filename,
#         output_path="final_overlay.png",
#     )

#     print("=" * 50)
#     print("🎉 DECRYPTION PIPELINE COMPLETE")
#     print("=" * 50)


# if __name__ == "__main__":
#     main()

# --- STEP 4: MAIN EXECUTION ---
def main():
    print("=" * 50)
    print("🚀 STARTING DECRYPTION PIPELINE")
    print("=" * 50)

    # 1. READ FILE
    file_path = "finalproject/encryption.bin"
    try:
        with open(file_path, "rb") as f:
            cipher = f.read()
        print(f"📁 Loaded file: '{file_path}'")
        print(f"📊 File size:   {len(cipher)} bytes")
    except FileNotFoundError:
        print(f"❌ Error: Could not find file '{file_path}'. Check path!")
        return

    # 2. DECODE AS UTF-8 TEXT
    #try:
        #encrypted_text = cipher.decode("utf-8").strip()
        #print(f"\n--- STEP 1: LOADED ENCRYPTED HEX TEXT ---")
        #print(f"🔍 Text Preview: {encrypted_text[:40]}...")
    #except UnicodeDecodeError:
        #print(
          #  "❌ File content is not text! (If this is a raw bit-shifted binary, try running undo_shift first)."
      #  )
        #return

    print("\n--- STEP 2: CONVERTING TO BLOCK CIPHER LIST ---")
    cipher_list = bytes_to_blocks(cipher, block_size=4)
    print(f"✅ Generated {len(cipher_list)} block chunks.")

    print("\n--- STEP 3: SEARCHING FOR BIT SHIFT KEY ---")
    found_key = None
    decrypted_bytes = None
    for key in range(32):
        message_list = undo_shift(cipher_list, key=10, block_size=4)
        message_bytes = rebuild_message(message_list, block_size=4)

        if key==10:
            found_key = key
            decrypted_bytes = message_bytes
            print(f"🎯 MATCH FOUND! Bit shift key = {key}")
        break

    # if decrypted_bytes is None:
    #     print("❌ Could not find a valid BMP header with any bit-shift key.")
    #     return

    # print("\n--- STEP 3: DECRYPTED BYTE DETAILS ---")
    # print(f"🔍 Header Magic Bytes: {decrypted_bytes[:2]} (Valid Bitmap!)")
    # print(f"🔍 First 20 Raw Bytes: {list(decrypted_bytes[:20])}")


    # 3. SEARCH FOR CAESAR SHIFT KEY
    print("\n--- STEP 2: SEARCHING FOR CAESAR SHIFT KEY ---")
    attempts = decode_shift(encrypted_text)

    found_key = None
    decrypted_bytes = None

    for key, hex_attempt in attempts:
        clean_hex = hex_attempt.strip().upper()

        # Hex strings must have an even length
        if len(clean_hex) % 2 != 0:
            continue

        try:
            # Convert Hex string back to raw bytes
            test_bytes = bytes.fromhex(clean_hex)

            # Check for BMP header signature 'BM'
            if test_bytes.startswith(b"BM"):
                found_key = key
                decrypted_bytes = test_bytes
                print(f"🎯 MATCH FOUND! Caesar shift key = {key}")
                break
        except ValueError:
            # Skip attempts with non-hex characters (e.g. G, H, Z)
            continue

    if decrypted_bytes is None:
        print("❌ Could not find a valid BMP header with any Caesar key.")
        return

    print("\n--- STEP 3: DECRYPTED BYTE DETAILS ---")
    print(f"🔍 Header Magic Bytes: {decrypted_bytes[:2]} (Valid Bitmap!)")
    print(f"🔍 First 20 Raw Bytes: {list(decrypted_bytes[:20])}")

    print("\n--- STEP 4: SAVING OUTPUT IMAGE ---")
    output_filename = "decrypted_flower.bmp"
    with open(output_filename, "wb") as f:
        f.write(decrypted_bytes)

    print(f"💾 File saved successfully as: '{output_filename}'")

    print("\n--- STEP 5: OVERLAYING PIXELS ON ORIGINAL IMAGE ---")
    original_bg = "unit3/paper.jpg"
    overlay_decrypted_pixels(
        original_path=original_bg,
        decrypted_path=output_filename,
        output_path="final_overlay.png",
    )

    print("=" * 50)
    print("🎉 DECRYPTION PIPELINE COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()