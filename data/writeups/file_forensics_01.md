---
title: File Forensics and Hidden Data
category: forensics
techniques: ["steganography", "hidden files", "metadata analysis"]
difficulty: medium
author: Forensics Expert
year: 2024
tags: ["forensics", "files", "steganography"]
---

# File Forensics and Hidden Data

## Overview
File forensics involves analyzing files to discover hidden information, metadata, or concealed data.

## Common Techniques

### 1. Hidden Files
Files may be hidden using:
- Leading dots in Unix/Linux (.hiddenfile)
- Alternate data streams in Windows
- File extension spoofing
- Steganography

### 2. Metadata Analysis
Extract metadata from files:
- EXIF data from images
- Document properties
- Hidden comments
- Author information

Tools: `exiftool`, `strings`, `binwalk`

### 3. Steganography
Data hidden within other files:
- LSB (Least Significant Bit) in images
- Text hidden in whitespace
- Audio steganography

Tools: `steghide`, `outguess`, `stegdetect`

### 4. File Carving
Recover files from disk images or unallocated space:
- `foremost`
- `scalpel`
- `photorec`

## Detection Indicators
- Unusual file sizes
- Suspicious file extensions
- Files with hidden attributes
- Encrypted or compressed data

## Investigation Workflow
1. List all files including hidden ones
2. Check file types and extensions
3. Extract metadata
4. Search for strings and patterns
5. Use carving tools if needed
6. Apply steganography detection

## Prevention
- Secure file deletion
- Metadata scrubbing before sharing
- Encrypt sensitive data properly
- Use secure file transfer methods
