# Abigail – AI Assistant with Gemini

Abigail is a full-featured AI assistant built with Gradio and Google Gemini. It offers a clean chat interface with personality customization, multilingual support, conversation history, snapshots, trash management, and more.

## Features

- 🤖 **AI Chat** – Powered by Google Gemini with model fallback
- 🧠 **Personalities** – Choose from Tsundere, Gentle, Sarcastic, or Professor
- 🌍 **Multilingual** – English, Português, Español, Français
- 💬 **Conversation History** – Auto-saved session, snapshots, trash
- 🗂️ **File Management** – Load, delete, restore, and empty trash
- ✏️ **Edit Messages** – Delete individual messages
- 🔄 **Reset** – Restore all settings to defaults
- 🎨 **Font Customization** – Family and size
- 📥 **Export History** – Download conversation as JSON
- 🧹 **Clear All History** – Permanently delete all snapshots
- 📊 **Progress Bar** – Visual feedback during AI processing
- 🔒 **Robust** – Backup and validation for config file
- 🧩 **Modular** – Cleanly organized codebase

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/abigail.git
cd abigail

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY