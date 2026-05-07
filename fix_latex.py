#!/usr/bin/env python3
# Fix LaTeX escaping issues in sn-article-eng.tex

import os
os.chdir(r'r:\Work\My_Science_projects\Code_Baglan\sn-article-template')

with open('sn-article-eng.tex', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the broken escaping from PowerShell replacement
content = content.replace(r'\\setlength\{\\LTright\}\{\\fill\}', r'\setlength{\LTright}{\fill}')

with open('sn-article-eng.tex', 'w', encoding='utf-8') as f:
    f.write(content)
    
print("✓ Fixed LaTeX escaping in tables")
