import ast
# Manual fix for Python 3.14 compatibility
if not hasattr(ast, 'Str'):
    ast.Str = ast.Constant

import easyocr
import cv2
from aksharamukha import transliterate
import matplotlib.pyplot as plt
import os
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

def start_project():
    # --- CONFIGURATION ---
    image_name = input("Enter the image filename (e.g., mysign.png): ") # Ensure your image is named test.jpg in the same folder
    
    if not os.path.exists(image_name):
        print(f"\n[!] Error: {image_name} not found. Please place the image in the project folder.")
        return

    # --- CLEAN TERMINAL HEADER ---
    print("\n" + "="*40)
    print("      BHARAT SIGNBOARD AI TOOL")
    print("="*40)
    
    # --- CHOOSE LANGUAGE ---
    print("\nCHOOSE LANGUAGE:")
    print("1. Tamil      2. Telugu      3. Kannada")
    print("4. Malayalam  5. Bengali     6. Gujarati")
    print("7. Gurmukhi   8. Hindi       9. ISO (English)")
    
    choice = input("\nEnter choice (1-9): ")
    
    lang_map = {
        "1": "Tamil", "2": "Telugu", "3": "Kannada",
        "4": "Malayalam", "5": "Bengali", "6": "Gujarati",
        "7": "Gurmukhi", "8": "Devanagari", "9": "ISO"
    }
    
    target_lang = lang_map.get(choice, "Tamil")
    
    # --- IMAGE ENHANCEMENT OPTION ---
    enhance = input("Enhance Image Quality? (y/n): ").lower()

    print(f"\n[1/3] Initializing AI Engine for {target_lang}...")
    reader = easyocr.Reader(['hi', 'en'])

    # --- IMAGE PROCESSING ---
    print("[2/3] Processing Signboard...")
    img = cv2.imread(image_name)
    
    if enhance == 'y':
        # Apply slight brightness and sharpening as done in App.py
        img = cv2.convertScaleAbs(img, alpha=1.2, beta=20)
        img = cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)
        
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # --- OCR & TRANSLITERATION ---
    print("[3/3] Generating Results...")
    results = reader.readtext(img)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(img_rgb)
    
    found_any = False
    for (bbox, text, prob) in results:
        if prob > 0.15:
            found_any = True
            try:
                # Transliterate from Devanagari (Hindi) to chosen language
                trans_text = transliterate.process('Devanagari', target_lang, text)
            except:
                trans_text = text
            
            print(f" Detected: {text} -> {target_lang}: {trans_text}")

            # Draw Labels (Modern Blue Badge Style)
            top_left = tuple(map(int, bbox[0]))
            ax.text(top_left[0], top_left[1]-20, trans_text, 
                    fontsize=16, color='white', fontweight='bold', 
                    family='Nirmala UI', 
                    bbox=dict(facecolor='#3b82f6', alpha=0.9, edgecolor='none', boxstyle='round,pad=0.5'))
            
            # Draw Green Detection Box
            rect = plt.Rectangle(top_left, bbox[2][0]-bbox[0][0], bbox[2][1]-bbox[0][1], 
                                 fill=False, edgecolor='#10b981', linewidth=4)
            ax.add_patch(rect)

    ax.axis('off')
    plt.title(f"Bharat Sign AI: Transliterated to {target_lang}", fontsize=14, pad=20)
    
    if found_any:
        print("\nProcess Complete. Displaying image...")
        plt.show()
    else:
        print("\n[!] No text detected on the signboard.")

if __name__ == "__main__":
    start_project()
