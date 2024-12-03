def log_event(event):
    """Log an event to a file."""
    with open("app.log", "a") as f:
        f.write(f"{event}\n")

def display_message(label, message, color):
    """Display a message with the specified color."""
    label.config(text=message, fg=color)

def display_error(label, message):
    """Display an error message."""
    display_message(label, message, "red")

def display_success(label, message):
    """Display a success message."""
    display_message(label, message, "green")