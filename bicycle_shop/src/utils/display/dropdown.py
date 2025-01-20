import tkinter as tk

def show_dropdown(event, user_info_frame, dropdown_frame):
    """Position and show the dropdown frame below user info."""
    x = user_info_frame.winfo_rootx()
    y = user_info_frame.winfo_rooty() + user_info_frame.winfo_height() - 10
    
    dropdown_frame.lift()  # Bring to front
    dropdown_frame.update_idletasks()  # Force geometry update
    dropdown_frame.place(x=x, y=y, width=user_info_frame.winfo_width())

def hide_dropdown(event, user_info_frame, dropdown_frame):
    """Hide dropdown based on mouse position."""
    if event is None:
        dropdown_frame.place_forget()
        return
    
    mouse_x = event.x_root
    mouse_y = event.y_root
    
    over_user_info = (
        user_info_frame.winfo_rootx() <= mouse_x <= user_info_frame.winfo_rootx() + user_info_frame.winfo_width() and
        user_info_frame.winfo_rooty() <= mouse_y <= user_info_frame.winfo_rooty() + user_info_frame.winfo_height()
    )
    
    over_dropdown = (
        dropdown_frame.winfo_rootx() <= mouse_x <= dropdown_frame.winfo_rootx() + dropdown_frame.winfo_width() and
        dropdown_frame.winfo_rooty() <= mouse_y <= dropdown_frame.winfo_rooty() + dropdown_frame.winfo_height()
    )
    
    if not (over_user_info or over_dropdown):
        dropdown_frame.place_forget()

def hide_dropdown_on_click(event, user_info_frame, dropdown_frame):
    """Hide dropdown when clicking outside."""
    mouse_x = event.x_root
    mouse_y = event.y_root
    
    over_user_info = (
        user_info_frame.winfo_rootx() <= mouse_x <= user_info_frame.winfo_rootx() + user_info_frame.winfo_width() and
        user_info_frame.winfo_rooty() <= mouse_y <= user_info_frame.winfo_rooty() + user_info_frame.winfo_height()
    )
    
    over_dropdown = (
        dropdown_frame.winfo_rootx() <= mouse_x <= dropdown_frame.winfo_rootx() + dropdown_frame.winfo_width() and
        dropdown_frame.winfo_rooty() <= mouse_y <= dropdown_frame.winfo_rooty() + dropdown_frame.winfo_height()
    )
    
    if not (over_user_info or over_dropdown):
        dropdown_frame.place_forget()

def update_dropdown_position(window, user_info_frame, dropdown_frame):
    """Update dropdown position relative to user info frame."""
    try:
        if dropdown_frame.winfo_ismapped():
            # Get window-relative coordinates for proper positioning
            x = user_info_frame.winfo_rootx() - window.winfo_rootx()
            y = (user_info_frame.winfo_rooty() + user_info_frame.winfo_height() + 20) - window.winfo_rooty()
            
            # Update position relative to main window
            dropdown_frame.place(
                x=x,
                y=y,
                width=user_info_frame.winfo_width()
            )
            # Ensure dropdown stays on top
            dropdown_frame.lift()
    except tk.TclError:
        pass