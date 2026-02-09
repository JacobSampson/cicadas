import argparse
import json
import os
import re
from pathlib import Path
from utils import get_project_root, load_json

def gather_context(name, is_brood=False):
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry = load_json(cicadas / "registry.json")
    
    context = {
        "forward_docs": {},
        "code_context": {},
        "canon_docs": {}
    }

    # 1. Gather Forward Docs
    if is_brood:
        source_dir = cicadas / "forward" / "broods" / name
    else:
        source_dir = cicadas / "forward" / name
    
    if source_dir.exists():
        for doc in source_dir.glob("*.md"):
            context["forward_docs"][doc.name] = doc.read_text()

    # 2. Gather Code Context (if branch)
    modules = []
    if not is_brood:
        branch_info = registry.get("branches", {}).get(name, {})
        modules = branch_info.get("modules", [])
    
    for mod in modules:
        # Simplistic mapping: mod.name -> src/mod/
        mod_path = root / "src" / mod.replace(".", "/")
        if not mod_path.exists():
            mod_path = root / mod.replace(".", "/") # Try without src
            
        if mod_path.exists():
            for py_file in mod_path.glob("**/*.py"):
                rel_path = py_file.relative_to(root)
                context["code_context"][str(rel_path)] = py_file.read_text()

    # 3. Gather Existing Canon
    canon_dir = cicadas / "canon"
    if canon_dir.exists():
        for doc in canon_dir.glob("*.md"):
            context["canon_docs"][doc.name] = doc.read_text()
            
    return context

def generate_prompt(context):
    root = get_project_root()
    prompt_template = (root / ".cicadas" / "scripts" / "chorus" / "templates" / "synthesis-prompt.md")
    if not prompt_template.exists():
        # Fallback to absolute if templates not in .cicadas (they are in the cicadas repo)
        prompt_template = Path(__file__).parent.parent / "templates" / "synthesis-prompt.md"

    template_text = prompt_template.read_text()
    
    prompt = f"{template_text}\n\n"
    prompt += "### DATA CONTEXT ###\n\n"
    
    prompt += "#### EXISTING CANON ####\n"
    for name, content in context["canon_docs"].items():
        prompt += f"File: canon/{name}\n```markdown\n{content}\n```\n\n"
        
    prompt += "#### FORWARD DOCS ####\n"
    for name, content in context["forward_docs"].items():
        prompt += f"File: {name}\n```markdown\n{content}\n```\n\n"

    prompt += "#### CODE CONTEXT ####\n"
    for path, content in context["code_context"].items():
        prompt += f"File: {path}\n```python\n{content}\n```\n\n"
        
    return prompt

def apply_response(response_text):
    root = get_project_root()
    cicadas = root / ".cicadas"
    canon_dir = cicadas / "canon"
    
    # Regex to find code blocks with file names
    # Expecting: File: canon/filename.md\n```markdown\ncontent\n```
    pattern = r"File: (canon/[\w\/\.-]+)\n```(?:markdown|python)?\n(.*?)\n```"
    matches = re.findall(pattern, response_text, re.DOTALL)
    
    if not matches:
        print("No file content blocks found in response.")
        return

    for file_path, content in matches:
        target = root / file_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content.strip() + "\n")
        print(f"✅ Updated {file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Headless Synthesis Orchestrator")
    parser.add_argument("name", help="Name of the branch or brood")
    parser.add_argument("--brood", action="store_true", help="Synthesize for a brood")
    parser.add_argument("--apply", help="Path to a file containing the LLM response to apply to the canon")
    
    args = parser.parse_args()
    
    if args.apply:
        response_path = Path(args.apply)
        if response_path.exists():
            apply_response(response_path.read_text())
        else:
            print(f"Error: Response file {args.apply} not found.")
    else:
        ctx = gather_context(args.name, is_brood=args.brood)
        print(generate_prompt(ctx))
