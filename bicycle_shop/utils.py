def log_event(event):
    """Log an event to a file."""
    with open("app.log", "a") as f:
        f.write(f"{event}\n")