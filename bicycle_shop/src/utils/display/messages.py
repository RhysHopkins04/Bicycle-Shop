def display_message(label, message, color, clear_delay=5000, success_callback=None):
    """Display a message with the specified color and auto-clear."""
    label.config(text="")
    label.config(text=message, fg=color)
    if success_callback and color == "green":
        label.after(1500, success_callback)
    elif clear_delay > 0:
        label.after(clear_delay, lambda: label.config(text=""))

def display_error(label, message, clear_delay=5000):
    """Display an error message that auto-clears."""
    display_message(label, message, "red", clear_delay)

def display_success(label, message, clear_delay=1500, success_callback=None):
    """Display a success message that auto-clears."""
    display_message(label, message, "green", clear_delay, success_callback)