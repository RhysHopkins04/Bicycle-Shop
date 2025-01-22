import tkinter as tk
from ..theme import get_style_config

def create_scrollable_frame(parent):
    """Create scrollable frame with canvas.
    
    Creates a frame with vertical scrolling capability:
    - Styled wrapper with border
    - Canvas for smooth scrolling
    - Automatic scrollbar visibility
    - Mouse wheel support
    
    Args:
        parent: Parent widget to place scrollable frame in
        
    Returns:
        tuple: (wrapper, canvas, scrollbar, scrollable_frame, bind_wheel, unbind_wheel)
            - wrapper: Outer frame containing everything
            - canvas: Scrollable canvas widget
            - scrollbar: Vertical scrollbar widget
            - scrollable_frame: Frame for content
            - bind_wheel: Function to enable mouse wheel
            - unbind_wheel: Function to disable mouse wheel
    """
    style = get_style_config()['scrollable']
    
    wrapper = tk.Frame(parent, bg=style['wrapper_bg'], padx=2, pady=2)
    
    border_frame = tk.Frame(wrapper, bg=style['border']['bg'], bd=1, relief="solid", highlightthickness=1, highlightbackground=style['border']['highlight'])
    border_frame.pack(fill="both", expand=True)
    
    canvas = tk.Canvas(border_frame, bg=style['canvas_bg'],highlightthickness=0)
    
    scrollbar = tk.Scrollbar(border_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=style['frame_bg'])
    
    def on_mouse_wheel(event):
        """Handle mouse wheel scrolling.
        
        Only scrolls if:
        - Canvas still exists
        - Content height exceeds visible area
        """
        # Check if the canvas widget exists
        if canvas.winfo_exists(): 
            # Get the bounding box of all items on the canvas
            bbox = canvas.bbox("all")
            # If the bounding box is not empty
            if bbox: 
                # Calculate the total scrollable and visible height
                scroll_height = bbox[3] - bbox[1]
                visible_height = canvas.winfo_height()
                # If the content is taller than the visible area
                if scroll_height > visible_height:
                    # Scroll the canvas vertically based on the mouse wheel event
                    canvas.yview_scroll(-1 * (event.delta // 120), "units")
    
    def bind_mouse_wheel():
        """Enable mouse wheel scrolling."""
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
    
    def unbind_mouse_wheel():
        """Disable mouse wheel scrolling."""
        canvas.unbind_all("<MouseWheel>")
    
    def on_frame_configure(event):
        """Update scrollbar and scroll region when frame changes.
        
        Shows scrollbar only when content exceeds visible area
        Updates scroll region to match content size
        """
        # Get the bounding box of all items on the canvas
        bbox = canvas.bbox("all")
        if bbox:
            # Calculate the total height of the scrollable and visible height
            scroll_height = bbox[3] - bbox[1]
            visible_height = canvas.winfo_height()
            # Set the scrollable region of the canvas to the bounding box
            canvas.configure(scrollregion=bbox)
            # Show the scrollbar if the scrollable area is larger than the visible area
            if scroll_height > visible_height:
                scrollbar.pack(side="right", fill="y", pady=2)
            else:
                scrollbar.pack_forget()
    
    scrollable_frame.bind("<Configure>", on_frame_configure)
    # Create a window on the canvas at coordinates (0, 0) with the scrollable_frame as its content, anchored to the northwest corner, and tag it as "frame".
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="frame")
    # Configure the canvas to update the scrollbar when the vertical scroll position changes.
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True, padx=2, pady=2)
    
    return wrapper, canvas, scrollbar, scrollable_frame, bind_mouse_wheel, unbind_mouse_wheel

def create_scrollable_grid_frame(parent):
    """Create scrollable frame using grid geometry manager.
    
    Creates a frame with vertical scrolling capability using grid:
    - Grid-based layout for better control
    - Styled wrapper with border
    - Canvas for smooth scrolling
    - Always visible scrollbar
    - Mouse wheel support
    
    Args:
        parent: Parent widget to place scrollable frame in
        
    Returns:
        tuple: (wrapper, canvas, scrollbar, scrollable_frame, bind_wheel, unbind_wheel)
            - wrapper: Outer frame containing everything
            - canvas: Scrollable canvas widget
            - scrollbar: Vertical scrollbar widget
            - scrollable_frame: Frame for content
            - bind_wheel: Function to enable mouse wheel
            - unbind_wheel: Function to disable mouse wheel
    """
    style = get_style_config()['scrollable']
    
    # Create and configure the wrapper frame
    wrapper = tk.Frame(parent, bg=style['wrapper_bg'])
    wrapper.grid(sticky="nsew")
    wrapper.grid_columnconfigure(0, weight=1)
    wrapper.grid_rowconfigure(0, weight=1)
    
    # Create and configure the border frame
    border_frame = tk.Frame(wrapper, bg=style['border']['bg'],bd=1, relief="solid",highlightthickness=1,highlightbackground=style['border']['highlight'])
    border_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
    border_frame.grid_columnconfigure(0, weight=1)
    border_frame.grid_rowconfigure(0, weight=1)
    
    # Create the canvas and scrollbar widgets
    canvas = tk.Canvas(border_frame, bg=style['canvas_bg'], highlightthickness=0)
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar = tk.Scrollbar(border_frame, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    scrollable_frame = tk.Frame(canvas, bg=style['frame_bg'])
    
    def on_canvas_configure(event):
        """Update canvas window width when canvas is resized."""
        # Adjust the width of the canvas window to match the new width
        canvas.itemconfig("frame", width=event.width)
    
    # Configure the canvas and scrollable frame for vertical scrolling with a scrollbar
    canvas.bind("<Configure>", on_canvas_configure)
    # Update scroll region on frame resize
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    # Create a window on the canvas for the scrollable frame
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="frame")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    def on_mouse_wheel(event):
        """Handle mouse wheel scrolling.
        
        Only scrolls if canvas still exists
        """
        if canvas.winfo_exists(): # Check if the canvas widget exists
            # Scroll the canvas vertically by a number of units based on the mouse wheel delta
            canvas.yview_scroll(-1 * (event.delta // 120), "units")
    
    def bind_mouse_wheel():
        """Enable mouse wheel scrolling."""
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
    
    def unbind_mouse_wheel():
        """Disable mouse wheel scrolling."""
        canvas.unbind_all("<MouseWheel>")

    return wrapper, canvas, scrollbar, scrollable_frame, bind_mouse_wheel, unbind_mouse_wheel