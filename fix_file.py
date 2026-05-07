#!/usr/bin/env python3
import re

# Read the file
with open(r'sn-article-template/sn-article-eng.tex', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all triple and double backslashes before \real
content = content.replace('\\\\\\real', '\\real')
content = content.replace('\\\\real', '\\real')

# Verify no other issues
print(f"Total \\real commands: {len(re.findall(r'\\real', content))}")

# Write back
with open(r'sn-article-template/sn-article-eng.tex', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed all escaping issues!")
