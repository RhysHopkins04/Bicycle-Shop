import tkinter as tk
from ..theme import get_style_config, get_default_button_style

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

def toggle_password_visibility(entry, button, show, eye_open_image, eye_closed_image):
    """Toggle the visibility of the password."""
    if entry.cget('show') == '':
        entry.config(show=show)
        button.config(image=eye_closed_image)
    else:
        entry.config(show='')
        button.config(image=eye_open_image)

def create_password_field(parent, label_text, entry_width=16, show_label=True, eye_open_image=None, eye_closed_image=None, style="dark"):
    """Create a password entry field with toggle visibility button"""
    style_config = get_style_config()['password_field']
    current_style = style_config.get(style, style_config["dark"])

    if show_label:
        tk.Label(parent, text=label_text, 
                bg=current_style["bg"], 
                fg=current_style["fg"]).pack()
    
    frame = tk.Frame(parent, bg=current_style["frame_bg"]) 
    frame.pack(pady=5)
    
    entry = tk.Entry(frame, show="*", width=entry_width,
                    bg=current_style["entry_bg"],
                    fg=current_style["entry_fg"])
    entry.pack(side="left", padx=5)
    
    button = tk.Button(frame, image=eye_closed_image, 
                      command=lambda: toggle_password_visibility(entry, button, '*', eye_open_image, eye_closed_image),
                      takefocus=False,
                      bg=current_style["button_bg"],
                      activebackground=current_style["button_bg"])
    button.pack()
    
    return entry, frame, button

def setup_search_widget(parent, placeholder="Search for products", font_size=20):
    """Create and setup search entry with placeholder"""
    style = get_style_config()['search']
    search_frame = tk.Frame(parent, bg=style['frame_bg'])
    search_entry = tk.Entry(
        search_frame, 
        width=style['entry']['width'],
        fg=style['entry']['placeholder_fg'],
        font=("Arial", font_size)
    )
    search_entry.insert(0, placeholder)
    search_entry.pack(pady=10)
    
    def on_focus_in(event):
        if search_entry.get() == placeholder:
            search_entry.delete(0, tk.END)
            search_entry.config(fg=style['entry']['active_fg'])
            
    def on_focus_out(event):
        if search_entry.get() == "":
            search_entry.insert(0, placeholder)
            search_entry.config(fg=style['entry']['placeholder_fg'])
    
    def disable_search():
        search_entry.config(state="disabled")
        search_entry.unbind("<FocusIn>")
        search_entry.unbind("<FocusOut>")
        
    def enable_search():
        search_entry.config(state="normal")
        search_entry.bind("<FocusIn>", on_focus_in)
        search_entry.bind("<FocusOut>", on_focus_out)
    
    search_entry.bind("<FocusIn>", on_focus_in)
    search_entry.bind("<FocusOut>", on_focus_out)
    
    return search_frame, search_entry, disable_search, enable_search

def create_user_info_display(parent, username, first_name, last_name, is_admin, user_icon, admin_icon):
    """Create user info display with labels"""
    style = get_style_config()['user_info']
    user_info_frame = tk.Frame(parent, bg=style['frame_bg'])
    
    icon_label = tk.Label(
        user_info_frame, 
        image=admin_icon if is_admin else user_icon, 
        bg=style['icon_bg']
    )
    icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 5))
    
    name_label = tk.Label(
        user_info_frame, 
        text=f"{first_name} {last_name}", 
        **style['name']
    )
    name_label.grid(row=0, column=1, sticky="w")
    
    username_label = tk.Label(
        user_info_frame, 
        text=f"@{username}", 
        **style['username']
    )
    username_label.grid(row=1, column=1, sticky="w")
    
    dropdown_indicator = tk.Label(
        user_info_frame, 
        text="▼", 
        **style['dropdown']
    )
    dropdown_indicator.grid(row=0, column=2, rowspan=2, padx=(5, 0))
    
    return user_info_frame, icon_label, name_label, username_label, dropdown_indicator