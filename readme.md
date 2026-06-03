<img width="856" height="791" alt="image" src="https://github.com/user-attachments/assets/e6affd3f-3fa9-4379-94b4-8156ed5fb5b5" /># 🤖 Jarvis AI — Maslitsa Edition
### The Ultimate Personal AI Assistant with Obsidian Memory Integration

A real-time voice AI that can hear, see, understand, and control your computer — on any OS. Supporting Windows, macOS, and Linux. Local execution. Zero subscriptions. Engineered for total autonomy.

This specific version of Jarvis is a **custom fork actively developed by Maslitsa**, featuring major improvements to memory persistence, a unified voice system, and an exclusive integration with **Obsidian Vault** for long-term memory management.

---

## ✨ Overview

Jarvis AI bridges the gap between the operating system and human intent. Through natural dialogue, Jarvis analyzes your screen, processes uploaded documents, and executes complex workflows. 

**Key Feature:** The brain of this Jarvis is connected directly to an Obsidian Vault. When you tell Jarvis facts about yourself, your projects, or your preferences, he permanently writes them into a structured knowledge graph in Obsidian. He can later read these markdown files to recall everything about you instantly.

---

## 🚀 Capabilities

### Core Features
| Feature | Description |
|---|---|
| 🎙️ **Unified Voice System** | Seamless, ultra-low latency conversation with a single cohesive persona |
| 🧠 **Obsidian Memory** | Deeply remembers your projects and preferences using an external Obsidian Vault |
| 🖥️ **System Control** | Launch apps, manage files, and execute terminal commands |
| 🧩 **Autonomous Tasks** | High-level planning for complex, multi-step goals |
| 👁️ **Visual Awareness** | Real-time screen processing and vision analysis |
| 🛡️ **Total Privacy** | All your memory and data are stored locally. No data leaks. |

---

## 📷 The Obsidian Brain

<img width="856" height="791" alt="image" src="https://github.com/user-attachments/assets/99fb3d8a-5d44-4068-a7dd-87b6d00203a0" />
`![Obsidian Vault Graph View](path/to/your/image.png)`

Jarvis uses Obsidian as his long-term memory center. You can open the `jarvis_vault` folder directly in Obsidian to see a living, breathing graph of everything Jarvis knows about you!

---

## ⚡ Quick Start

```bash
git clone https://github.com/Maslitsa/Jarvis.git
cd Jarvis
pip install -r requirements.txt
playwright install
python setup.py
python main.py
```

> ⚠️ **Installation Note:** To keep the repository lightweight, some OS-specific dependencies are not bundled in `requirements.txt`. If you run into a `ModuleNotFoundError`, simply install the missing package via `pip install <module_name>` for your specific system.

---

## 📋 Requirements

| Requirement | Details |
|---|---|
| **OS** | Windows 10/11, macOS, or Linux |
| **Python** | 3.11 or 3.12 |
| **Microphone** | Required for voice interaction |
| **API Key** | Free Google Gemini API key |

---

## 🛡️ Privacy & Security

**Your data is yours.** 
All files, configuration, API keys, and memory vaults (`jarvis_vault`) are completely local. The `.gitignore` is explicitly configured to ensure none of your personal memory or identity nodes are ever pushed to GitHub or leaked publicly. The only thing sent externally is the API request to Gemini.

---

## ⚖️ License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Maslitsa.
