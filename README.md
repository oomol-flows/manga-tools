# Manga Tools

A comprehensive manga file format conversion toolkit for the OOMOL platform that enables seamless conversion between different manga formats and provides advanced archiving capabilities.

## 🚀 What is Manga Tools?

Manga Tools is a collection of workflow blocks designed to help you work with digital manga files. Whether you're organizing your manga library, converting between formats, or extracting images for editing, this toolkit provides everything you need in an easy-to-use visual workflow interface.

## 📚 Supported Formats

- **CBZ** (Comic Book ZIP) - Most common digital comic format
- **CBR** (Comic Book RAR) - RAR-compressed comic format
- **EPUB** - Electronic publication format with metadata support
- **PDF** - Portable Document Format

## 🔧 Available Workflow Blocks

### Core Conversion Blocks

#### **Transform**
Convert any manga file from one format to another while preserving quality and metadata.
- **What it does**: Takes a manga file in any supported format and converts it to your desired output format
- **Use cases**: Converting CBR files to CBZ, creating PDFs from EPUB files, standardizing your collection
- **Metadata support**: Preserves and allows editing of title, author, and reading order information

#### **Archive Directory**
Create manga files from folders of images.
- **What it does**: Takes a folder containing image files and packages them into a manga archive
- **Use cases**: Creating digital manga from scanned pages, organizing loose image collections
- **Supported image formats**: JPEG, PNG, GIF, WebP, BMP, TIFF, AVIF

#### **Unarchive to Images**
Extract all pages from manga files as individual image files.
- **What it does**: Opens manga archives and saves each page as a separate image file
- **Use cases**: Extracting artwork, preparing for editing, converting to other formats
- **Smart organization**: Maintains reading order and extracts embedded metadata

## 🎯 Common Use Cases

### **Library Management**
- **Standardize formats**: Convert your entire collection to a single format (e.g., all CBZ)
- **Reduce file sizes**: Convert to more efficient formats or compress existing files
- **Add metadata**: Enhance your collection with proper titles, authors, and reading directions

### **Content Creation**
- **Digitize physical manga**: Scan pages and create digital archives
- **Edit and republish**: Extract images, make edits, and repackage
- **Format optimization**: Create different versions for different devices or platforms

### **Archive Preservation**
- **Format migration**: Move from older formats (CBR) to more standard ones (CBZ)
- **Backup creation**: Convert to multiple formats for redundancy
- **Metadata preservation**: Ensure important information travels with your files

## 💡 How to Use

1. **Start with any workflow block** by dragging it into your OOMOL workspace
2. **Connect your input** - select the manga file or image folder you want to work with
3. **Configure settings** - choose output format, add metadata, set reading order
4. **Run the workflow** - watch as your files are processed automatically
5. **Access results** - download or use the converted files in subsequent blocks

## 🌟 Key Features

- **Batch Processing**: Handle multiple files or entire directories at once
- **Lossless Conversion**: Maintain original image quality throughout the process
- **Metadata Support**: Preserve and edit titles, authors, and reading preferences
- **Format Flexibility**: Convert between any supported formats seamlessly
- **Visual Workflows**: No coding required - build your processes visually

## 🛠️ Technical Requirements

- **Platform**: OOMOL workflow environment
- **Dependencies**: Automatically installed (fpdf2, Pillow, PyMuPDF, rarfile)
- **Input formats**: CBZ, CBR, EPUB, PDF files or image directories
- **Output formats**: CBZ, EPUB, PDF files or extracted images

## 📖 Getting Started

The easiest way to start is with the **Transform** block:

1. Add the Transform block to your workflow
2. Select a manga file from your computer
3. Choose your desired output format
4. Add any metadata (title, author, reading direction)
5. Run the workflow and download your converted file

For more advanced workflows, try combining blocks - for example, use **Unarchive to Images** to extract pages, then **Archive Directory** to repackage them in a different format with new metadata.

## 🔗 Repository

Visit our [GitHub repository](https://github.com/oomol-flows/manga-tools) for source code, issue reporting, and contributions.

---

*Manga Tools v0.0.3 - Built for the OOMOL visual workflow platform*