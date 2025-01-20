from src.file_system.config.config_manager import get_theme

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
            'category_labels': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
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
                'font': ("Arial", 24, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'frame': {
                'bg': theme['dark_primary']
            },
            'image_frame': {
                'bg': theme['dark_primary']
            },
            'entries': {
                'bg': theme['light_primary'],
                'fg': theme['dark_text'],
                'insertbackground': theme['dark_text'],
                'relief': 'flat'
            },
            'price': {
                'font': ("Arial", 16, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'labels': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'description': {
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
        },
        'cart': {
            'frame': {
                'bg': theme['dark_primary']
            },
            'labels': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'message': {
                'bg': theme['dark_primary']
            },
            'buttons': {
                'bg': theme['med_primary'],
                'fg': theme['dark_text'],
                'activebackground': theme['med_primary'],
                'activeforeground': theme['dark_text']
            }
        },
        'manage_user': {
            'title': {
                'font': ("Arial", 24, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'frame': {
                'bg': theme['dark_primary']
            },
            'labels': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'entries': {
                'bg': theme['light_primary'],
                'fg': theme['dark_text'],
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
            },
            'dashboard': {
                'section_frame': {
                    'bg': theme['dark_primary'],
                    'bd': 1,
                    'relief': "solid",
                    'padx': 10,
                    'pady': 10
                },
                'section_title': {
                    'font': ("Arial", 16, "bold"),
                    'bg': theme['dark_primary'],
                    'fg': theme['light_text']
                },
                'text': {
                    'font': ("Arial", 12),
                    'bg': theme['dark_primary'],
                    'fg': theme['light_text']
                },
                'log_frame': {
                    'bg': theme['dark_primary'],
                    'relief': "solid",
                    'bd': 1
                },
                'log_title': {
                    'font': ("Arial", 14, "bold"),
                    'bg': theme['dark_primary'],
                    'fg': theme['light_text']
                },
                'log_text': {
                    'bg': theme['light_primary'],
                    'fg': theme['dark_text'],
                    'font': ("Arial", 10)
                },
                'stats_title': {
                    'font': ("Arial", 16, "bold"),
                    'bg': theme['dark_primary'],
                    'fg': theme['light_text']
                },
                'stats_label': {
                    'font': ("Arial", 12),
                    'bg': theme['dark_primary'],
                    'fg': theme['med_text']
                },
                'stats_value': {
                    'font': ("Arial", 14, "bold"),
                    'bg': theme['dark_primary'],
                    'fg': theme['light_text']
                },
                'alert_text': {
                    'font': ("Arial", 12),
                    'bg': theme['dark_primary'],
                    'fg': theme['light_text']
                },
            }
        },
        'add_product': {
            'title': {
                'font': ("Arial", 24, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'frame': {
                'bg': theme['dark_primary']
            },
            'image_frame': {
                'bg': theme['dark_primary']
            },
            'entries': {
                'bg': theme['light_primary'],
                'fg': theme['dark_text']
            },
            'price': {
                'font': ("Arial", 16, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'labels': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
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
            },
            'placeholder': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text'],
                'font': ('Arial', 14),
                'justify': 'center'
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
            'category_labels': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'message': {
                'bg': theme['dark_primary']
            }
        },
        'edit_product': {
            'title': {
                'font': ("Arial", 18, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'frame': {
                'bg': theme['dark_primary']
            },
            'image_frame': {
                'bg': theme['dark_primary']
            },
            'entries': {
                'bg': theme['light_primary'],
                'fg': theme['dark_text']
            },
            'price': {
                'font': ("Arial", 16, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'labels': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
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
            },
            'placeholder': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text'],
                'font': ('Arial', 14),
                'justify': 'center'
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
            },
            'header': {
                'font': ("Arial", 14, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'cell': {
                'font': ('Arial', 10),
                'bg': theme['dark_primary'],
                'fg': theme['light_text'],
                'anchor': 'center',
            }
        },
        'manage_users': {
            'title': {
                'font': ("Arial", 24, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'frame': {
                'bg': theme['dark_primary']
            },
            'user_frame': {
                'bg': theme['dark_primary']
            },
            'header': {
                'font': ("Arial", 14, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'text': {
                'font': ("Arial", 12),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'entries': {
                'bg': theme['light_primary'],
                'fg': theme['dark_text']
            },
            'buttons': {
                'bg': theme['med_primary'],
                'fg': theme['dark_text']
            },
            'message': {
                'bg': theme['dark_primary']
            },
            'cell': {
                'font': ('Arial', 10),
                'bg': theme['dark_primary'],
                'fg': theme['light_text'],
                'anchor': 'center',
            }
        },
        'edit_user_dialog': {
            'dialog': {
                'bg': theme['dark_primary'],
            },
            'frame': {
                'bg': theme['dark_primary'],
            },
            'title': {
                'font': ("Arial", 24, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'labels': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text'],
            },
            'entries': {
                'bg': theme['light_primary'],
                'fg': theme['dark_text'],
            },
            'buttons': {
                'bg': theme['med_primary'],
                'fg': theme['dark_text'],
                'activebackground': theme['med_primary'],
                'activeforeground': theme['dark_text'],
            },
            'combobox': {
                'bg': theme['light_primary'],
                'fg': theme['dark_text'],
                'fieldbackground': theme['light_primary'],
                'selectbackground': theme['light_primary'],
                'selectforeground': theme['dark_text']
            },
            'message': {
                'bg': theme['dark_primary'],
                'fg': 'red',
                'font': ('Arial', 10)
            }
        },
        'manage_discounts': {
            'title': {
                'font': ("Arial", 24, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'frame': {
                'bg': theme['dark_primary']
            },
            'discounts_frame': {
                'bg': theme['dark_primary']
            },
            'header': {
                'font': ("Arial", 14, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'text': {
                'font': ("Arial", 12),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'labels': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text'],
            },
            'entries': {
                'bg': theme['light_primary'],
                'fg': theme['dark_text']
            },
            'buttons': {
                'bg': theme['med_primary'],
                'fg': theme['dark_text'],
                'activebackground': theme['med_primary'],
                'activeforeground': theme['dark_text']
            },
            'message': {
                'bg': theme['dark_primary']
            },
            'cell': {
                'font': ('Arial', 10),
                'bg': theme['dark_primary'],
                'fg': theme['light_text'],
                'anchor': 'center',
            }
        },
        'logging': {
            'title': {
                'font': ("Arial", 24, "bold"),
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'frame': {
                'bg': theme['dark_primary']
            },
            'labels': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
            },
            'text': {
                'bg': theme['light_primary'],
                'fg': theme['dark_text'],
                'font': ("Arial", 12)
            },
            'buttons': {
                'bg': theme['med_primary'],
                'fg': theme['dark_text'],
                'activebackground': theme['med_primary'],
                'activeforeground': theme['dark_text']
            },
            'message': {
                'bg': theme['dark_primary']
            },
            'filters': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text']
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
        },
        'password_field': {
            'dark': {
                'bg': theme['dark_primary'],
                'fg': theme['light_text'],
                'frame_bg': theme['dark_primary'],
                'entry_bg': theme['light_primary'],
                'entry_fg': theme['dark_text'],
                'button_bg': theme['light_primary']
            },
            'light': {
                'bg': theme['med_primary'],
                'fg': theme['dark_text'],
                'frame_bg': theme['med_primary'],
                'entry_bg': theme['light_primary'],
                'entry_fg': theme['dark_text'],
                'button_bg': theme['light_primary']
            }
        },
        'user_info': {
            'frame_bg': theme['dark_primary'],
            'icon_bg': theme['dark_primary'],
            'name': {
                'font': ("Arial", 20),
                'bg': theme['dark_primary'],
                'fg': theme['light_primary']
            },
            'username': {
                'font': ("Arial", 12),
                'bg': theme['dark_primary'],
                'fg': theme['med_text']
            },
            'dropdown': {
                'font': ("Arial", 12),
                'bg': theme['dark_primary'],
                'fg': theme['light_primary']
            }
        },
        'search': {
            'frame_bg': theme['dark_primary'],
            'entry': {
                'width': 50,
                'placeholder_fg': theme['med_text'],
                'active_fg': theme['dark_text']
            }
        },
        'scrollable': {
            'wrapper_bg': theme['dark_primary'],
            'border': {
                'bg': theme['dark_primary'],
                'highlight': theme['light_text']
            },
            'canvas_bg': theme['dark_primary'],
            'frame_bg': theme['dark_primary']
        },
        'product_grid': {
            'frame_bg': theme['dark_primary'],
            'text': {
                'fg': theme['light_primary'],
                'bg': theme['dark_primary']
            },
            'buttons': {
                'bg': theme['med_primary'],
                'fg': theme['dark_text']
            },
            'qr_label': {
                'bg': theme['dark_primary']
            }
        }
    }

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