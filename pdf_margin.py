import os
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog
#pip install PyMuPDF

def add_margins_to_pdf(input_pdf, left=0, right=0, top=0, bottom=0):
    """
    Adds margins to all pages of a PDF.
    Output PDF will be saved in the same directory as input with '_margin' added to the filename.

    :param input_pdf: Path to the input PDF file.
    :param left: Left margin in inches.
    :param right: Right margin in inches.
    :param top: Top margin in inches.
    :param bottom: Bottom margin in inches.
    :return: Tuple of (success: bool, message: str, output_path: str or None)
    """
    # Generate output filename by adding '_margin' before the extension
    base_name = os.path.splitext(input_pdf)[0]
    extension = os.path.splitext(input_pdf)[1]
    output_pdf = f"{base_name}_margin{extension}"

    # Convert inches to points (1 inch = 72 points)
    left_pts = left * 72
    right_pts = right * 72
    top_pts = top * 72
    bottom_pts = bottom * 72

    if not os.path.exists(input_pdf):
        return False, f"Error: Input PDF '{input_pdf}' does not exist.", None

    try:
        # Open the input PDF
        doc = fitz.open(input_pdf)

        # Create a new PDF document
        new_doc = fitz.open()

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            rect = page.rect  # Original page rectangle

            # Calculate new page size with margins
            new_width = rect.width + left_pts + right_pts
            new_height = rect.height + top_pts + bottom_pts

            # Create a new page in the new document
            new_page = new_doc.new_page(width=new_width, height=new_height)

            # Define the rectangle where the original page will be placed (with margins)
            dest_rect = fitz.Rect(left_pts, top_pts, left_pts + rect.width, top_pts + rect.height)

            # Show the original page on the new page
            new_page.show_pdf_page(dest_rect, doc, page_num)

        # Save the new PDF
        new_doc.save(output_pdf)
        new_doc.close()
        doc.close()

        return True, f"Successfully added margins and saved as '{os.path.basename(output_pdf)}'.", output_pdf

    except Exception as e:
        return False, f"Error processing PDF: {e}", None


class CustomButton(tk.Canvas):
    """Custom button widget with guaranteed color rendering"""
    def __init__(self, parent, text, command, bg, hover_bg, fg, font, **kwargs):
        # Calculate size based on text
        padding_x = kwargs.get('padx', 30)
        padding_y = kwargs.get('pady', 15)

        # Create temporary label to measure text size
        temp_label = tk.Label(parent, text=text, font=font)
        temp_label.update_idletasks()
        text_width = temp_label.winfo_reqwidth()
        text_height = temp_label.winfo_reqheight()
        temp_label.destroy()

        width = text_width + padding_x * 2
        height = text_height + padding_y * 2

        super().__init__(parent, width=width, height=height,
                        bg=parent.cget('bg'), highlightthickness=0, cursor="hand2")

        self.text = text
        self.command = command
        self.normal_bg = bg
        self.hover_bg = hover_bg
        self.fg = fg
        self.font = font
        self.is_enabled = True

        # Draw button
        self.rect = self.create_rectangle(0, 0, width, height, fill=bg, outline="")
        self.text_item = self.create_text(width//2, height//2, text=text,
                                         fill=fg, font=font)

        # Bind events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def on_enter(self, _):
        if self.is_enabled:
            self.itemconfig(self.rect, fill=self.hover_bg)

    def on_leave(self, _):
        if self.is_enabled:
            self.itemconfig(self.rect, fill=self.normal_bg)

    def on_click(self, _):
        if self.is_enabled and self.command:
            # Visual click feedback
            self.itemconfig(self.rect, fill=self.hover_bg)
            self.after(100, lambda: self.reset_and_call())

    def reset_and_call(self):
        if self.is_enabled:
            self.itemconfig(self.rect, fill=self.normal_bg)
        self.command()

    def set_enabled(self, enabled):
        self.is_enabled = enabled
        if enabled:
            self.itemconfig(self.rect, fill=self.normal_bg)
            self.config(cursor="hand2")
        else:
            self.itemconfig(self.rect, fill="#95a5a6")
            self.config(cursor="arrow")

    def set_text(self, new_text):
        self.text = new_text
        self.itemconfig(self.text_item, text=new_text)


class PDFMarginGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Margin Editor")
        self.root.geometry("700x650")
        self.root.resizable(False, False)

        # Configure colors
        self.bg_color = "#f5f6fa"
        self.primary_color = "#4834d4"
        self.primary_hover = "#6c5ce7"
        self.success_color = "#26de81"
        self.success_hover = "#20bf6b"
        self.error_color = "#fc5c65"
        self.text_color = "#2f3640"

        self.root.configure(bg=self.bg_color)

        # Font family - try SF Pro, fallback to system fonts
        self.font_family = "SF Pro Display"
        try:
            # Test if SF Pro is available
            import tkinter.font as tkfont
            available_fonts = tkfont.families()
            if self.font_family not in available_fonts:
                # Try alternatives
                for font in ["SF Pro Text", "Helvetica Neue", "Segoe UI", "Arial"]:
                    if font in available_fonts:
                        self.font_family = font
                        break
        except:
            self.font_family = "Helvetica"

        # Selected file path
        self.selected_file = None

        self.create_widgets()

    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.root, bg=self.primary_color, height=100)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="PDF Margin Editor",
            font=(self.font_family, 36, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        title_label.pack(expand=True)

        # Main content frame
        content_frame = tk.Frame(self.root, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=35)

        # File selection section
        file_frame = tk.Frame(content_frame, bg=self.bg_color)
        file_frame.pack(fill=tk.X, pady=(0, 25))

        self.select_btn = CustomButton(
            file_frame,
            text="Select PDF File",
            command=self.select_file,
            bg=self.primary_color,
            hover_bg=self.primary_hover,
            fg="white",
            font=(self.font_family, 18, "bold"),
            padx=35,
            pady=18
        )
        self.select_btn.pack(pady=(0, 15))

        # Selected file display
        self.file_label = tk.Label(
            file_frame,
            text="No file selected",
            font=(self.font_family, 15),
            bg=self.bg_color,
            fg="#95a5a6",
            wraplength=620
        )
        self.file_label.pack()

        # Margin inputs section
        margin_frame = tk.LabelFrame(
            content_frame,
            text="  Margins (inches)  ",
            font=(self.font_family, 17, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
            padx=30,
            pady=20
        )
        margin_frame.pack(fill=tk.X, pady=(0, 25))

        # Create grid for margin inputs
        margins = [
            ("Left:", "left"),
            ("Right:", "right"),
            ("Top:", "top"),
            ("Bottom:", "bottom")
        ]

        self.margin_entries = {}

        for i, (label_text, key) in enumerate(margins):
            row = i // 2
            col = (i % 2) * 2

            label = tk.Label(
                margin_frame,
                text=label_text,
                font=(self.font_family, 16),
                bg=self.bg_color,
                fg=self.text_color
            )
            label.grid(row=row, column=col, sticky=tk.W, padx=(0, 15), pady=12)

            entry = tk.Entry(
                margin_frame,
                font=(self.font_family, 16),
                width=12,
                relief=tk.SOLID,
                borderwidth=2
            )
            entry.insert(0, "0")
            entry.grid(row=row, column=col+1, sticky=tk.W, padx=(0, 40), pady=12)

            self.margin_entries[key] = entry

        # Run button
        self.run_btn = CustomButton(
            content_frame,
            text="Run Conversion",
            command=self.run_conversion,
            bg=self.primary_color,
            hover_bg=self.primary_hover,
            fg="white",
            font=(self.font_family, 19, "bold"),
            padx=45,
            pady=18
        )
        self.run_btn.pack(pady=(0, 20))

        # Status label
        self.status_label = tk.Label(
            content_frame,
            text="",
            font=(self.font_family, 15, "bold"),
            bg=self.bg_color,
            wraplength=620
        )
        self.status_label.pack()

    def select_file(self):
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if filename:
            self.selected_file = filename
            self.file_label.config(
                text=f"Selected: {os.path.basename(filename)}",
                fg=self.text_color
            )
            self.status_label.config(text="")

    def run_conversion(self):
        if not self.selected_file:
            self.status_label.config(
                text="Please select a PDF file first!",
                fg=self.error_color
            )
            return

        # Get margin values
        try:
            left = float(self.margin_entries["left"].get())
            right = float(self.margin_entries["right"].get())
            top = float(self.margin_entries["top"].get())
            bottom = float(self.margin_entries["bottom"].get())
        except ValueError:
            self.status_label.config(
                text="Please enter valid numbers for margins!",
                fg=self.error_color
            )
            return

        # Disable button during processing
        self.run_btn.set_enabled(False)
        self.run_btn.set_text("Processing...")
        self.root.update()

        # Process PDF
        success, message, _ = add_margins_to_pdf(
            self.selected_file, left, right, top, bottom
        )

        # Update status
        if success:
            self.status_label.config(
                text=f"Conversion Successful!\n{message}",
                fg=self.success_color
            )
        else:
            self.status_label.config(
                text=f"Conversion Failed!\n{message}",
                fg=self.error_color
            )

        # Re-enable button
        self.run_btn.set_text("Run Conversion")
        self.run_btn.set_enabled(True)


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFMarginGUI(root)
    root.mainloop()
