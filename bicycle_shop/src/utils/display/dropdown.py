import tkinter as tk

def show_dropdown(event, user_info_frame, dropdown_frame):
    """Position and show the dropdown frame below user info.
    
    Args:
        event: Mouse event that triggered the dropdown
        user_info_frame: Frame containing user information
        dropdown_frame: Frame containing dropdown menu items
        
    Note:
        Positions dropdown below user info frame
        Forces geometry update to ensure proper rendering
        Brings dropdown to front of window stacking order
    """
    x = user_info_frame.winfo_rootx()
    y = user_info_frame.winfo_rooty() + user_info_frame.winfo_height() - 10
    
    dropdown_frame.lift()  # Bring to front
    dropdown_frame.update_idletasks()  # Force geometry update
    dropdown_frame.place(x=x, y=y, width=user_info_frame.winfo_width())

def hide_dropdown(event, user_info_frame, dropdown_frame):
    """Hide dropdown based on mouse position.
    
    Args:
        event: Mouse event that triggered hide (None for force hide)
        user_info_frame: Frame containing user information  
        dropdown_frame: Frame containing dropdown menu items
        
    Note:
        Hides dropdown if mouse not over user info or dropdown
        Handles force hide when event is None
        Calculates mouse position relative to screen coordinates
    """
    if event is None:
        dropdown_frame.place_forget()
        return
    
    mouse_x = event.x_root
    mouse_y = event.y_root
    
    # Check if the mouse is over the user info frame
    over_user_info = (
        user_info_frame.winfo_rootx() <= mouse_x <= user_info_frame.winfo_rootx() + user_info_frame.winfo_width() and
        user_info_frame.winfo_rooty() <= mouse_y <= user_info_frame.winfo_rooty() + user_info_frame.winfo_height()
    )
    
    # Check if the mouse is over the dropdown frame
    over_dropdown = (
        dropdown_frame.winfo_rootx() <= mouse_x <= dropdown_frame.winfo_rootx() + dropdown_frame.winfo_width() and
        dropdown_frame.winfo_rooty() <= mouse_y <= dropdown_frame.winfo_rooty() + dropdown_frame.winfo_height()
    )
    
    # If the mouse is not over either the user info frame or the dropdown frame, then hide the dropdown
    if not (over_user_info or over_dropdown):
        dropdown_frame.place_forget()

def hide_dropdown_on_click(event, user_info_frame, dropdown_frame):
    """Hide dropdown when clicking outside.
    
    Args:
        event: Mouse click event
        user_info_frame: Frame containing user information
        dropdown_frame: Frame containing dropdown menu items
        
    Note:
        Hides dropdown if click is outside both frames
        Uses screen coordinates for position checking
        Different from hide_dropdown as this handles clicks
    """
    mouse_x = event.x_root
    mouse_y = event.y_root
    
    # Check if the mouse is over the user_info_frame
    over_user_info = (
        user_info_frame.winfo_rootx() <= mouse_x <= user_info_frame.winfo_rootx() + user_info_frame.winfo_width() and
        user_info_frame.winfo_rooty() <= mouse_y <= user_info_frame.winfo_rooty() + user_info_frame.winfo_height()
    )
    
    # Check if the mouse is over the dropdown_frame
    over_dropdown = (
        dropdown_frame.winfo_rootx() <= mouse_x <= dropdown_frame.winfo_rootx() + dropdown_frame.winfo_width() and
        dropdown_frame.winfo_rooty() <= mouse_y <= dropdown_frame.winfo_rooty() + dropdown_frame.winfo_height()
    )
    
    # If the mouse is not over either the user_info_frame or the dropdown_frame, then hide the dropdown
    if not (over_user_info or over_dropdown):
        dropdown_frame.place_forget()

def update_dropdown_position(window, user_info_frame, dropdown_frame):
    """Update dropdown position relative to user info frame.
    
    Args:
        window: Main application window
        user_info_frame: Frame containing user information
        dropdown_frame: Frame containing dropdown menu items
        
    Note:
        Updates position when window moves/resizes
        Calculates position relative to main window
        Handles widget destruction gracefully
        Ensures dropdown stays above other widgets
    """
    try:
        # Check if the dropdown_frame is currently mapped (visible)
        if dropdown_frame.winfo_ismapped():
            # Get window-relative coordinates for proper positioning
            x = user_info_frame.winfo_rootx() - window.winfo_rootx()
            # Get the y-coordinate relative to the main window, placing it below the user_info_frame with an offset of 20 pixels
            y = (user_info_frame.winfo_rooty() + user_info_frame.winfo_height() + 20) - window.winfo_rooty()
            
            # Place the dropdown_frame at the calculated position with the same width as user_info_frame
            dropdown_frame.place(
                x=x,
                y=y,
                width=user_info_frame.winfo_width()
            )
            # Ensure the dropdown_frame stays on top of other widgets
            dropdown_frame.lift()
    except tk.TclError:
        # If there is a TclError (e.g., widget not found), ignore it
        pass