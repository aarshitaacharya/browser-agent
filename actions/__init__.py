# Central registry mapping the action names the LLM (or a test) can emit to
# the handler that executes them. agents/browser_controller.py looks actions
# up here by name; adding a new action type means writing a handler module
# and registering it in this dict.
from .goto import handle_goto
from .click import handle_click
from .fill import handle_fill
from .keyboard_press import handle_keyboard_press
from .wait import handle_wait
from .scroll import handle_scroll
from .screenshot import handle_screenshot
from .dismiss_popup import handle_dismiss_popup

ACTION_HANDLERS = {
    "goto": handle_goto,
    "click": handle_click,
    "fill": handle_fill,
    "keyboard_press": handle_keyboard_press,
    "wait": handle_wait,
    "scroll": handle_scroll,
    "screenshot": handle_screenshot,
    "dismiss_popup": handle_dismiss_popup,
}
