from tkinter import *
from tkinter import filedialog, messagebox
from spellchecker import SpellChecker
import random

spell = SpellChecker()

def new_file(editor):
    editor.delete(1.0, END)

def open_file(editor):
    file_path = filedialog.askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if file_path:
        with open(file_path, "r") as file:
            content = file.read()
            editor.delete(1.0, END)
            editor.insert(INSERT, content)

def save_file(editor):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if file_path:
        with open(file_path, "w") as file:
            file.write(editor.get(1.0, END))

def save_as_file(editor):
    save_file(editor)

def close_file(editor):
    if messagebox.askyesno("Close", "Do you want to save changes before closing?"):
        save_file(editor)
    editor.delete(1.0, END)

def exit_app():
    if messagebox.askokcancel("Quit", "Do you really want to exit?"):
        root.quit()

def undo_action(editor):
    try:
        editor.edit_undo()
    except TclError:
        messagebox.showinfo("Undo", "Nothing to undo!")

def cut_text(editor):
    editor.event_generate("<<Cut>>")

def copy_text(editor):
    editor.event_generate("<<Copy>>")

def paste_text(editor):
    editor.event_generate("<<Paste>>")

def delete_text(editor):
    try:
        editor.delete(SEL_FIRST, SEL_LAST)
    except TclError:
        pass

def select_all(editor):
    editor.tag_add(SEL, "1.0", END)
    editor.mark_set(INSERT, "1.0")
    editor.see(INSERT)

def real_time_spellcheck(editor):
    text_content = editor.get("1.0", "end-1c").split()
    editor.tag_remove("misspelled", "1.0", END)

    for word in text_content:
        if word.lower() not in spell:
            start_index = "1.0"
            while True:
                start_index = editor.search(word, start_index, stopindex=END)
                if not start_index:
                    break
                end_index = f"{start_index}+{len(word)}c"
                editor.tag_add("misspelled", start_index, end_index)
                start_index = end_index

    editor.tag_config("misspelled", foreground="red", underline=True)

def manual_spellcheck(editor):
    real_time_spellcheck(editor)
    messagebox.showinfo("Spellcheck", "Manual spellcheck completed.")

def show_suggestions(event):
    try:
        index = text.index(f"@{event.x},{event.y}") # Checks cursor index
    except TclError:
        return  

    # Find the start and end of the word 
    word_start = text.search(r'\w+', index, stopindex="1.0", backwards=True, regexp=True)
    if not word_start:
        return  

    word_end = text.search(r'\W', word_start, stopindex="end", regexp=True)
    if not word_end:
        word_end = "end"  

    word = text.get(word_start, word_end).strip()

    # Check if the word is misspelled
    if word.lower() not in spell:
        suggestions = spell.candidates(word)
        if not suggestions:
            suggestions = ["No suggestions available"]

        menu = Menu(root, tearoff=0) # Display Suggestions
        for suggestion in suggestions:
            menu.add_command(label=suggestion, command=lambda s=suggestion: replace_word(word_start, word_end, s))
        menu.post(event.x_root, event.y_root)



def replace_word(start, end, replacement): # Replace with selected word
    text.delete(start, end)
    text.insert(start, replacement)

def open_line_generator(): # random list generator
    generator_window = Toplevel(root)
    generator_window.title("Line Generator")
    generator_window.geometry("800x600")

    lines1 = []
    lines2 = []

    def open_file1():
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            with open(file_path, "r") as file:
                content = file.readlines()
                text1.delete(1.0, END)
                text1.insert(INSERT, ''.join(content))
            nonlocal lines1
            lines1 = [line.strip() for line in content if line.strip()]

    def open_file2():
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            with open(file_path, "r") as file:
                content = file.readlines()
                text2.delete(1.0, END)
                text2.insert(INSERT, ''.join(content))
            nonlocal lines2
            lines2 = [line.strip() for line in content if line.strip()]

    def generate_lines():
        try:
            num_lines = int(num_lines_entry.get())
            if num_lines <= 0:
                raise ValueError("Number of lines must be positive.")

            if not lines1 or not lines2:
                raise ValueError("Both files must be loaded before generating.")

            generated_lines = []
            for _ in range(num_lines):
                line1 = random.choice(lines1)
                line2 = random.choice(lines2)
                generated_lines.append(f"{line1} - {line2}")

            text3.delete(1.0, END)
            text3.insert(INSERT, "\n".join(generated_lines))

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", "An unexpected error occurred.")

    # File 1 Section
    frame1 = Frame(generator_window)
    frame1.pack(pady=5)

    Button(frame1, text="Open File 1", command=open_file1).pack(side=LEFT, padx=5)
    text1 = Text(frame1, width=50, height=15, wrap="word")
    text1.pack(side=LEFT, padx=5)

    # File 2 Section
    frame2 = Frame(generator_window)
    frame2.pack(pady=5)

    Button(frame2, text="Open File 2", command=open_file2).pack(side=LEFT, padx=5)
    text2 = Text(frame2, width=50, height=15, wrap="word")
    text2.pack(side=LEFT, padx=5)

    # Control Panel
    frame_controls = Frame(generator_window)
    frame_controls.pack(pady=10)

    Label(frame_controls, text="Number of Lines:").pack(side=LEFT, padx=5)
    num_lines_entry = Entry(frame_controls, width=5)
    num_lines_entry.pack(side=LEFT, padx=5)
    num_lines_entry.insert(0, "5")

    Button(frame_controls, text="Generate Lines", command=generate_lines).pack(side=LEFT, padx=5)

    # Output Section
    frame3 = Frame(generator_window)
    frame3.pack(pady=5)

    Label(frame3, text="Generated Lines:").pack()
    text3 = Text(frame3, width=100, height=15, wrap="word")
    text3.pack(pady=5)

def open_split_editor():
    
    split_window = Toplevel(root)
    split_window.title("Split Text Editor")
    split_window.geometry("1000x600")

   
    pane = PanedWindow(split_window, orient=HORIZONTAL)
    pane.pack(fill=BOTH, expand=1)

    
    text1 = Text(pane, undo=True, wrap="word")
    text2 = Text(pane, undo=True, wrap="word")
    pane.add(text1)
    pane.add(text2)
    text1.bind("<KeyRelease>", lambda event: real_time_spellcheck(text1)) # enable realtime spellcheck
    text2.bind("<KeyRelease>", lambda event: real_time_spellcheck(text2))
    menubar = Menu(split_window)

    # file menu
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="New (Left)", command=lambda: new_file(text1))
    filemenu.add_command(label="New (Right)", command=lambda: new_file(text2))
    filemenu.add_command(label="Open (Left)", command=lambda: open_file(text1))
    filemenu.add_command(label="Open (Right)", command=lambda: open_file(text2))
    filemenu.add_command(label="Save (Left)", command=lambda: save_file(text1))
    filemenu.add_command(label="Save (Right)", command=lambda: save_file(text2))
    filemenu.add_command(label="Close (Left)", command=lambda: close_file(text1))
    filemenu.add_command(label="Close (Right)", command=lambda: close_file(text2))
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=split_window.destroy)
    menubar.add_cascade(label="File", menu=filemenu)

    # Edit menu
    editmenu = Menu(menubar, tearoff=0)
    editmenu.add_command(label="Undo (Left)", command=lambda: undo_action(text1))
    editmenu.add_command(label="Undo (Right)", command=lambda: undo_action(text2))
    editmenu.add_separator()
    editmenu.add_command(label="Cut (Left)", command=lambda: cut_text(text1))
    editmenu.add_command(label="Cut (Right)", command=lambda: cut_text(text2))
    editmenu.add_command(label="Copy (Left)", command=lambda: copy_text(text1))
    editmenu.add_command(label="Copy (Right)", command=lambda: copy_text(text2))
    editmenu.add_command(label="Paste (Left)", command=lambda: paste_text(text1))
    editmenu.add_command(label="Paste (Right)", command=lambda: paste_text(text2))
    editmenu.add_command(label="Delete (Left)", command=lambda: delete_text(text1))
    editmenu.add_command(label="Delete (Right)", command=lambda: delete_text(text2))
    editmenu.add_command(label="Select All (Left)", command=lambda: select_all(text1))
    editmenu.add_command(label="Select All (Right)", command=lambda: select_all(text2))
    menubar.add_cascade(label="Edit", menu=editmenu)

    # tools menu
    toolsmenu = Menu(menubar, tearoff=0)
    toolsmenu.add_command(label="Spellcheck (Left)", command=lambda: manual_spellcheck(text1))
    toolsmenu.add_command(label="Spellcheck (Right)", command=lambda: manual_spellcheck(text2))
    menubar.add_cascade(label="Tools", menu=toolsmenu)
    split_window.config(menu=menubar)

# main window
root = Tk()
root.title("Text Editor with Real-Time Spellcheck")
root.geometry("800x600")
text = Text(root, undo=True, wrap="word")
text.pack(expand=1, fill=BOTH)
text.bind("<KeyRelease>", lambda event: real_time_spellcheck(text))
text.bind("<Button-3>", show_suggestions) #right click error

#menu bar
menubar = Menu(root)

# File menu
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=lambda: new_file(text))
filemenu.add_command(label="Open", command=lambda: open_file(text))
filemenu.add_command(label="Save", command=lambda: save_file(text))
filemenu.add_command(label="Save as...", command=lambda: save_as_file(text))
filemenu.add_command(label="Close", command=lambda: close_file(text))
filemenu.add_separator()
filemenu.add_command(label="Exit", command=exit_app)
menubar.add_cascade(label="File", menu=filemenu)

# Edit menu
editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Undo", command=lambda: undo_action(text))
editmenu.add_separator()
editmenu.add_command(label="Cut", command=lambda: cut_text(text))
editmenu.add_command(label="Copy", command=lambda: copy_text(text))
editmenu.add_command(label="Paste", command=lambda: paste_text(text))
editmenu.add_command(label="Delete", command=lambda: delete_text(text))
editmenu.add_command(label="Select All", command=lambda: select_all(text))
menubar.add_cascade(label="Edit", menu=editmenu)

# Tools menu
toolsmenu = Menu(menubar, tearoff=0)
toolsmenu.add_command(label="Spellcheck", command=lambda: manual_spellcheck(text))  # Manual spellcheck
toolsmenu.add_command(label="Line Generator", command=open_line_generator)  # Line generator
toolsmenu.add_command(label="Split Editor", command=open_split_editor)  # Split editor
menubar.add_cascade(label="Tools", menu=toolsmenu)

# Help menu
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=lambda: messagebox.showinfo("Help", "This is a simple text editor example with spellcheck."))
helpmenu.add_command(label="About...", command=lambda: messagebox.showinfo("About", "Simple Text Editor v1.0\nCreated with Tkinter."))
menubar.add_cascade(label="Help", menu=helpmenu)

root.config(menu=menubar)
root.mainloop()

