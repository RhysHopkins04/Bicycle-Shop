def center_window(window, width, height):
    """Center a window on the screen.
    
    Args:
        window: Tkinter window to center
        width: Window width in pixels
        height: Window height in pixels
        
    Note:
        Updates window geometry using screen dimensions
        Forces geometry update with update_idletasks()
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.update_idletasks()

def create_fullscreen_handler(window, window_state):
    """Create and bind fullscreen toggle functionality.
    
    Args:
        window: Main application window
        window_state: Dictionary tracking window states containing:
            - is_fullscreen: Boolean tracking fullscreen state
            
    Returns:
        Function that toggles fullscreen when called
        
    Note:
        Binds F11 key to toggle fullscreen
        Returns "break" to prevent event propagation
    """
    def toggle_fullscreen(event=None):
        """Toggle fullscreen state of window.
        
        Args:
            event: Key event that triggered toggle (optional)
            
        Returns:
            str: "break" to prevent event propagation
        """
        window_state['is_fullscreen'] = not window_state['is_fullscreen']
        window.attributes("-fullscreen", window_state['is_fullscreen'])
        return "break"
    window.bind("<F11>", toggle_fullscreen)
    return toggle_fullscreen

def clear_frame(frame):
    """Clear all widgets from the given frame.
    
    Args:
        frame: Frame to clear of widgets
        
    Note:
        Destroys all child widgets in frame
    """
    for widget in frame.winfo_children():
        widget.destroy()