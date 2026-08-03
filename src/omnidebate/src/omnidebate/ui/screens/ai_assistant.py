"""AI Assistant Screen — Interactive Oracle Chat for Debate Prep.

Provides a split-layout chat interface where debaters can converse with the
local Ollama AI model (nicknamed *Oracle*).  Supports pre-built prompt
templates via ``/`` commands for common debate-prep workflows.

Uses :func:`omnishared.ai.client.generate_completion` for AI responses and
handles :class:`omnishared.ai.client.OllamaOfflineError` gracefully with a
visible error banner.

© 2026 OmniSuite. Built for the Digital Grandmaster.
"""

from __future__ import annotations

from omnishared.ai.client import OllamaOfflineError, generate_completion
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, Static

# ── Constants ────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are Oracle, an expert competitive debate coach and strategist. "
    "You help debaters analyze arguments, find weaknesses, strengthen cases, "
    "and prepare for rounds. Be concise, strategic, and insightful. "
    "Use debate terminology (contention, warrant, impact, turn, link, "
    "uniqueness) accurately."
)

PROMPT_TEMPLATES: dict[str, dict[str, str]] = {
    "/summarize": {
        "label": "Summarize",
        "prefix": (
            "Please provide a concise strategic summary of the following "
            "debate evidence, highlighting the key claim, warrant, and impact:\n\n"
        ),
    },
    "/counter": {
        "label": "Counter-Arguments",
        "prefix": (
            "Generate 3–5 strong counter-arguments against the following "
            "position. For each, provide a link story and impact:\n\n"
        ),
    },
    "/strengthen": {
        "label": "Strengthen",
        "prefix": (
            "Suggest specific ways to strengthen the following argument. "
            "Identify weaknesses in the link chain and propose additional "
            "warrants or evidence angles:\n\n"
        ),
    },
    "/impact": {
        "label": "Impact Analysis",
        "prefix": (
            "Analyze the impact chain of the following argument. Identify "
            "the terminal impact, assess probability, timeframe, magnitude, "
            "and reversibility:\n\n"
        ),
    },
    "/brief": {
        "label": "Case Outline",
        "prefix": (
            "Generate a structured case outline based on the following topic "
            "or argument. Include contentions, sub-points, warrants, and "
            "impacts in a debate-ready format:\n\n"
        ),
    },
}


# ── Widgets ──────────────────────────────────────────────────────────────────


class ChatMessage(Static):
    """A single chat message bubble.

    Displays with a role label (``[You]`` or ``[Oracle]``) and appropriate
    styling based on the message sender.
    """

    DEFAULT_CSS = """
    ChatMessage {
        width: 100%;
        padding: 1 2;
        margin-bottom: 1;
        height: auto;
    }
    ChatMessage.user-message {
        background: $primary-background-darken-2;
        border-left: thick $primary;
    }
    ChatMessage.oracle-message {
        background: $success-background-darken-2;
        border-left: thick $success;
    }
    ChatMessage.error-message {
        background: $error-background-darken-2;
        border-left: thick $error;
    }
    ChatMessage.system-message {
        background: $surface-lighten-1;
        border-left: thick $warning;
        color: $text-muted;
    }
    """

    def __init__(self, role: str, content: str, **kwargs) -> None:
        self.role = role
        self.content = content
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        """Render the message with role prefix."""
        role_label = {
            "user": "[You]",
            "oracle": "[Oracle]",
            "error": "[Error]",
            "system": "[System]",
        }.get(self.role, f"[{self.role}]")

        yield Label(f"{role_label}  {self.content}")


# ── Main Screen ──────────────────────────────────────────────────────────────


class AIAssistantScreen(Screen):
    """Interactive AI chat panel for debate preparation.

    Layout
    ------
    - **Top**: Scrollable chat history showing user and Oracle messages.
    - **Bottom**: Input area for composing messages.

    Prompt Templates (``/`` commands)
    ---------------------------------
    - ``/summarize`` — Summarize selected card text
    - ``/counter`` — Generate counter-arguments
    - ``/strengthen`` — Suggest ways to strengthen an argument
    - ``/impact`` — Analyze impact chain
    - ``/brief`` — Generate case outline

    Type a ``/`` command followed by your text, e.g.:
    ``/counter Free trade increases economic growth``

    Keyboard shortcuts
    ------------------
    - ``Enter`` — send message
    - ``Escape`` — back to main screen
    """

    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
    ]

    DEFAULT_CSS = """
    AIAssistantScreen {
        layout: vertical;
    }
    #chat-container {
        height: 1fr;
    }
    #chat-history {
        height: 1fr;
        padding: 1 2;
        border: solid $surface-lighten-2;
        scrollbar-gutter: stable;
    }
    #chat-input-area {
        dock: bottom;
        height: auto;
        max-height: 6;
        padding: 1 2;
        background: $surface;
        border-top: solid $accent;
    }
    #chat-input-area Label {
        margin-bottom: 1;
    }
    #loading-indicator {
        dock: bottom;
        height: 1;
        background: $warning-darken-2;
        color: $text;
        padding: 0 2;
        display: none;
    }
    #loading-indicator.visible {
        display: block;
    }
    #template-hints {
        dock: bottom;
        height: auto;
        padding: 0 2;
        background: $surface-lighten-1;
        color: $text-muted;
    }
    """

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._messages: list[dict[str, str]] = []
        self._is_generating: bool = False

    # ── Compose ──────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        """Build the AI assistant screen layout."""
        yield Header(show_clock=True)

        with Vertical(id="chat-container"):
            with VerticalScroll(id="chat-history"):
                pass  # Messages mounted dynamically

            yield Static("⏳ Oracle is thinking…", id="loading-indicator")

            yield Static(
                "💡 Commands: /summarize · /counter · /strengthen · /impact · /brief  │  "
                "Type freely for general questions",
                id="template-hints",
            )

            with Vertical(id="chat-input-area"):
                yield Input(
                    placeholder="Ask Oracle anything, or use /command…",
                    id="chat-input",
                )

        yield Footer()

    def on_mount(self) -> None:
        """Display a welcome message when the screen mounts."""
        welcome = (
            "Welcome to Oracle AI Assistant. I'm your debate prep partner. "
            "Ask me anything about arguments, strategy, or use a /command:\n"
            "  /summarize · /counter · /strengthen · /impact · /brief"
        )
        self._add_message("system", welcome, css_class="system-message")
        self.query_one("#chat-input", Input).focus()

    # ── Message Display ──────────────────────────────────────────────────

    def _add_message(
        self,
        role: str,
        content: str,
        css_class: str = "",
    ) -> None:
        """Append a message to the chat history and scroll to bottom.

        Args:
            role: Message sender (``"user"``, ``"oracle"``, ``"error"``,
                ``"system"``).
            content: The message text.
            css_class: Optional CSS class for styling.
        """
        self._messages.append({"role": role, "content": content})

        class_name = css_class or {
            "user": "user-message",
            "oracle": "oracle-message",
            "error": "error-message",
            "system": "system-message",
        }.get(role, "")

        msg_widget = ChatMessage(role=role, content=content, classes=class_name)

        try:
            history = self.query_one("#chat-history", VerticalScroll)
            history.mount(msg_widget)
            # Scroll to the newest message
            self.call_after_refresh(lambda: history.scroll_end(animate=False))
        except Exception:
            pass

    def _set_loading(self, loading: bool) -> None:
        """Toggle visibility of the loading indicator.

        Args:
            loading: ``True`` to show, ``False`` to hide.
        """
        self._is_generating = loading
        try:
            indicator = self.query_one("#loading-indicator", Static)
            indicator.set_class(loading, "visible")
        except Exception:
            pass

        # Disable/enable input while generating
        try:
            inp = self.query_one("#chat-input", Input)
            inp.disabled = loading
        except Exception:
            pass

    # ── Input Handling ───────────────────────────────────────────────────

    @on(Input.Submitted, "#chat-input")
    def _handle_send(self, event: Input.Submitted) -> None:
        """Process user input: detect slash commands or plain messages."""
        raw = event.value.strip()
        if not raw:
            return

        # Clear the input immediately
        event.input.value = ""

        if self._is_generating:
            self.app.notify("Please wait for Oracle to finish responding.", severity="warning")
            return

        # Check for slash commands
        prompt_text = raw
        template_prefix = ""

        for cmd, template in PROMPT_TEMPLATES.items():
            if raw.lower().startswith(cmd):
                remaining = raw[len(cmd) :].strip()
                if not remaining:
                    self.app.notify(
                        f"Usage: {cmd} <your text>",
                        severity="warning",
                    )
                    return
                template_prefix = template["prefix"]
                prompt_text = remaining
                self._add_message(
                    "user",
                    f"[{template['label']}] {remaining}",
                    css_class="user-message",
                )
                break
        else:
            # Plain message — no command matched
            self._add_message("user", raw, css_class="user-message")

        # Construct the full prompt
        full_prompt = f"{template_prefix}{prompt_text}" if template_prefix else prompt_text

        # Launch async AI generation
        self._generate_response(full_prompt)

    @work(thread=True, exclusive=True, group="oracle")
    def _generate_response(self, prompt: str) -> None:
        """Call the AI backend in a worker thread.

        Runs :func:`generate_completion` off the main thread to keep the TUI
        responsive.  Posts results back via :meth:`call_from_thread`.

        Args:
            prompt: The full prompt string to send to the model.
        """
        self.call_from_thread(self._set_loading, True)

        try:
            response = generate_completion(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
                timeout=60.0,
            )
            self.call_from_thread(self._add_message, "oracle", response, "oracle-message")
        except OllamaOfflineError as exc:
            error_msg = (
                f"Oracle is offline. Please ensure Ollama is running locally.\nDetails: {exc}"
            )
            self.call_from_thread(self._add_message, "error", error_msg, "error-message")
        except Exception as exc:
            error_msg = f"Unexpected error: {exc}"
            self.call_from_thread(self._add_message, "error", error_msg, "error-message")
        finally:
            self.call_from_thread(self._set_loading, False)

    # ── Navigation ───────────────────────────────────────────────────────

    def action_go_back(self) -> None:
        """Pop back to the main screen."""
        self.app.pop_screen()
