# BMP Binary Analyzer

A Python GUI application for analyzing BMP image files at the binary level. This tool allows you to load BMP files, view their binary representation, and understand the internal structure of the image format.

## Features

- **Load BMP Files**: Open and read BMP format image files
- **Image Preview**: Visual preview of the loaded BMP image with dimensions and color mode information
- **Binary Display**: View the binary data in a hex editor format with addresses and ASCII representation
- **Structure Analysis**: Automatically identifies and highlights different sections of the BMP file:
  - BMP Header (file signature, size, offsets)
  - DIB Header (image metadata: width, height, color depth, etc.)
  - Color Palette (if present)
  - Pixel Data
  - Padding
  - End Marker
- **Color-Coded Highlighting**: Different sections are highlighted with distinct colors for easy identification
- **Legend**: Visual legend explaining what each color represents
- **Preview Binary Data**: Preview the image from modified binary data in the text box before exporting
- **Export Functionality**: Export the binary data from the text box back to a BMP image file
- **Steganography**: Embed strings into pixel data by replacing random bytes
  - Enter a string and embed it into the pixel data
  - Positions are saved in the same order as characters in the string
  - Replaced bytes are highlighted in light pink
  - Save positions to ADR file (named "photo_name.adr")
  - Load ADR file to extract the hidden string (maintains character order)

## Requirements

- Python 3.6 or higher
- tkinter (usually included with Python)
- Pillow>=9.0.0
- Pillow (PIL) - Install with: `pip install Pillow`

## Usage

1. Run the program:
   ```bash
   python bmp_analyzer.py
   ```

2. Click "Load BMP File" to select a BMP image file

3. The image preview will appear in the top panel showing the loaded image with its dimensions and color mode

4. The binary data will be displayed in the text box below with color-coded sections:
   - **Light Red**: BMP Header (first 14 bytes)
   - **Light Blue**: DIB Header (image information)
   - **Light Green**: Color Palette (if present)
   - **Light Yellow**: Pixel Data
   - **Light Gray**: Padding
   - **Light Pink**: End Marker / Replaced Bytes (steganography)

5. **Edit and Preview**: You can modify the binary data in the text box (edit hex values), then click "Preview Binary Data" to see how the modified image looks

6. **Steganography Features**:
   - Enter a string in the "Enter string to hide" text box
   - Click "Embed String in Pixel Data" to replace random bytes in the pixel data
   - Positions are saved in the same order as the characters in your string
   - Replaced bytes will be highlighted in light pink
   - Click "Save Positions to ADR File" to save the positions (file will be named "photo_name.adr")
   - To extract: Load the modified BMP file, click "Load ADR File and Extract", select the ADR file
   - The extracted string will appear in the "Extracted string" read-only text box in the correct order

7. To export the binary data back to an image:
   - Click "Export Binary to Image"
   - Choose a location to save the file
   - The binary data from the text box will be written to a new BMP file

## BMP File Structure

The application parses the following BMP structure:

- **BMP Header (14 bytes)**: Contains file signature ("BM"), file size, reserved fields, and offset to pixel data
- **DIB Header (varies)**: Contains image dimensions, color depth, compression method, and other metadata
- **Color Palette (optional)**: Present in indexed color images (1, 4, or 8 bits per pixel)
- **Pixel Data**: The actual image pixel information
- **Padding/End Marker**: Any additional data at the end of the file

## Notes

- The application works best with standard BMP files (BITMAPINFOHEADER format)
- Large BMP files may take a moment to load and display
- The binary display shows 16 bytes per line in hexadecimal format
- You can edit the binary data in the text box and use "Preview Binary Data" to see the result before exporting
- Invalid or corrupted binary data will show an error when previewing or exporting
- **Steganography**: The string embedding feature replaces random bytes in pixel data. The image may have slight visual changes, but the changes are usually imperceptible. Make sure to save the ADR file to recover the hidden message later.

