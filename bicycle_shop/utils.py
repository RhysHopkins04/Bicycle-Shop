import tkinter as tk

# Logging Feature
def log_event(event):
    """Log an event to a file."""
    with open("app.log", "a") as f:
        f.write(f"{event}\n")

# Display Message Functions:
def display_message(label, message, color):
    """Display a message with the specified color."""
    label.config(text=message, fg=color)

def display_error(label, message):
    """Display an error message."""
    display_message(label, message, "red")

def display_success(label, message):
    """Display a success message."""
    display_message(label, message, "green")

# UI Utility Functions:
# Password visibility toggle
def toggle_password_visibility(entry, button, show, eye_open_image, eye_closed_image):
    """Toggle the visibility of the password."""
    if entry.cget('show') == '':
        entry.config(show=show)
        button.config(image=eye_closed_image)
    else:
        entry.config(show='')
        button.config(image=eye_open_image)

# Function used to dynamically clear and update the frame that is being called for reuseability in the code.
def clear_frame(frame):
    """Clear all widgets from the given frame."""
    for widget in frame.winfo_children():
        widget.destroy()

# Dropdown menu UI Functions:

def show_dropdown(event, user_info_frame, dropdown_frame):
    # Prints below were for debugging process to ensure that the dropdown was working as intended after many failures
    #print("Showing dropdown")

    # Position the dropdown frame below the user_info_frame
    x = user_info_frame.winfo_rootx()
    y = user_info_frame.winfo_rooty() + user_info_frame.winfo_height() - 10
    
    # Ensure the dropdown is properly sized and visible
    dropdown_frame.lift()  # Bring to front
    dropdown_frame.update_idletasks()  # Force geometry update
    dropdown_frame.place(x=x, y=y, width=user_info_frame.winfo_width())
    
    #print(f"Placed dropdown at ({x}, {y})")
    #print(f"Dropdown dimensions: {dropdown_frame.winfo_width()}x{dropdown_frame.winfo_height()}")

def hide_dropdown(event, user_info_frame, dropdown_frame):
    #print("Hide dropdown called")
    if event is None:
        dropdown_frame.place_forget()
        return
    
    # Get the mouse coordinates relative to the screen
    mouse_x = event.x_root
    mouse_y = event.y_root
    #print(f"Mouse position: ({mouse_x}, {mouse_y})")
    
    # Check if the mouse is over either the user_info_frame or dropdown_frame
    over_user_info = (
        user_info_frame.winfo_rootx() <= mouse_x <= user_info_frame.winfo_rootx() + user_info_frame.winfo_width() and
        user_info_frame.winfo_rooty() <= mouse_y <= user_info_frame.winfo_rooty() + user_info_frame.winfo_height()
    )
    
    over_dropdown = (
        dropdown_frame.winfo_rootx() <= mouse_x <= dropdown_frame.winfo_rootx() + dropdown_frame.winfo_width() and
        dropdown_frame.winfo_rooty() <= mouse_y <= dropdown_frame.winfo_rooty() + dropdown_frame.winfo_height()
    )
    
    #print(f"Over user info: {over_user_info}")
    #print(f"Over dropdown: {over_dropdown}")
    
    if not (over_user_info or over_dropdown):
        dropdown_frame.place_forget()

def hide_dropdown_on_click(event, user_info_frame, dropdown_frame):
    #print("hide_dropdown_on_click called")
    # Hide the dropdown frame if clicking outside of it
    mouse_x = event.x_root
    mouse_y = event.y_root
    
    # Check if clicking within user_info_frame or dropdown_frame
    over_user_info = (
        user_info_frame.winfo_rootx() <= mouse_x <= user_info_frame.winfo_rootx() + user_info_frame.winfo_width() and
        user_info_frame.winfo_rooty() <= mouse_y <= user_info_frame.winfo_rooty() + user_info_frame.winfo_height()
    )
    
    over_dropdown = (
        dropdown_frame.winfo_rootx() <= mouse_x <= dropdown_frame.winfo_rootx() + dropdown_frame.winfo_width() and
        dropdown_frame.winfo_rooty() <= mouse_y <= dropdown_frame.winfo_rooty() + dropdown_frame.winfo_height()
    )
    
    #print(f"Click coordinates: ({mouse_x}, {mouse_y})")
    #print(f"Over user info: {over_user_info}")
    #print(f"Over dropdown: {over_dropdown}")
    
    if not (over_user_info or over_dropdown):
        dropdown_frame.place_forget()
        #print("Dropdown hidden on click")

# UI Nav-Button Functions:
def get_default_button_style():
    """Return the default button style dictionary."""
    return {
        "font": ("Arial", 20),
        "bg": "#171d22",
        "fg": "white",
        "bd": 2,
        "highlightbackground": "darkgrey",
        "highlightcolor": "darkgrey",
        "highlightthickness": 2,
        "activebackground": "#171d22",
        "activeforeground": "white"
    }

def create_nav_buttons(parent, button_configs):
    """
    Create navigation buttons with consistent styling.
    
    Args:
        parent: Parent widget to place buttons
        button_configs: List of tuples containing (text, command)
    """
    buttons = []
    button_style = get_default_button_style()
    
    for text, command in button_configs:
        button = tk.Button(parent, text=text, command=command, **button_style)
        buttons.append(button)
    
    # Make all buttons the same width
    max_width = max(button.winfo_reqwidth() for button in buttons)
    for button in buttons:
        button.config(width=max_width - 10)
        button.pack(padx=10, pady=5)

### UI Component Creation Functions ###
def create_user_info_display(parent, username, first_name, last_name, is_admin, user_icon, admin_icon, bg_color="#171d22"):
    """Create user info display with labels"""
    user_info_frame = tk.Frame(parent, bg=bg_color)
    
    icon_label = tk.Label(
        user_info_frame, 
        image=admin_icon if is_admin else user_icon, 
        bg=bg_color
    )
    icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 5))
    
    name_label = tk.Label(
        user_info_frame, 
        text=f"{first_name} {last_name}", 
        font=("Arial", 20), 
        bg=bg_color, 
        fg="white"
    )
    name_label.grid(row=0, column=1, sticky="w")
    
    username_label = tk.Label(
        user_info_frame, 
        text=f"@{username}", 
        font=("Arial", 12), 
        bg=bg_color, 
        fg="darkgrey"
    )
    username_label.grid(row=1, column=1, sticky="w")
    
    dropdown_indicator = tk.Label(
        user_info_frame, 
        text="▼", 
        font=("Arial", 12), 
        bg=bg_color, 
        fg="white"
    )
    dropdown_indicator.grid(row=0, column=2, rowspan=2, padx=(5, 0))
    
    return user_info_frame, icon_label, name_label, username_label, dropdown_indicator

### Search Functions ###
def setup_search_widget(parent, placeholder="Search for products", font_size=20, bg_color="#171d22"):
    """Create and setup search entry with placeholder"""
    search_frame = tk.Frame(parent, bg=bg_color)
    search_entry = tk.Entry(search_frame, width=50, fg="dark gray", font=("Arial", font_size))
    search_entry.insert(0, placeholder)
    search_entry.pack(pady=10)
    
    def on_focus_in(event):
        if search_entry.get() == placeholder:
            search_entry.delete(0, tk.END)
            search_entry.config(fg="black")
            
    def on_focus_out(event):
        if search_entry.get() == "":
            search_entry.insert(0, placeholder)
            search_entry.config(fg="dark gray")
    
    search_entry.bind("<FocusIn>", on_focus_in)
    search_entry.bind("<FocusOut>", on_focus_out)
    
    return search_frame, search_entry

### Scrollable Frame Functions ###
def create_scrollable_frame(parent, bg_color="#171d22"):
    """Create scrollable frame with canvas"""
    # Create a wrapper frame to hold both canvas and scrollbar
    wrapper = tk.Frame(parent, bg=bg_color)
    
    canvas = tk.Canvas(wrapper, bg=bg_color)
    scrollbar = tk.Scrollbar(wrapper, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=bg_color)
    
    def on_mouse_wheel(event):
        if canvas.winfo_exists():
            canvas.yview_scroll(-1 * (event.delta // 120), "units")
    
    def bind_mouse_wheel():
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
    
    def unbind_mouse_wheel():
        canvas.unbind_all("<MouseWheel>")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    return wrapper, canvas, scrollbar, scrollable_frame, bind_mouse_wheel, unbind_mouse_wheel