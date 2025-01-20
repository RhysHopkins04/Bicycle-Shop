def center_window(window, width, height):
    """Center a window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.update_idletasks()

def create_fullscreen_handler(window, window_state):
    """Create and bind fullscreen toggle functionality."""
    def toggle_fullscreen(event=None):
        window_state['is_fullscreen'] = not window_state['is_fullscreen']
        window.attributes("-fullscreen", window_state['is_fullscreen'])
        return "break"
    window.bind("<F11>", toggle_fullscreen)
    return toggle_fullscreen

def clear_frame(frame):
    """Clear all widgets from the given frame."""
    for widget in frame.winfo_children():
        widget.destroy()