def display_message(label, message, color, clear_delay=5000, success_callback=None):
    """Display a message with the specified color and auto-clear.
    
    Args:
        label: Label widget to display message in
        message: Message text to display
        color: Text color for message
        clear_delay: Time in ms before message clears (0 for no auto-clear)
        success_callback: Optional callback for success messages
        
    Note:
        Success callbacks only trigger for green messages
        Messages auto-clear after specified delay
        Success messages use shorter default delay
    """
    label.config(text="")
    label.config(text=message, fg=color)
    if success_callback and color == "green":
        label.after(1500, success_callback)
    elif clear_delay > 0:
        label.after(clear_delay, lambda: label.config(text=""))

def display_error(label, message, clear_delay=5000):
    """Display an error message that auto-clears.
    
    Args:
        label: Label widget to display error in  
        message: Error message text to display
        clear_delay: Time in ms before message clears
        
    Note:
        Messages appear in red
        Auto-clears after specified delay
    """
    display_message(label, message, "red", clear_delay)

def display_success(label, message, clear_delay=1500, success_callback=None):
    """Display a success message that auto-clears.
    
    Args:
        label: Label widget to display success in
        message: Success message text to display  
        clear_delay: Time in ms before message clears
        success_callback: Optional callback after success
        
    Note:
        Messages appear in green
        Auto-clears after specified delay
        Can trigger callback after delay
    """
    display_message(label, message, "green", clear_delay, success_callback)