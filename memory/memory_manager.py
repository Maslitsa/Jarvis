import os
import re
from pathlib import Path
from datetime import datetime
import sys

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
VAULT_DIR = BASE_DIR / "jarvis_vault"

def _ensure_vault():
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    index_path = VAULT_DIR / "Jarvis Brain.md"
    if not index_path.exists():
        index_path.write_text("# Jarvis Brain Index\n\n[[Identity]]\n[[Preferences]]\n[[Projects]]\n[[Relationships]]\n[[Wishes]]\n[[Notes]]\n", encoding="utf-8")

def _read_md(filename: str) -> str:
    path = VAULT_DIR / f"{filename}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""

def _write_md(filename: str, content: str):
    _ensure_vault()
    path = VAULT_DIR / f"{filename}.md"
    path.write_text(content, encoding="utf-8")

def _append_md(filename: str, content: str):
    _ensure_vault()
    path = VAULT_DIR / f"{filename}.md"
    existing = _read_md(filename)
    if existing:
        path.write_text(existing + "\n" + content, encoding="utf-8")
    else:
        path.write_text(f"# {filename.capitalize()}\n\n" + content, encoding="utf-8")

def update_memory(memory_update: dict) -> dict:
    for cat, items in memory_update.items():
        if isinstance(items, dict):
            for key, val_obj in items.items():
                val = val_obj.get("value", "") if isinstance(val_obj, dict) else str(val_obj)
                if val:
                    # Write to the category file
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    cat_name = cat.capitalize()
                    
                    # Create a specific node for the key if it's important
                    node_name = f"{key.replace('_', ' ').title()}"
                    _write_md(node_name, f"# {node_name}\n\n{val}\n\n*Updated: {timestamp}*")
                    
                    # Append a link to the category file
                    _append_md(cat_name, f"- {node_name}: [[{node_name}]]")
    return load_memory()

def load_memory() -> dict:
    # We parse the vault back into the dictionary format that main.py expects
    _ensure_vault()
    memory = {
        "identity": {},
        "preferences": {},
        "projects": {},
        "relationships": {},
        "wishes": {},
        "notes": {}
    }
    
    for cat in memory.keys():
        cat_file = _read_md(cat.capitalize())
        lines = cat_file.split("\n")
        for line in lines:
            match = re.search(r'- (.*?): \[\[(.*?)\]\]', line)
            if match:
                key_title = match.group(1)
                node_name = match.group(2)
                node_content = _read_md(node_name)
                # extract just the value from node content
                val_match = re.search(r'# (.*?)\n\n(.*?)\n\n\*Updated:', node_content, re.DOTALL)
                if val_match:
                    val = val_match.group(2).strip()
                    # convert back to snake_case key
                    key = key_title.lower().replace(" ", "_")
                    memory[cat][key] = {"value": val}
    return memory

def save_memory(memory: dict):
    update_memory(memory)

def format_memory_for_prompt(memory: dict | None) -> str:
    if not memory:
        return ""

    lines = []
    
    for cat, items in memory.items():
        if items:
            lines.append(f"[{cat.upper()}]")
            for key, val_obj in items.items():
                val = val_obj.get("value", "") if isinstance(val_obj, dict) else str(val_obj)
                lines.append(f"- {key.replace('_', ' ').title()}: {val}")
            lines.append("")

    if not lines:
        return ""

    header = "[OBSIDIAN KNOWLEDGE GRAPH MEMORY — Use this to provide personalized answers]\n"
    return header + "\n".join(lines) + "\n"

def remember(key: str, value: str, category: str = "notes") -> str:
    update_memory({category: {key: {"value": value}}})
    return f"Remembered in Obsidian Vault: [[{category.capitalize()}]] -> [[{key.replace('_', ' ').title()}]]"

def forget(key: str, category: str = "notes") -> str:
    # Simplified forget: just remove the file
    node_name = key.replace('_', ' ').title()
    path = VAULT_DIR / f"{node_name}.md"
    if path.exists():
        path.unlink()
        return f"Forgotten node: {node_name}"
    return f"Not found: {node_name}"

forget_memory = forget