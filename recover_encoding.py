import sys
import chardet
from ftfy import fix_text, fix_encoding

def try_recover_file(filepath):
    try:
        # Read raw bytes
        with open(filepath, 'rb') as f:
            raw_data = f.read()
            
        # Detect encoding
        result = chardet.detect(raw_data)
        detected_enc = result['encoding']
        confidence = result['confidence']
        print(f"Chardet detected encoding: {detected_enc} with confidence: {confidence}")
        
        # Try decoding with detected encoding
        if detected_enc:
            try:
                text = raw_data.decode(detected_enc)
                print("\n--- Decoded with detected encoding ---")
                # print(text[:500]) # Print snippet
            except Exception as e:
                print(f"Failed to decode with {detected_enc}: {e}")
        
        # Try ftfy to fix mojibake
        try:
            # Often, this kind of mojibake is UTF-8 read as Big5 and saved as UTF-8 again.
            # Let's try a few raw decodes first, but ftfy works on strings.
            # First, read as utf-8, ignoring errors, then let ftfy try.
            text_utf8 = raw_data.decode('utf-8', errors='replace')
            fixed_text = fix_text(text_utf8)
            
            with open('recovered_ftfy.md', 'w', encoding='utf-8') as f:
                f.write(fixed_text)
            print("\n--- Saved ftfy attempt to recovered_ftfy.md ---")
        except Exception as e:
            print(f"ftfy failed: {e}")

        # Brute force common Taiwanese double encodings
        encodings = ['utf-8', 'big5', 'gbk', 'cp950', 'cp1252', 'latin1']
        
        best_guess = ""
        max_valid_chars = 0
        
        for enc1 in encodings:
            try:
                text1 = raw_data.decode(enc1)
                # print(f"\nSuccessfully decoded directly with {enc1}")
                # Save it just in case
                with open(f'recovered_{enc1}.md', 'w', encoding='utf-8') as f:
                    f.write(text1)
                
                # Check for double encoding
                for enc2 in encodings:
                    if enc1 == enc2: continue
                    for enc3 in encodings:
                         if enc2 == enc3: continue
                         try:
                             # Example: utf-8 string -> encoded as latin1 -> decoded as big5
                             recovered = text1.encode(enc2).decode(enc3)
                             # Heuristic: looking for recognizable Chinese punctuation or common words
                             if '（' in recovered or '。' in recovered or '測試' in recovered or '功能' in recovered:
                                 print(f"Potential match found: Decode {enc1} -> Encode {enc2} -> Decode {enc3}")
                                 with open('recovered_best_guess.md', 'w', encoding='utf-8') as f:
                                     f.write(recovered)
                                 return
                         except:
                             pass
            except:
                pass

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    try_recover_file("主次項目定義.md")
