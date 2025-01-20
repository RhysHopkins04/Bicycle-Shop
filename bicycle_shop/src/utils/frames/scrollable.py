import tkinter as tk
from ..theme import get_style_config

def create_scrollable_frame(parent):
    """Create scrollable frame with canvas"""
    style = get_style_config()['scrollable']
    
    wrapper = tk.Frame(parent, bg=style['wrapper_bg'], padx=2, pady=2)
    
    border_frame = tk.Frame(
        wrapper, 
        bg=style['border']['bg'],
        bd=1, 
        relief="solid", 
        highlightthickness=1, 
        highlightbackground=style['border']['highlight']
    )
    border_frame.pack(fill="both", expand=True)
    
    canvas = tk.Canvas(
        border_frame, 
        bg=style['canvas_bg'],
        highlightthickness=0
    )
    
    scrollbar = tk.Scrollbar(border_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=style['frame_bg'])
    
    def on_mouse_wheel(event):
        if canvas.winfo_exists():
            bbox = canvas.bbox("all")
            if bbox:
                scroll_height = bbox[3] - bbox[1]
                visible_height = canvas.winfo_height()
                if scroll_height > visible_height:
                    canvas.yview_scroll(-1 * (event.delta // 120), "units")
    
    def bind_mouse_wheel():
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
    
    def unbind_mouse_wheel():
        canvas.unbind_all("<MouseWheel>")
    
    def on_frame_configure(event):
        bbox = canvas.bbox("all")
        if bbox:
            scroll_height = bbox[3] - bbox[1]
            visible_height = canvas.winfo_height()
            canvas.configure(scrollregion=bbox)
            if scroll_height > visible_height:
                scrollbar.pack(side="right", fill="y", pady=2)
            else:
                scrollbar.pack_forget()
    
    scrollable_frame.bind("<Configure>", on_frame_configure)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="frame")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True, padx=2, pady=2)
    
    return wrapper, canvas, scrollbar, scrollable_frame, bind_mouse_wheel, unbind_mouse_wheel

def create_scrollable_grid_frame(parent):
    """Create scrollable frame with canvas using grid geometry"""
    style = get_style_config()['scrollable']
    
    wrapper = tk.Frame(parent, bg=style['wrapper_bg'])
    wrapper.grid(sticky="nsew")
    wrapper.grid_columnconfigure(0, weight=1)
    wrapper.grid_rowconfigure(0, weight=1)
    
    border_frame = tk.Frame(wrapper, 
                          bg=style['border']['bg'],
                          bd=1, 
                          relief="solid",
                          highlightthickness=1,
                          highlightbackground=style['border']['highlight'])
    border_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
    border_frame.grid_columnconfigure(0, weight=1)
    border_frame.grid_rowconfigure(0, weight=1)
    
    canvas = tk.Canvas(border_frame,
                      bg=style['canvas_bg'],
                      highlightthickness=0)
    canvas.grid(row=0, column=0, sticky="nsew")
    
    scrollbar = tk.Scrollbar(border_frame, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    
    scrollable_frame = tk.Frame(canvas, bg=style['frame_bg'])
    
    def on_canvas_configure(event):
        canvas.itemconfig("frame", width=event.width)
        
    canvas.bind("<Configure>", on_canvas_configure)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="frame")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    def on_mouse_wheel(event):
        if canvas.winfo_exists():
            canvas.yview_scroll(-1 * (event.delta // 120), "units")
    
    def bind_mouse_wheel():
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
    
    def unbind_mouse_wheel():
        canvas.unbind_all("<MouseWheel>")

    return wrapper, canvas, scrollbar, scrollable_frame, bind_mouse_wheel, unbind_mouse_wheel