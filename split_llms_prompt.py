import os
import re
from collections import defaultdict

SRC = ".github/llms-full.md"
DST_DIR = ".github/copilot-prompts"
os.makedirs(DST_DIR, exist_ok=True)

with open(SRC, "r", encoding="utf-8") as f:
    content = f.read()

# Find all function blocks with their source code path
pattern = re.compile(
    r"(##### .+?)(Source code in `pyrevitlib/pyrevit/([^/]+)/.+?`)(.*?)(?=##### |\Z)", 
    re.DOTALL | re.IGNORECASE
)
matches = pattern.findall(content)

sections = defaultdict(list)

for func_header, src_line, subfolder, rest in matches:
    # Use only the subfolder as filename, fallback to 'misc'
    fname = f"{subfolder.lower() if subfolder else 'misc'}.md"
    block = f"{func_header}\n{src_line}\n{rest}".strip()
    sections[fname].append(block)

# Write each subfolder's functions to its own markdown file
for fname, blocks in sections.items():
    fpath = os.path.join(DST_DIR, fname)
    with open(fpath, "w", encoding="utf-8") as out:
        out.write("\n\n---\n\n".join(blocks))

# Optionally, write an index
with open(os.path.join(DST_DIR, "README.md"), "w", encoding="utf-8") as idx:
    idx.write("# Copilot Prompts by Subfolder\n\n")
    for fname in sorted(sections):
        idx.write(f"- [{fname}]({fname})\n")

print(f"Split complete. Files: {list(sections.keys())}")