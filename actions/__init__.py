from .goto import handle_goto
from .click import handle_click
from .fill import handle_fill
from .keyboard_press import handle_keyboard_press
from .wait import handle_wait
from .scroll import handle_scroll
from .screenshot import handle_screenshot
from .extract import handle_extract
from .dismiss_popup import handle_dismiss_popup

ACTION_HANDLERS = {
    "goto": handle_goto,
    "click": handle_click,
    "fill": handle_fill,
    "keyboard_press": handle_keyboard_press,
    "wait": handle_wait,
    "scroll": handle_scroll,
    "screenshot": handle_screenshot,
    "extract": handle_extract,
    "dismiss_popup": handle_dismiss_popup,
}

