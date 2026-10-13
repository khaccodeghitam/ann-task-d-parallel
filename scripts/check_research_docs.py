#!/usr/bin/env python3
"""Check active navigation; historical frozen documents are not rewritten."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
files=[root/'README.md',root/'AGENTS.md']+list((root/'docs').glob('*.md'))
errors=[]
for p in files:
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if '://' in target or target.startswith('#'):continue
  if not (p.parent/target.split('#')[0]).exists():errors.append(str(p.relative_to(root))+': '+target)
if errors:raise SystemExit('\n'.join(errors))
print(f'Active documentation links: PASS ({len(files)} files)')
