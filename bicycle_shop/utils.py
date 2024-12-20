import tkinter as tk

from file_manager import get_theme

# Logging Feature
def log_event(event):
    """Log an event to a file."""
    with open("app.log", "a") as f:
        f.write(f"{event}\n")

# Display Message Functions:
# Message now has an auto clear after 3s
def display_message(label, message, color, clear_delay=5000, success_callback=None):
    """Display a message with the specified color and auto-clear."""
    # Clear any existing message first
    label.config(text="")
    
    # Show new message
    label.config(text=message, fg=color)
    
    # Handle auto-clear and callbacks
    if success_callback and color == "green":
        label.after(1500, success_callback)
    elif clear_delay > 0:
        label.after(clear_delay, lambda: label.config(text=""))

def display_error(label, message, clear_delay=5000):
    """Display an error message that auto-clears."""
    display_message(label, message, "red", clear_delay)

def display_success(label, message, clear_delay=1000, success_callback=None):
    """Display a success message that auto-clears."""
    display_message(label, message, "green", clear_delay, success_callback)

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

def create_password_field(parent, label_text, entry_width=16, show_label=True, eye_open_image=None, eye_closed_image=None, style="dark"):
    """
    Create a password entry field with toggle visibility button
    
    Args:
        parent: Parent widget
        label_text: Text for label above password field
        entry_width: Width of entry field 
        show_label: Whether to show label
        eye_open_image: Image for password visible
        eye_closed_image: Image for password hidden
    
    Returns:
        tuple: (entry, frame, button)
    """
    # Define styles
    theme = get_theme()
    styles = {
        "dark": {
            "bg": theme['dark_primary'],
            "fg": theme['light_text'],
            "frame_bg": theme['dark_primary'],
            "entry_bg": theme['light_primary'],
            "entry_fg": theme['dark_text']
        },
        "light": {
            "bg": theme['med_primary'],
            "fg": theme['dark_text'], 
            "frame_bg": theme['med_primary'],
            "entry_bg": theme['light_primary'],
            "entry_fg": theme['dark_text']
        }
    }
    
    current_style = styles.get(style, styles["dark"])

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
                      bg=current_style["frame_bg"])
    button.pack()
    
    return entry, frame, button

# Create the gui.py stylings:
def get_style_config():
    """Get application-wide style configuration."""
    theme = get_theme()
    return {
        'login_register_screen': {
            'background': theme['med_primary'],
            'title': {
                'font': ("Arial", 18),
                'bg': theme['med_primary'],
                'fg': theme['dark_text']
            },
            'labels': {
                'bg': theme['med_primary'],
                'fg': theme['dark_text'],
                'font': ("Arial", 10)
            },
            'entries': {
                'bg': theme['light_primary'], 
                'fg': theme['dark_text'],
                'width': 20
            },
            'buttons': {
                'bg': theme['med_primary'],
                'fg': theme['dark_text'],
                'activebackground': theme['med_primary'],
                'activeforeground': theme['dark_text'],
            },
            'message': {
                'bg': theme['med_primary'],
            }
        },
        'store_listing': {
            'top_bar': {
                'bg': theme['dark_primary'],
                'title': {
                    'font': ("Swis721 Blk BT", 40),
                    'bg': theme['dark_primary'],
                    'fg': theme['light_text']
                }
            },
            'dropdown': {
                'frame': {
                    'bg': theme['dark_primary'],
                    'bd': 1,
                    'relief': "solid",
                    'highlightthickness': 1,
                    'highlightbackground': theme['light_text']
                },
                'buttons': {
                    'bg': theme['med_primary'],
                    'fg': theme['dark_text'],
                    'activebackground': theme['med_primary'],
                    'activeforeground': theme['dark_text'],
                },
            },
            'content': {
                'frame_bg': theme['dark_surface'],
                'inner_frame': {
                    'bg': theme['dark_primary'],
                }
            },
            'message': {
                'bg': theme['dark_primary'],
            },
            'frame': {
                'bg': theme['dark_primary'],
            }
        },
        'product_page': {
            'title': {
                'font': ("Arial", 18),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'labels': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'image_frame': {
                'bg': theme['dark_primary']
            },
            'message': {
                'bg': theme['dark_primary']
            }
        },
        'admin_panel': {
            'top_bar': {
                'bg': theme['dark_primary'],
                'title': {
                    'font': ("Swis721 Blk BT", 40),
                    'bg': theme['dark_primary'],
                    'fg': theme['light_text']
                }
            },
            'left_nav': {
                'bg': theme['dark_primary'],
                'title': {
                    'font': ("Arial", 16),
                    'bg': theme['dark_primary'],
                    'fg': theme['med_text']
                }
            },
            'dropdown': {
                'frame': {
                    'bg': theme['dark_primary'],
                    'bd': 1,
                    'relief': "solid",
                    'highlightthickness': 1,
                    'highlightbackground': theme['light_text']
                },
                'buttons': {
                    'bg': theme['med_primary'],
                    'fg': theme['dark_text'],
                    'activebackground': theme['med_primary'],
                    'activeforeground': theme['dark_text'],
                },
            },
            'content': {
                'frame_bg': theme['dark_surface'],
                'inner_frame': {
                    'bg': theme['dark_primary'],
                }
            }
        },
        'add_product': {
            'title': {
                'font': ("Arial", 24, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'labels': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'entries': {
                'bg': theme['light_primary'],
                'fg': theme['dark_text'],
            },
            'combobox': {
                'bg': theme['light_primary'],
                'fg': theme['dark_text'],
                'fieldbackground': theme['light_primary'],
                'selectbackground': theme['dark_secondary'],
                'selectforeground': theme['light_text']
            },
            'buttons': {
                'bg': theme['med_primary'],
                'fg': theme['dark_text'],
                'activebackground': theme['med_primary'],
                'activeforeground': theme['dark_text'],
            },
            'message': {
                'bg': theme['dark_primary']
            }
        },
        'manage_products': {
            'title': {
                'font': ("Arial", 24, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'frame': {
                'bg': theme['dark_primary']
            },
            'search': {
                'frame_bg': theme['dark_primary'],
                'entry': {
                    'bg': theme['light_primary'],
                    'fg': theme['dark_text'],
                    'placeholder_fg': theme['med_text']
                }
            },
            'buttons': {
                'bg': theme['med_primary'],
                'fg': theme['dark_text'],
                'activebackground': theme['med_primary'],
                'activeforeground': theme['dark_text']
            },
            'message': {
                'bg': theme['dark_primary']
            }
        },
        'edit_product': {
            'title': {
                'font': ("Arial", 24, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'labels': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'entries': {
                'bg': theme['light_primary'],
                'fg': theme['dark_text']
            },
            'combobox': {
                'bg': theme['light_primary'],
                'fg': theme['dark_text'],
                'fieldbackground': theme['light_primary'],
                'selectbackground': theme['dark_secondary'],
                'selectforeground': theme['light_text']
            },
            'buttons': {
                'bg': theme['med_primary'],
                'fg': theme['dark_text'],
                'activebackground': theme['med_primary'],
                'activeforeground': theme['dark_text']
            },
            'message': {
                'bg': theme['dark_primary']
            }
        },
        'manage_categories': {
            'title': {
                'font': ("Arial", 24, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'labels': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'entries': {
                'bg': theme['light_primary'],
                'fg': theme['dark_text']
            },
            'frame': {
                'bg': theme['dark_primary']
            },
            'category_frame': {
                'bg': theme['dark_primary']
            },
            'buttons': {
                'bg': theme['med_primary'],
                'fg': theme['dark_text'],
                'activebackground': theme['med_primary'],
                'activeforeground': theme['dark_text']
            },
            'message': {
                'bg': theme['dark_primary']
            }
        },
        'change_password': {
            'light': {
                'title': {
                    'font': ("Arial", 18),
                    'bg': theme['med_primary'],
                    'fg': theme['dark_text']
                },
                'buttons': {
                    'bg': theme['med_primary'],
                    'fg': theme['dark_text'],
                    'activebackground': theme['med_primary'],
                    'activeforeground': theme['dark_text']
                },
                'message': {
                    'bg': theme['med_primary']
                }
            },
            'dark': {
                'title': {
                    'font': ("Arial", 18),
                    'bg': theme['dark_primary'],
                    'fg': theme['light_text']
                },
                'buttons': {
                    'bg': theme['med_primary'],
                    'fg': theme['dark_text'],
                    'activebackground': theme['med_primary'],
                    'activeforeground': theme['dark_text']
                },
                'message': {
                    'bg': theme['dark_primary']
                }
            }
        }
    }

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
    theme = get_theme()
    return {
        "font": ("Arial", 20),
        "bg": theme['dark_primary'],
        "fg": theme['light_primary'],
        "bd": 2,
        "highlightbackground": theme['med_text'],
        "highlightcolor": theme['med_text'],
        "highlightthickness": 2,
        "activebackground": theme['dark_primary'],
        "activeforeground": theme['light_primary'],
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
def create_user_info_display(parent, username, first_name, last_name, is_admin, user_icon, admin_icon):
    """Create user info display with labels"""
    theme = get_theme()
    bg_color=theme['dark_primary']
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
        fg=theme['light_primary']
    )
    name_label.grid(row=0, column=1, sticky="w")
    
    username_label = tk.Label(
        user_info_frame, 
        text=f"@{username}", 
        font=("Arial", 12), 
        bg=bg_color, 
        fg=theme['med_text']
    )
    username_label.grid(row=1, column=1, sticky="w")
    
    dropdown_indicator = tk.Label(
        user_info_frame, 
        text="▼", 
        font=("Arial", 12), 
        bg=bg_color, 
        fg=theme['light_primary']
    )
    dropdown_indicator.grid(row=0, column=2, rowspan=2, padx=(5, 0))
    
    return user_info_frame, icon_label, name_label, username_label, dropdown_indicator

# UI Search Functions
def setup_search_widget(parent, placeholder="Search for products", font_size=20):
    theme = get_theme()
    bg_color=theme['dark_primary']
    """Create and setup search entry with placeholder"""
    search_frame = tk.Frame(parent, bg=bg_color)
    search_entry = tk.Entry(search_frame, width=50, fg=theme['med_text'], font=("Arial", font_size))
    search_entry.insert(0, placeholder)
    search_entry.pack(pady=10)
    
    def on_focus_in(event):
        if search_entry.get() == placeholder:
            search_entry.delete(0, tk.END)
            search_entry.config(fg=theme['dark_text'])
            
    def on_focus_out(event):
        if search_entry.get() == "":
            search_entry.insert(0, placeholder)
            search_entry.config(fg=theme['med_text'])
    
    search_entry.bind("<FocusIn>", on_focus_in)
    search_entry.bind("<FocusOut>", on_focus_out)
    
    return search_frame, search_entry

# UI Scrollable Frame Functions
def create_scrollable_frame(parent):
    """Create scrollable frame with canvas"""
    theme = get_theme()
    bg_color=theme['dark_primary']
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

# UI Product Display Functions:
def setup_product_grid(scrollable_frame, canvas, products, product_width=290, padding=5):
    """Sets up the basic grid layout for products"""
    theme = get_theme()

    if not products:
        message_label = tk.Label(scrollable_frame, text="", bg=theme['dark_primary'])
        message_label.pack(pady=10)
        display_error(message_label, "No products available.")
        return None
        
    canvas.update_idletasks()
    content_width = canvas.winfo_width()
    num_columns = max(1, content_width // (product_width + padding))
    return num_columns

def create_basic_product_frame(row_frame, product, product_width):
    """Creates standard product frame with common elements"""
    theme = get_theme()
    bg_color=theme['dark_primary']
    fg_color=theme['light_primary']

    product_frame = tk.Frame(row_frame, width=product_width, padx=5, pady=5, bg=bg_color)
    product_frame.pack(side="left", padx=5, pady=5)

    tk.Label(product_frame, text=f"Name: {product[1]}", bg=bg_color, fg=fg_color).pack()
    tk.Label(product_frame, text=f"Price: £{product[2]:.2f}", bg=bg_color, fg=fg_color).pack()

    qr_code_image = tk.PhotoImage(file=product[3])
    tk.Label(product_frame, image=qr_code_image, bg=bg_color).pack()
    product_frame.image = qr_code_image
    
    return product_frame

def create_product_management_frame(row_frame, product, product_width, edit_callback, delete_callback):
    """Creates product frame with management buttons"""
    product_frame = create_basic_product_frame(row_frame, product, product_width)
    
    tk.Button(product_frame, text="Edit", 
              command=lambda p=product[0]: edit_callback(p)).pack(side="left")
    tk.Button(product_frame, text="Delete", 
              command=lambda p=product[0]: delete_callback(p)).pack(side="right")
    
    return product_frame
