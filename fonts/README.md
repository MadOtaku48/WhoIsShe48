# Korean/CJK Fonts for AKB48 Face Classifier

This directory contains TrueType and OpenType fonts that support Korean, Japanese, and Chinese (CJK) characters, tested and verified to work with PIL/Pillow.

## Available Fonts

### 1. NotoSansCJK-Regular.ttc
- **Type**: OpenType Font Collection (TTC)
- **Size**: 19MB
- **Description**: Google's Noto Sans CJK font collection containing multiple CJK variants
- **Coverage**: Full CJK support (Korean, Japanese, Chinese)

### 2. NotoSansCJKkr-VF.ttf
- **Type**: TrueType Variable Font
- **Size**: 34MB
- **Description**: Variable font version of Noto Sans CJK Korean
- **Coverage**: Optimized for Korean, supports Japanese and Chinese

### 3. NotoSansCJKkr-Regular.otf
- **Type**: OpenType Font
- **Size**: 16MB
- **Description**: Regular weight Noto Sans CJK Korean
- **Coverage**: Optimized for Korean, supports Japanese and Chinese

### 4. NotoSansCJKkr-Bold.otf
- **Type**: OpenType Font
- **Size**: 16MB
- **Description**: Bold weight Noto Sans CJK Korean
- **Coverage**: Optimized for Korean, supports Japanese and Chinese

## Usage with PIL/Pillow

```python
from PIL import Image, ImageDraw, ImageFont

# Load a font
font = ImageFont.truetype('fonts/NotoSansCJKkr-Regular.otf', 40)

# Create an image and draw text
img = Image.new('RGB', (800, 200), color='white')
draw = ImageDraw.Draw(img)
draw.text((50, 50), "한글 Korean 日本語", font=font, fill='black')
img.save('output.png')
```

## Font Sources

All fonts were downloaded from official Google Fonts repositories:
- Noto Sans CJK: https://github.com/googlefonts/noto-cjk

## Testing

Run `test_fonts.py` to verify font functionality:
```bash
python test_fonts.py
```

This will generate test images for each font showing Korean, English, and Japanese text rendering.