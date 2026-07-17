"""
Gradio interface - all components and callbacks.
No theme selection. Only light mode.
"""

import os
import json
import logging
import glob
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any  # noqa: F401

import gradio as gr

from abigail.config import Config
from abigail.persistence import HistoryRepository
from abigail.ai_client import AIProvider
from abigail.prompt_builder import PromptBuilder
from abigail.translations import TRANSLATIONS

logger = logging.getLogger(__name__)


class UI:
    def __init__(self, config: Config, repo: HistoryRepository, ai: AIProvider) -> None:
        self.config = config
        self.repo = repo
        self.ai = ai
        self._lang = config.get("interface_language", "English")
        self.texts = TRANSLATIONS[self._lang]
        self.demo: Optional[gr.Blocks] = None
        self._build()

    # ======================================================================
    # HELPERS
    # ======================================================================
    def _to_messages(self, history: List[Tuple[str, str]]) -> List[Dict[str, str]]:
        """Convert tuple history to Gradio message format."""
        messages = []
        for user, bot in history:
            messages.append({"role": "user", "content": user})
            if bot:
                messages.append({"role": "assistant", "content": bot})
        return messages

    def _build(self) -> None:
        with gr.Blocks() as self.demo:
            cfg_state = gr.State(self.config.to_dict())
            hist_state = gr.State([])

            title = gr.Markdown(f"# {self.texts['title']}")
            subtitle = gr.Markdown(f"## {self.texts['subtitle']}")

            # ---- Main layout ----
            with gr.Row():
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(label="Abigail", height=self.config.get("chat_height"))
                with gr.Column(scale=1):
                    with gr.Accordion(self.texts["settings_label"], open=False):
                        pers_choices = [(self.texts["personality_names"][k], k) for k in PromptBuilder.PERSONALITIES.keys()]
                        personality = gr.Dropdown(
                            choices=pers_choices,
                            value=self.config.get("personality"),
                            label=self.texts["personality_label"]
                        )
                        response_lang = gr.Dropdown(
                            choices=["English", "Português", "Español", "Français"],
                            value=self.config.get("response_language"),
                            label=self.texts["response_language_label"]
                        )
                        interface_lang = gr.Dropdown(
                            choices=["English", "Português", "Español", "Français"],
                            value=self._lang,
                            label=self.texts["interface_language_label"]
                        )
                        with gr.Row():
                            # Botões de tema removidos
                            pass
                        font_family = gr.Dropdown(
                            choices=["Sans-serif", "Serif", "Monospace"],
                            value=self.config.get("font_family").capitalize(),
                            label=self.texts["font_family_label"]
                        )
                        font_size = gr.Dropdown(
                            choices=["Small", "Medium", "Large"],
                            value=self.config.get("font_size").capitalize(),
                            label=self.texts["font_size_label"]
                        )
                        chat_height = gr.Slider(
                            minimum=200, maximum=800, value=self.config.get("chat_height"),
                            step=50, label=self.texts["chat_height_label"]
                        )
                        with gr.Row():
                            reset_btn = gr.Button("↺ Restore Defaults", size="sm")
                            new_conv_btn = gr.Button(self.texts["new_conversation_btn"], size="sm")

            # ---- Input ----
            with gr.Row():
                msg = gr.Textbox(
                    label=self.texts["placeholder"],
                    placeholder=self.texts["placeholder"],
                    scale=4
                )
                send = gr.Button(self.texts["send_btn"], variant="primary")

            # ---- File management ----
            with gr.Row():
                with gr.Column(scale=2):
                    files_dropdown = gr.Dropdown(
                        choices=self.repo.list_snapshots(),
                        label=self.texts["load_dropdown_label"]
                    )
                with gr.Column(scale=1):
                    load_btn = gr.Button(self.texts["load_btn"])
            with gr.Row():
                delete_btn = gr.Button(self.texts["delete_btn"])
                delete_all_btn = gr.Button(self.texts["delete_all_btn"], variant="stop")
                save_snapshot_btn = gr.Button(
                    self.texts["save_snapshot_btn"],
                    variant="secondary"
                )

            with gr.Row():
                with gr.Column(scale=2):
                    trash_dropdown = gr.Dropdown(
                        choices=self.repo.list_trash(),
                        label=self.texts["trash_label"]
                    )
                with gr.Column(scale=1):
                    restore_btn = gr.Button(self.texts["restore_btn"])
            with gr.Row():
                empty_trash_btn = gr.Button(self.texts["empty_trash_btn"], variant="stop")

            # ---- Export and Clear ----
            with gr.Row():
                export_btn = gr.Button("📥 Export History", variant="secondary")
                clear_all_btn = gr.Button("🧹 Clear All History", variant="stop")
                export_file = gr.File(label="Download export", interactive=False, visible=False)

            # ---- Message deletion ----
            with gr.Row():
                confirm = gr.Checkbox(label=self.texts["confirm_label"], value=False)
            with gr.Row():
                messages_checkbox = gr.CheckboxGroup(
                    choices=[],
                    label=self.texts["messages_label"]
                )
                delete_msgs_btn = gr.Button(self.texts["delete_msgs_btn"], variant="stop")
                status_msg = gr.Textbox(
                    label=self.texts["status_label"],
                    placeholder=self.texts["status_placeholder"],
                    interactive=False
                )

            # ======================================================================
            # CALLBACKS
            # ======================================================================

            # ---- Send message ----
            send.click(
                self._on_send,
                [msg, hist_state, cfg_state],
                [msg, hist_state, chatbot, messages_checkbox, status_msg, send]
            )
            msg.submit(
                self._on_send,
                [msg, hist_state, cfg_state],
                [msg, hist_state, chatbot, messages_checkbox, status_msg, send]
            )

            # ---- File management ----
            load_btn.click(
                self._on_load,
                [files_dropdown],
                [hist_state, chatbot, messages_checkbox, status_msg, files_dropdown, trash_dropdown]
            )
            delete_btn.click(
                self._on_delete,
                [files_dropdown],
                [files_dropdown, trash_dropdown, status_msg]
            )
            delete_all_btn.click(
                self._on_delete_all,
                [confirm],
                [files_dropdown, trash_dropdown, status_msg, confirm]
            )
            save_snapshot_btn.click(
                self._on_save_snapshot,
                [hist_state],
                [status_msg, files_dropdown]
            )
            restore_btn.click(
                self._on_restore,
                [trash_dropdown],
                [trash_dropdown, files_dropdown, status_msg]
            )
            empty_trash_btn.click(
                self._on_empty_trash,
                [],
                [trash_dropdown, status_msg]
            )

            # ---- Delete messages ----
            delete_msgs_btn.click(
                self._on_delete_messages,
                [hist_state, messages_checkbox],
                [hist_state, messages_checkbox, chatbot, status_msg]
            )

            # ---- New conversation ----
            new_conv_btn.click(
                self._on_new_conversation,
                [],
                [hist_state, chatbot, messages_checkbox, status_msg]
            )

            # ---- Export and Clear ----
            export_btn.click(
                self._on_export,
                [hist_state],
                [status_msg, export_file]
            )
            clear_all_btn.click(
                self._on_clear_all,
                [],
                [files_dropdown, trash_dropdown, status_msg]
            )

            # ---- Interface language – update all labels ----
            interface_lang.change(
                self._on_language_change,
                [interface_lang, cfg_state, hist_state],
                [
                    title, subtitle, personality, response_lang, interface_lang,
                    msg, send, chat_height, font_family, font_size,
                    files_dropdown, delete_btn, delete_all_btn,
                    trash_dropdown, restore_btn, empty_trash_btn,
                    confirm, messages_checkbox, delete_msgs_btn,
                    status_msg, cfg_state, new_conv_btn, save_snapshot_btn
                ]
            )

            # ---- Font family – save and show reload message ----
            font_family.change(
                self._save_font,
                [font_family, gr.State("font_family"), cfg_state],
                [cfg_state, status_msg]
            )

            # ---- Font size – save and show reload message ----
            font_size.change(
                self._save_font,
                [font_size, gr.State("font_size"), cfg_state],
                [cfg_state, status_msg]
            )

            # ---- Reset – save defaults and show reload message ----
            reset_btn.click(
                self._on_reset,
                [cfg_state],
                [
                    title, subtitle, personality, response_lang, interface_lang,
                    msg, send, font_family, font_size, chat_height, chatbot,
                    cfg_state, files_dropdown, trash_dropdown,
                    messages_checkbox, status_msg, new_conv_btn, save_snapshot_btn
                ]
            )

            # ---- Personality and response language – silent save ----
            personality.change(
                self._save_silent,
                [personality, gr.State("personality"), cfg_state],
                [cfg_state]
            )
            response_lang.change(
                self._save_silent,
                [response_lang, gr.State("response_language"), cfg_state],
                [cfg_state]
            )

            # ---- Chat height – no reload needed ----
            chat_height.change(
                self._on_chat_height_change,
                [chat_height, cfg_state],
                [cfg_state, chatbot]
            )

            # ---- Load initial session ----
            self.demo.load(
                self._on_load_initial,
                [],
                [hist_state, chatbot, messages_checkbox, status_msg]
            )

    # ======================================================================
    # CALLBACKS
    # ======================================================================

    def _on_send(self, msg_text: str, history: List[Tuple[str, str]],
                 cfg_dict: Dict[str, Any], progress: gr.Progress = gr.Progress()):
        if not msg_text:
            return "", history, gr.update(), gr.update(choices=[]), "Empty message", gr.update(interactive=True)

        progress(0.1, desc="Preparing...")
        reply = ""
        send_update = gr.update(interactive=False)
        status_msg_update = self.texts.get("thinking", "Thinking...")
        try:
            personality = cfg_dict.get("personality", "tsundere")
            response_lang = cfg_dict.get("response_language", "English")
            context = cfg_dict.get("context_messages", 10)
            max_hist = cfg_dict.get("max_history", 500)

            if len(history) >= max_hist:
                history = history[-(max_hist - 1):]

            progress(0.3, desc="Building prompt...")
            prompt = PromptBuilder.build(history, personality, response_lang, context)
            progress(0.6, desc="Calling AI...")
            reply, err = self.ai.generate_response(prompt)
            if err:
                reply = f"⚠️ {err}"
            progress(0.9, desc="Done!")
        except Exception as e:
            reply = f"❌ Unexpected error: {str(e)}"
            logger.error(f"AI error: {e}")
        finally:
            history.append((msg_text, reply))
            self.repo.save_current(history)
            opts = self._message_options(history)
            send_update = gr.update(interactive=True)
            status_msg_update = f"Response ({len(history)} msgs)"
            progress(1.0, desc="Complete")

        # Converter history para mensagens antes de atualizar o chatbot
        messages = self._to_messages(history)
        return ("", history, gr.update(value=messages),
                gr.update(choices=opts, value=[]),
                gr.update(value=status_msg_update), send_update)

    def _on_load(self, fname: str):
        if not fname:
            return [], gr.update(), gr.update(choices=[]), "No file", gr.update(), gr.update()
        history, err = self.repo.load_snapshot(fname)
        if err:
            return [], gr.update(), gr.update(choices=[]), f"Error: {err}", gr.update(), gr.update()
        self.repo.save_current(history)
        opts = self._message_options(history)
        messages = self._to_messages(history)
        return (history, gr.update(value=messages), gr.update(choices=opts, value=[]),
                f"Loaded {fname}", gr.update(choices=self.repo.list_snapshots()),
                gr.update(choices=self.repo.list_trash()))

    def _on_delete(self, fname: str):
        if not fname:
            return gr.update(), gr.update(), "No file selected"
        ok, err = self.repo.delete_snapshot(fname)
        if ok:
            return (gr.update(choices=self.repo.list_snapshots()),
                    gr.update(choices=self.repo.list_trash()),
                    f"Moved {fname} to trash")
        return (gr.update(choices=self.repo.list_snapshots()),
                gr.update(choices=self.repo.list_trash()),
                f"Error: {err}")

    def _on_delete_all(self, confirmed: bool):
        if not confirmed:
            return gr.update(), gr.update(), "Check confirmation", gr.update(value=False)
        count, err = self.repo.delete_all_snapshots()
        if err:
            return (gr.update(choices=self.repo.list_snapshots()),
                    gr.update(choices=self.repo.list_trash()),
                    f"{count} moved, errors: {err}",
                    gr.update(value=False))
        return (gr.update(choices=self.repo.list_snapshots()),
                gr.update(choices=self.repo.list_trash()),
                f"{count} moved to trash",
                gr.update(value=False))

    def _on_save_snapshot(self, history: List[Tuple[str, str]]):
        if not history:
            return gr.update(value="No messages"), gr.update(choices=self.repo.list_snapshots())
        fname, err = self.repo.save_snapshot(history)
        if err:
            return gr.update(value=f"Error: {err}"), gr.update(choices=self.repo.list_snapshots())
        return gr.update(value=f"Snapshot: {fname}"), gr.update(choices=self.repo.list_snapshots())

    def _on_restore(self, fname: str):
        if not fname:
            return gr.update(), gr.update(), "No file selected"
        ok, err = self.repo.restore_from_trash(fname)
        if ok:
            return (gr.update(choices=self.repo.list_trash()),
                    gr.update(choices=self.repo.list_snapshots()),
                    f"Restored {fname}")
        return (gr.update(choices=self.repo.list_trash()),
                gr.update(choices=self.repo.list_snapshots()),
                f"Error: {err}")

    def _on_empty_trash(self):
        count, err = self.repo.empty_trash()
        if err:
            return gr.update(choices=[]), f"{count} removed, errors: {err}"
        return gr.update(choices=[]), f"Trash emptied ({count} files)"

    def _on_delete_messages(self, history: List[Tuple[str, str]],
                            selected: List[str]):
        if not selected:
            return history, gr.update(), gr.update(value=history), "No messages selected"
        indices = sorted([self._parse_idx(s) for s in selected if self._parse_idx(s) >= 0], reverse=True)
        for i in indices:
            if i < len(history):
                del history[i]
        self.repo.save_current(history)
        opts = self._message_options(history)
        messages = self._to_messages(history)
        return history, gr.update(choices=opts, value=[]), gr.update(value=messages), f"{len(indices)} messages deleted"

    def _on_new_conversation(self):
        self.repo.save_current([])
        return [], gr.update(value=[]), gr.update(choices=[]), "Conversation cleared"

    def _on_export(self, history: List[Tuple[str, str]]):
        if not history:
            return gr.update(value="No history to export"), gr.update(visible=False)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"history/export_{ts}.json"
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        return gr.update(value=f"Exported: {fname}"), gr.update(value=fname, visible=True)

    def _on_clear_all(self):
        files = glob.glob(os.path.join(self.repo.base_dir, "conversation_*.json"))
        count = 0
        for f in files:
            try:
                os.remove(f)
                count += 1
            except Exception as e:
                logger.error(f"Could not delete {f}: {e}")
        return (gr.update(choices=[]), gr.update(choices=[]), f"Cleared {count} snapshots.")

    def _save_font(self, value: str, key: str, cfg_dict: Dict[str, Any]):
        if key in ("font_family", "font_size"):
            cfg_dict[key] = value.lower()
        else:
            cfg_dict[key] = value
        self.config._data.update(cfg_dict)
        self.config._save()
        return cfg_dict, self.texts["reload_message"]

    def _on_reset(self, cfg_dict: Dict[str, Any]):
        new_cfg = Config.DEFAULTS.copy()
        self.config._data.update(new_cfg)
        self.config._save()
        texts = TRANSLATIONS[new_cfg["interface_language"]]
        pers_choices = [(texts["personality_names"][k], k) for k in PromptBuilder.PERSONALITIES.keys()]
        return (
            gr.update(value=f"# {texts['title']}"),
            gr.update(value=f"## {texts['subtitle']}"),
            gr.update(value=new_cfg["personality"], choices=pers_choices, label=texts["personality_label"]),
            gr.update(value=new_cfg["response_language"], label=texts["response_language_label"]),
            gr.update(value=new_cfg["interface_language"], label=texts["interface_language_label"]),
            gr.update(label=texts["placeholder"], placeholder=texts["placeholder"]),
            gr.update(value=texts["send_btn"]),
            gr.update(value=new_cfg["font_family"].capitalize(), label=texts["font_family_label"]),
            gr.update(value=new_cfg["font_size"].capitalize(), label=texts["font_size_label"]),
            gr.update(value=new_cfg["chat_height"], label=texts["chat_height_label"]),
            gr.update(height=new_cfg["chat_height"]),
            new_cfg,
            gr.update(choices=self.repo.list_snapshots()),
            gr.update(choices=self.repo.list_trash()),
            gr.update(label=texts["messages_label"], choices=[]),
            gr.update(value=texts["reload_message"]),
            gr.update(value=texts["new_conversation_btn"]),
            gr.update(value=texts["save_snapshot_btn"])
        )

    def _on_language_change(self, lang: str, cfg_dict: Dict[str, Any],
                            history: List[Tuple[str, str]]):
        cfg_dict["interface_language"] = lang
        self.config._data.update(cfg_dict)
        self.config._save()
        texts = TRANSLATIONS[lang]
        opts = self._message_options(history)
        pers_choices = [(texts["personality_names"][k], k) for k in PromptBuilder.PERSONALITIES.keys()]
        return (
            gr.update(value=f"# {texts['title']}"),
            gr.update(value=f"## {texts['subtitle']}"),
            gr.update(choices=pers_choices, label=texts["personality_label"]),
            gr.update(label=texts["response_language_label"]),
            gr.update(label=texts["interface_language_label"]),
            gr.update(label=texts["placeholder"], placeholder=texts["placeholder"]),
            gr.update(value=texts["send_btn"]),
            gr.update(label=texts["chat_height_label"]),
            gr.update(label=texts["font_family_label"]),
            gr.update(label=texts["font_size_label"]),
            gr.update(label=texts["load_dropdown_label"]),
            gr.update(value=texts["delete_btn"]),
            gr.update(value=texts["delete_all_btn"]),
            gr.update(label=texts["trash_label"]),
            gr.update(value=texts["restore_btn"]),
            gr.update(value=texts["empty_trash_btn"]),
            gr.update(label=texts["confirm_label"]),
            gr.update(label=texts["messages_label"], choices=opts, value=[]),
            gr.update(value=texts["delete_msgs_btn"]),
            gr.update(value=texts["reload_message"]),
            cfg_dict,
            gr.update(value=texts["new_conversation_btn"]),
            gr.update(value=texts["save_snapshot_btn"])
        )

    def _save_silent(self, value: str, key: str, cfg_dict: Dict[str, Any]):
        if key in ("font_family", "font_size"):
            cfg_dict[key] = value.lower()
        else:
            cfg_dict[key] = value
        self.config._data.update(cfg_dict)
        self.config._save()
        return cfg_dict

    def _on_chat_height_change(self, height: int, cfg_dict: Dict[str, Any]):
        cfg_dict["chat_height"] = height
        self.config._data.update(cfg_dict)
        self.config._save()
        return cfg_dict, gr.update(height=height)

    def _on_load_initial(self):
        history, err = self.repo.load_current()
        if err:
            return history, gr.update(value=history), gr.update(choices=[]), f"Error: {err}"
        opts = self._message_options(history)
        messages = self._to_messages(history)
        return history, gr.update(value=messages), gr.update(choices=opts), f"Loaded {len(history)} messages"

    def _message_options(self, history: List[Tuple[str, str]]) -> List[str]:
        limited = history[-50:] if len(history) > 50 else history
        return [f"{i}▌user: {u[:30]}..." for i, (u, _) in enumerate(limited)]

    def _parse_idx(self, opt: str) -> int:
        try:
            return int(opt.split("▌")[0])
        except ValueError:
            return -1

    # ======================================================================
    # LAUNCH
    # ======================================================================
    def launch(self, **kwargs) -> None:
        if self.demo is None:
            raise RuntimeError("UI not built")

        kwargs.setdefault('server_name', "0.0.0.0" if os.environ.get("RENDER") else "127.0.0.1")
        kwargs.setdefault('server_port', int(os.environ.get("PORT", 7860)))

        self.demo.launch(
            theme=gr.themes.Default(),
            **kwargs
        )
