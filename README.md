# 🤖 Abigail – AI Assistant with Gemini

Abigail is a full-featured AI assistant built with Gradio and Google Gemini. It offers a clean chat interface with multiple personalities, multilingual support, conversation history management, and export tools.

---

## 🚀 Quick Start (Get it running in 3 steps)

1. Clone the repository:
   git clone https://github.com/yourusername/abigail.git
   cd abigail

2. Install dependencies:
   pip install -r requirements.txt

3. Run the app:
   python app.py

Open http://127.0.0.1:7860 in your browser.

Note: You'll need a GOOGLE_API_KEY. See the Environment Variables section below.

---

## ✨ Features

### 🤖 Core AI
- Chat with Gemini – Powered by Google's Gemini API with fallback models.
- 4 Personalities – Choose from Tsundere, Gentle, Sarcastic, or Professor to change the tone of responses.
- Conversation Context – The AI remembers the last 10 exchanges for coherent replies.

### 💾 Data Management
- Auto-save – Your current session is saved automatically.
- Snapshots – Save named snapshots of conversations to revisit later.
- Trash – Delete snapshots (moves to trash) and restore them if needed.
- Export History – Download the entire conversation as a JSON file.
- Clear All History – Permanently delete all saved snapshots.

### 🌍 User Experience
- Multilingual UI – Available in English, Português, Español, and Français.
- Font Customization – Change font family (Sans-serif, Serif, Monospace) and size (Small, Medium, Large).
- Progress Bar – Visual feedback while the AI is generating a response.
- Adjustable Chat Height – Resize the chat window to fit your screen.

### 🛠️ Robustness
- Config Backup – config.json is automatically backed up (config.json.bak) and validated.
- Modular Codebase – Cleanly organized into separate modules for easy maintenance.

---

## 📥 Installation

### 1. Clone the repository
git clone https://github.com/yourusername/abigail.git
cd abigail

### 2. Create a virtual environment (recommended)
Windows:
python -m venv venv
venv\Scripts\activate

Linux / Mac:
python -m venv venv
source venv/bin/activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Set up your API key
Create a .env file in the root directory:
cp .env.example .env

Edit .env and add your Google Gemini API key:
GOOGLE_API_KEY=your_actual_api_key_here

Where to get the key: Google AI Studio (https://aistudio.google.com/)

---

## 🕹️ Usage

### Run the app
python app.py

Open http://127.0.0.1:7860 in your browser.

### Keyboard Shortcuts
- Ctrl+Enter (or Cmd+Enter on Mac) – Send message.

### Changing Fonts / Language
Adjust the settings in the ⚙️ Settings panel on the right.
Important: After changing font family, font size, or interface language, refresh the page (F5) for the changes to take effect.

---

## 📂 Project Structure

abigail/
├── abigail/                 # Core package
│   ├── config.py            # Configuration management (config.json)
│   ├── persistence.py       # History, snapshots, and trash operations
│   ├── ai_client.py         # Gemini API client
│   ├── prompt_builder.py    # Personality and context prompt builder
│   ├── translations.py      # UI translations (4 languages)
│   └── ui/
│       └── interface.py     # Gradio UI components and callbacks
├── tests/                   # Unit tests
│   └── test_config.py
├── app.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Files ignored by Git
└── README.md                # This file

---

## ⚙️ Environment Variables

| Variable | Description |
|----------|-------------|
| GOOGLE_API_KEY | Required. Your Google Gemini API key. |
| PORT | (Optional) Port for the Gradio app. Defaults to 7860. |
| RENDER | (Optional) Set to true if deploying on Render. |

---

## 🧪 Running Tests

To run the unit tests:
pip install pytest
python -m pytest tests/

---

## 🚀 Deployment

### Deploy on Hugging Face Spaces
1. Create a new Space on Hugging Face.
2. Upload the code (exclude venv/, history/, trash/, config.json, *.log).
3. Add GOOGLE_API_KEY as a repository secret.
4. The app will launch automatically.

### Deploy on Render
1. Create a new Web Service on Render.
2. Connect your GitHub repository.
3. Set the environment variable RENDER=true.
4. Add GOOGLE_API_KEY as a secret environment variable.

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| ImportError: No module named 'abigail' | Make sure you are running python app.py from the root directory (Chatbot/). |
| ValueError: GOOGLE_API_KEY environment variable not set | You forgot to create the .env file or it's missing the API key. Copy .env.example to .env and add your key. |
| Changes to fonts/language don't appear | Refresh the page (F5) after saving settings. |
| Port 7860 already in use | Change the port by setting the PORT environment variable (e.g., export PORT=7861 on Linux/Mac or $env:PORT=7861 on Windows PowerShell before running). |

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch (git checkout -b feature/amazing-feature).
3. Make your changes.
4. Run tests (python -m pytest tests/).
5. Commit and push (git push origin feature/amazing-feature).
6. Open a Pull Request.

---

## 📜 License

This project is licensed under the MIT License – see the LICENSE file for details.

---

## 🙏 Credits

- Built with Gradio and Google Gemini.
- Icons by Twemoji.
