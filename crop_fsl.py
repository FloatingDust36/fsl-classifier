import fitz  # pymupdf
import os
from PIL import Image
import io

PDF_PATH = r"D:\FSL.pdf"
OUTPUT_DIR = r"D:\fsl-classifier\web\fsl_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Letters in grid order (5 columns, 5 rows + Z at bottom which we skip)
# J and Z are in the chart but we exclude them
LETTERS = [
    "A",
    "B",
    "C",
    "D",
    "E",  # row 1
    "F",
    "G",
    "H",
    "I",
    None,  # row 2 — None = J, skip
    "K",
    "L",
    "M",
    "N",
    "O",  # row 3
    "P",
    "Q",
    "R",
    "S",
    "T",  # row 4
    "U",
    "V",
    "W",
    "X",
    "Y",  # row 5
]

# Render PDF page at high resolution
doc = fitz.open(PDF_PATH)
page = doc[0]
mat = fitz.Matrix(4, 4)  # 4x zoom — high resolution
pix = page.get_pixmap(matrix=mat)

img_width = pix.width
img_height = pix.height
print(f"Rendered image size: {img_width} x {img_height}")

img_data = pix.tobytes("png")
img = Image.open(io.BytesIO(img_data))

# Grid boundaries — approximate, we'll verify after first run
# The chart has a header at top and footer at bottom
# Columns: 5, Rows: 5 (we skip the Z row at bottom)
LEFT_MARGIN = 0.01
RIGHT_MARGIN = 0.99
TOP_MARGIN = 0.10
BOTTOM_MARGIN = 0.82

col_width = (RIGHT_MARGIN - LEFT_MARGIN) / 5
row_height = (BOTTOM_MARGIN - TOP_MARGIN) / 5

for i, letter in enumerate(LETTERS):
    if letter is None:
        continue  # skip J

    row = i // 5
    col = i % 5

    x0 = int((LEFT_MARGIN + col * col_width) * img_width)
    y0 = int((TOP_MARGIN + row * row_height) * img_height)
    x1 = int((LEFT_MARGIN + (col + 1) * col_width) * img_width)
    y1 = int((TOP_MARGIN + (row + 1) * row_height) * img_height)

    # Crop using Pillow
    cropped = img.crop((x0, y0, x1, y1))

    out_path = os.path.join(OUTPUT_DIR, f"{letter}.png")
    cropped.save(out_path)
    print(f"Saved {letter}.png")

doc.close()
print("Done.")
