"""
        ============================================================
        RATBAG DEV 2025                              SK-CAPK.DEV
        ------------------------------------------------------------
        Ratbags SQL-Image Rename Tool 
        Version:       1.02
        Released:      18/12/2025
        Last Update:   21/12/2025

        Author:        Bromigo-CAPK@github
        Contributions: Bromigo-CAPK@github
        ============================================================

        This tool compares an SQL data file against image files and
        displays results for easy searching and renaming of images.

        This Current version is for RedM, but theres no reason
        why it couldnt be adapted for FiveM or any other 
        database-driven systems.

        This project is intended as an opensource template.
        Feel free to modify, extend, or add custom filters/settings.

        FEATURES:
            • Recursive image scanning
            • Analysis filters
            • Item name & description display
            • Match detection & suggestions
            • Search bar
            • Batch rename after confirmation
            • Duplicate cleanup after rename
            • Image preview on hover

        HOW TO USE:
            1. Export your item database to SQL
            
            2. Create a root folder
                - Place the SQL file inside
                - Create two subfolders for images

            3. Copy:
                - Images to keep → Folder A
                - New image set  → Folder B
    
            4. Run the app
                - Select SQL file
                - Select root image folder
                - Adjust filters
                - Run analysis
                - Review results
                - Rename as needed

            5. A BACKUP folder is created automatically
                - Previous matches are stored
                - Old backups and copied files are deleted
                
        SETTINGS:
            Only what ive added below if you look hard enuff.
"""


import os
import re
import difflib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

# ---------- SQL Parsing ----------
def parse_sql_items(sql_path):
    items = []
    descriptions = {}
    try:
        with open(sql_path, 'r', encoding='utf-8') as f:
            data = f.read()
        pattern = r"\('([^']+)',\s*'[^']*',\s*\d+,\s*\d+,\s*'[^']*',\s*\d+,\s*\d+,\s*\d+,\s*\d+,\s*'[^']*',\s*'([^']*)'"
        matches = re.findall(pattern, data)
        for item, desc in matches:
            items.append(item.strip())
            descriptions[item.strip()] = desc.strip()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to parse SQL: {e}")
    return items, descriptions

# ---------- Analysis ----------
def analyze(sql_items, image_folder):
    image_files = []
    image_map = {}

    exclude_dirs = {
        #"backup",
        "old_images_backup",
        #"new_rename_output"
    }

    for root_dir, dirs, files in os.walk(image_folder):
        # prevent walking into excluded folders
        dirs[:] = [d for d in dirs if d.lower() not in exclude_dirs]

        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                rel_path = os.path.relpath(os.path.join(root_dir, f), image_folder)
                name_only = os.path.splitext(f)[0]
                image_files.append(name_only)
                image_map[name_only.lower()] = rel_path

    sql_items_lower = [i.lower() for i in sql_items]
    image_files_lower = [f.lower() for f in image_files]

    matched = [i for i, i_l in zip(sql_items, sql_items_lower) if i_l in image_files_lower]
    missing_images = [i for i, i_l in zip(sql_items, sql_items_lower) if i_l not in image_files_lower]
    extra_images = [f for f, f_l in zip(image_files, image_files_lower) if f_l not in sql_items_lower]

    return matched, missing_images, extra_images, image_files, image_map

# ---------- GUI Setup ----------
root = tk.Tk()
root.title("SQL vs Image File Analyzer")
root.geometry("1500x700")

current_img_folder = ""
image_files_all = []
image_map = {}
selected_rows = {}
extra_selected_rows = {}
active_listbox = None
active_search_entry = None
preview_window = None
preview_label = None

# ---------- Filters Variables ----------
ignore_underscore_var = tk.BooleanVar(value=True)
ignore_order_var = tk.BooleanVar(value=False)
use_keyword_var = tk.BooleanVar(value=False)
case_sensitive_var = tk.BooleanVar(value=False)
ignore_double_letters_var = tk.BooleanVar(value=True)
keywords_var = tk.StringVar(value="consumable,tool,item,equipment")

# ---------- Notebook Tabs ----------
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

analyzer_tab = ttk.Frame(notebook)
filters_tab = ttk.Frame(notebook)
extra_images_tab = ttk.Frame(notebook)

notebook.add(analyzer_tab, text="Analyzer")
notebook.add(filters_tab, text="Filters")
notebook.add(extra_images_tab, text="Not in SQL")

# ---------- Filters Tab ----------
ttk.Label(filters_tab, text="Filter Options:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
ttk.Checkbutton(filters_tab, text="Ignore _ / -", variable=ignore_underscore_var).pack(anchor="w", padx=20)
ttk.Checkbutton(filters_tab, text="Ignore double letters (ll→l, ss→s, etc)", variable=ignore_double_letters_var).pack(anchor="w", padx=20)
ttk.Checkbutton(filters_tab, text="Ignore word order", variable=ignore_order_var).pack(anchor="w", padx=20)
ttk.Checkbutton(filters_tab, text="Partial match / keywords", variable=use_keyword_var).pack(anchor="w", padx=20)
ttk.Checkbutton(filters_tab, text="Case Sensitive", variable=case_sensitive_var).pack(anchor="w", padx=20)
ttk.Label(filters_tab, text="Keywords (comma-separated):").pack(anchor="w", padx=10, pady=5)
ttk.Entry(filters_tab, textvariable=keywords_var, width=50).pack(anchor="w", padx=20)

# ---------- Analyzer Tab ----------
frame = ttk.Frame(analyzer_tab, padding=10)
frame.pack(fill="x")

sql_path_var = tk.StringVar()
img_folder_var = tk.StringVar()

# File selection
ttk.Label(frame, text="SQL File:").grid(row=0, column=0, sticky="w")
ttk.Entry(frame, textvariable=sql_path_var, width=80).grid(row=0, column=1, padx=5)
ttk.Button(frame, text="Browse", command=lambda: sql_path_var.set(filedialog.askopenfilename(filetypes=[("SQL files","*.sql"),("All files","*.*")]))).grid(row=0, column=2)

ttk.Label(frame, text="Image Folder:").grid(row=1, column=0, sticky="w")
ttk.Entry(frame, textvariable=img_folder_var, width=80).grid(row=1, column=1, padx=5)
ttk.Button(frame, text="Browse", command=lambda: img_folder_var.set(filedialog.askdirectory())).grid(row=1, column=2)

# ---------- Treeview ----------
# MODIFIED: New order: Status - Description - Item - Search - Suggestions - Select
columns = ("Status","Description","Item","Search","Suggestions","Select")
tree_frame = ttk.Frame(analyzer_tab)
tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
for col in columns:
    tree.heading(col, text=col, command=lambda c=col: toggle_select_all() if c=="Select" else None)
    if col=="Select":
        tree.column(col, width=50, anchor="center")
    elif col in ("Item","Description"):
        tree.column(col, width=250)
    elif col=="Search":
        tree.column(col, width=150)
    # The 'Status' and 'Suggestions' columns will use the default width=200
    else:
        tree.column(col, width=200) 
tree.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# ---------- Extra Images Treeview ----------
extra_columns = ("Select","Image","Path")
extra_tree_frame = ttk.Frame(extra_images_tab)
extra_tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

extra_tree = ttk.Treeview(extra_tree_frame, columns=extra_columns, show="headings", selectmode="browse")
for col in extra_columns:
    extra_tree.heading(col, text=col, command=lambda c=col: toggle_extra_select_all() if c=="Select" else None)
    if col=="Select":
        extra_tree.column(col, width=50, anchor="center")
    elif col=="Image":
        extra_tree.column(col, width=300)
    else:
        extra_tree.column(col, width=500)
extra_tree.pack(side="left", fill="both", expand=True)

extra_scrollbar = ttk.Scrollbar(extra_tree_frame, orient="vertical", command=extra_tree.yview)
extra_tree.configure(yscroll=extra_scrollbar.set)
extra_scrollbar.pack(side="right", fill="y")

# ---------- Preview ----------
def show_preview(name):
    global preview_window, preview_label
    if not name or name=="None":
        hide_preview()
        return
    path = image_map.get(name.lower())
    if path is None:
        path = os.path.join(current_img_folder, f"{name}.png")
    else:
        path = os.path.join(current_img_folder, path)
    if not os.path.isfile(path):
        hide_preview()
        return
    if preview_window is None:
        preview_window = tk.Toplevel(root)
        preview_window.overrideredirect(True)
        preview_label = tk.Label(preview_window, bd=2, relief="solid")
        preview_label.pack()
    img = Image.open(path)
    img.thumbnail((200,200))
    preview_label.img = ImageTk.PhotoImage(img)
    preview_label.config(image=preview_label.img)
    x = root.winfo_rootx() + root.winfo_width() - 220
    y = root.winfo_rooty() + 30
    preview_window.geometry(f"+{x}+{y}")
    preview_window.lift()

def hide_preview(event=None):
    global preview_window
    if preview_window:
        preview_window.destroy()
        preview_window=None


def on_motion(event):
    row_id = tree.identify_row(event.y)
    col = tree.identify_column(event.x)
    if row_id:
        values = tree.item(row_id)['values']
        if len(values) < 6:
            hide_preview()
            return
        col_index = int(col.replace("#",""))-1
        # Item name for preview is at data index [2]
        if col_index in (1, 2):  # Hovering over Description (#2, index 1) or Item (#3, index 2)
            show_preview(values[2]) 
        # Suggestions name for preview is at data index [4]
        elif col_index == 4:     # Hovering over Suggestions (#5, index 4)
            val = values[4]
            show_preview(val if val!="None" else None)
        else:
            hide_preview()
    else:
        hide_preview()

def on_extra_motion(event):
    row_id = extra_tree.identify_row(event.y)
    col = extra_tree.identify_column(event.x)
    if row_id:
        values = extra_tree.item(row_id)['values']
        if len(values) < 2:
            hide_preview()
            return
        col_index = int(col.replace("#",""))-1
        if col_index == 1:  # Image column
            show_preview(values[1])
        else:
            hide_preview()
    else:
        hide_preview()

tree.bind("<Motion>", on_motion)
tree.bind("<Leave>", hide_preview)
extra_tree.bind("<Motion>", on_extra_motion)
extra_tree.bind("<Leave>", hide_preview)

# ---------- Filters & Matching ----------
def normalize_name(name):
    if ignore_underscore_var.get():
        return name.replace("_"," ").replace("-"," ")
    return name

def normalize_double_letters(text):
    """Normalize double letters to single (aa→a, bb→b, etc) for comparison"""
    if not ignore_double_letters_var.get():
        return text
    import re
    # Replace any double letter with single letter
    return re.sub(r'(.)\1+', r'\1', text)

def compare_strings(str1, str2, check_double_letters=True):
    """Compare two strings with optional double letter normalization"""
    if str1 == str2:
        return True
    if check_double_letters and ignore_double_letters_var.get():
        return normalize_double_letters(str1) == normalize_double_letters(str2)
    return False

def suggest_match(item, image_files):
    kw_list = [k.strip() for k in keywords_var.get().split(",") if k.strip()]
    item_norm = normalize_name(item)

    suggestions_with_priority = []          # (priority, img, reasons)
    match_reasons = {}

    for img in image_files:
        img_norm = normalize_name(img)

        # ------------------------------------------------------------------
        # Normalised strings for the different comparison flavours
        # ------------------------------------------------------------------
        item_cmp          = item_norm.lower()
        img_cmp           = img_norm.lower()
        item_cmp_case     = item_norm
        img_cmp_case      = img_norm

        reason   = []
        priority = 999                     # start high, will be lowered

        # ------------------------------------------------------------------
        # 1. Keyword removal (optional)
        # ------------------------------------------------------------------
        item_cmp_cleaned      = item_cmp
        img_cmp_cleaned       = img_cmp
        item_cmp_cleaned_case = item_cmp_case
        img_cmp_cleaned_case  = img_cmp_case

        if use_keyword_var.get():
            for kw in kw_list:
                kw_l = kw.lower()
                item_cmp_cleaned      = item_cmp_cleaned.replace(kw_l, "")
                img_cmp_cleaned       = img_cmp_cleaned.replace(kw_l, "")
                item_cmp_cleaned_case = item_cmp_cleaned_case.replace(kw, "")
                img_cmp_cleaned_case  = img_cmp_cleaned_case.replace(kw, "")
            if item_cmp != item_cmp_cleaned or img_cmp != img_cmp_cleaned:
                reason.append("keyword filter")

        # ------------------------------------------------------------------
        # 2. Helper for double-letter normalisation
        # ------------------------------------------------------------------
        def dbl_norm(s):                     # only called when the flag is on
            return normalize_double_letters(s) if ignore_double_letters_var.get() else s

        # ------------------------------------------------------------------
        # 3. Priority checks – **no early `continue` after priority 1**
        # ------------------------------------------------------------------

        # ---- 0 : Exact match (case-sensitive) --------------------------------
        if compare_strings(item_cmp_cleaned_case, img_cmp_cleaned_case, check_double_letters=False):
            priority = 0
            reason.append("exact match")
            suggestions_with_priority.append((priority, img, reason[:]))
            continue                     # best possible, skip the rest for THIS img

        # ---- 1 : Exact match (case-insensitive) -------------------------------
        if compare_strings(dbl_norm(item_cmp_cleaned), dbl_norm(img_cmp_cleaned)):
            priority = 1
            reason.append("exact match (ci)")
            suggestions_with_priority.append((priority, img, reason[:]))
            continue                     # still the best, skip lower checks for THIS img

        # ---- 2 : Compound-word exact (no spaces) -----------------------------
        item_no_space = item_cmp_cleaned.replace(" ", "")
        img_no_space  = img_cmp_cleaned.replace(" ", "")
        if item_no_space == img_no_space:
            priority = min(priority, 2)
            reason.append("exact compound")
            suggestions_with_priority.append((priority, img, reason[:]))

        # ---- 3 : Starts-with (case-exact) ------------------------------------
        if img_cmp_cleaned_case.startswith(item_cmp_cleaned_case):
            priority = min(priority, 3)
            reason.append("starts with (case exact)")
            suggestions_with_priority.append((priority, img, reason[:]))

        # ---- 4 : Ends-with (case-exact) --------------------------------------
        if img_cmp_cleaned_case.endswith(item_cmp_cleaned_case):
            priority = min(priority, 4)
            reason.append("ends with (case exact)")
            suggestions_with_priority.append((priority, img, reason[:]))

        # ---- 5 / 6 : Ignore word order ----------------------------------------
        if ignore_order_var.get():
            item_words = sorted(item_cmp_cleaned.split())
            img_words  = sorted(img_cmp_cleaned.split())
            if item_words == img_words:
                priority = min(priority, 5)
                reason.append("ignore order (exact)")
                suggestions_with_priority.append((priority, img, reason[:]))
            elif all(w in img_words for w in item_words):
                priority = min(priority, 6)
                reason.append("ignore order (partial)")
                suggestions_with_priority.append((priority, img, reason[:]))

        # ---- 7 : Starts-with (case-insensitive) -------------------------------
        if img_cmp_cleaned.startswith(item_cmp_cleaned):
            priority = min(priority, 7)
            reason.append("starts with")
            suggestions_with_priority.append((priority, img, reason[:]))

        # ---- 8 : Ends-with (case-insensitive) --------------------------------
        if img_cmp_cleaned.endswith(item_cmp_cleaned):
            priority = min(priority, 8)
            reason.append("ends with")
            suggestions_with_priority.append((priority, img, reason[:]))

        # ---- 9 : Partial containment -----------------------------------------
        if item_cmp_cleaned in img_cmp_cleaned:
            priority = min(priority, 9)
            reason.append("partial match")
            suggestions_with_priority.append((priority, img, reason[:]))

        # ---- 10 : Fuzzy -------------------------------------------------------
        ratio = difflib.SequenceMatcher(None,
                                        item_cmp_cleaned,
                                        img_cmp_cleaned).ratio()
        if ratio > 0.70:                     # <-- raised from 0.6
            priority = min(priority, 10)
            reason.append(f"fuzzy match ({ratio:.0%})")
            suggestions_with_priority.append((priority, img, reason[:]))

    # ----------------------------------------------------------------------
    # Final sort: lower priority first, then alphabetical
    # ----------------------------------------------------------------------
    suggestions_with_priority.sort(key=lambda x: (x[0], x[1]))

    # Build the two return values expected by the rest of the program
    suggestions = [img for _p, img, _r in suggestions_with_priority]
    match_reasons = {img: r for _p, img, r in suggestions_with_priority}

    return suggestions, match_reasons

# ---------- Click handling ----------
active_listbox = None
active_search_entry = None

def toggle_select_all():
    """Toggle select all/deselect all in main tree"""
    all_selected = all(selected_rows.get(r, False) for r in tree.get_children())
    for row_id in tree.get_children():
        if all_selected:
            tree.set(row_id, "Select", "")
            selected_rows[row_id] = False
        else:
            tree.set(row_id, "Select", "✔")
            selected_rows[row_id] = True

def toggle_extra_select_all():
    """Toggle select all/deselect all in extra images tree"""
    all_selected = all(extra_selected_rows.get(r, False) for r in extra_tree.get_children())
    for row_id in extra_tree.get_children():
        if all_selected:
            extra_tree.set(row_id, "Select", "")
            extra_selected_rows[row_id] = False
        else:
            extra_tree.set(row_id, "Select", "✔")
            extra_selected_rows[row_id] = True

def select_by_status(status_type):
    """Select items based on highlight/tag (green=ok only), or missing."""
    for row_id in tree.get_children():
        tags = tree.item(row_id).get("tags", ())
        status_val = tree.item(row_id).get("values", [""])[0]  # Status column

        if status_type == "Matched":
            # ONLY green highlighted lines
            if "ok" in tags:
                tree.set(row_id, "Select", "✔")
                selected_rows[row_id] = True
            else:
                tree.set(row_id, "Select", "")
                selected_rows[row_id] = False

        elif status_type == "Missing":
            # Keep your old logic OR use the tag if you prefer
            if "missing" in tags or ("Missing" in str(status_val)) or ("Suggested" in str(status_val)):
                tree.set(row_id, "Select", "✔")
                selected_rows[row_id] = True
            else:
                tree.set(row_id, "Select", "")
                selected_rows[row_id] = False

def on_click(event):
    global active_listbox, active_search_entry
    row_id = tree.identify_row(event.y)
    col = tree.identify_column(event.x)
    
    if not row_id:
        return

    # Handle Select column click (Visual Column #6)
    if col=="#6":
        current_val = tree.set(row_id, "Select")
        if current_val == "✔":
            tree.set(row_id, "Select", "")
            selected_rows[row_id] = False
        else:
            tree.set(row_id, "Select", "✔")
            selected_rows[row_id] = True
        return

    # Handle Search column click (Visual Column #4)
    if col=="#4": 
        if active_search_entry:
            active_search_entry.destroy()
            active_search_entry = None
        if active_listbox:
            active_listbox.destroy()
            active_listbox = None

        # IMPORTANT: Use the correct visual column identifier for BBOX calculation
        bbox = tree.bbox(row_id, column="#4") 
        if not bbox:
            return
            
        search_var = tk.StringVar(value=tree.set(row_id, "Search"))
        active_search_entry = ttk.Entry(tree, textvariable=search_var, width=20)
        active_search_entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        
        # Create search results listbox
        search_listbox = tk.Listbox(tree, height=10)
        search_listbox.place(x=bbox[0], y=bbox[1] + bbox[3], width=250)
        
        def update_search_results(*args):
            search_term = search_var.get()
            tree.set(row_id, "Search", search_term)
            
            search_listbox.delete(0, "end")
            if search_term:
                search_lower = search_term.lower()
                matches = [img for img in image_files_all if search_lower in img.lower()]
                for img in matches[:20]:  # Limit to 20 results
                    search_listbox.insert("end", img)
        
        def on_search_select(event):
            sel = search_listbox.curselection()
            if sel:
                selected_img = search_listbox.get(sel[0])
                tree.set(row_id, "Search", selected_img)
                # CRUCIAL: Set the Suggestions column (data index 4)
                tree.set(row_id, "Suggestions", selected_img) 
                search_var.set(selected_img)
            search_listbox.destroy()
            active_search_entry.destroy()
        
        search_var.trace('w', update_search_results)
        update_search_results()
        active_search_entry.focus()
        
        def on_search_return(e):
            if search_listbox.curselection():
                on_search_select(e)
            else:
                search_listbox.destroy()
                active_search_entry.destroy()
        
        active_search_entry.bind("<Return>", on_search_return)
        active_search_entry.bind("<Escape>", lambda e: (search_listbox.destroy(), active_search_entry.destroy()))
        active_search_entry.bind("<Down>", lambda e: search_listbox.focus())
        search_listbox.bind("<ButtonRelease-1>", on_search_select)
        search_listbox.bind("<Return>", on_search_select)
        search_listbox.bind("<Escape>", lambda e: (search_listbox.destroy(), active_search_entry.destroy()))
        return

    # Handle Suggestions column click (Visual Column #5)
    if col=="#5":
        if active_listbox:
            active_listbox.destroy()
            active_listbox = None
        if active_search_entry:
            active_search_entry.destroy()
            active_search_entry = None

        values = tree.item(row_id)["values"]
        # CRUCIAL: Item name is at data index 2
        item_name = values[2] 
        # CRUCIAL: Search term is at data index 3
        search_term = values[3] if len(values) > 3 else "" 
        
        # IMPORTANT: Use the correct visual column identifier for BBOX calculation
        bbox = tree.bbox(row_id, column="#5")
        if not bbox:
            return

        active_listbox = tk.Listbox(tree, height=12)
        active_listbox.place(x=bbox[0], y=bbox[1], width=250)

        # Get suggestions for this item
        suggestions, match_reasons = suggest_match(item_name, image_files_all)
        
        # Filter by search term if present
        filtered = ["None"]
        if search_term:
            search_lower = search_term.lower()
            for img in suggestions:
                if search_lower in img.lower():
                    filtered.append(img)
        else:
            filtered.extend(suggestions)

        # Populate listbox
        for img in filtered:
            display = img
            if img != "None" and img in match_reasons:
                reasons = ", ".join(match_reasons[img])
                display = f"{img} ({reasons})"
            active_listbox.insert("end", display)

        def on_select(event):
            global active_listbox
            sel = active_listbox.curselection()
            if sel:
                val = active_listbox.get(sel[0])
                # Extract just the image name (before any parentheses)
                val = val.split(" (")[0]
                # CRUCIAL: Set the Suggestions column (data index 4)
                tree.set(row_id, "Suggestions", val) 
            if active_listbox:
                active_listbox.destroy()
                active_listbox = None
            hide_preview()

        active_listbox.bind("<ButtonRelease-1>", on_select)
        active_listbox.bind("<Escape>", lambda e: active_listbox.destroy() if active_listbox else None)
        active_listbox.focus()

def update_suggestions_dropdown(row_id, search_term):
    """Update the suggestions dropdown based on search term"""
    global active_listbox
    if not active_listbox:
        return
    
    values = tree.item(row_id)["values"]
    item_name = values[2]
    
    suggestions, match_reasons = suggest_match(item_name, image_files_all)
    
    active_listbox.delete(0, "end")
    
    filtered = ["None"]
    if search_term:
        search_lower = search_term.lower()
        for img in suggestions:
            if search_lower in img.lower():
                filtered.append(img)
    else:
        filtered.extend(suggestions)
    
    for img in filtered:
        display = img
        if img != "None" and img in match_reasons:
            reasons = ", ".join(match_reasons[img])
            display = f"{img} ({reasons})"
        active_listbox.insert("end", display)

tree.bind("<Button-1>", on_click)

# ---------- Buttons ----------
btn_frame = ttk.Frame(analyzer_tab)
btn_frame.pack(fill="x", padx=10)
ttk.Button(btn_frame, text="Analyze", command=lambda: run_analysis()).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Rename Selected", command=lambda: auto_rename_images()).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Select Missing", command=lambda: select_by_status("Missing")).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Select Matched", command=lambda: select_by_status("Matched")).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Deselect All", command=lambda: toggle_select_all()).pack(side="left", padx=5)

# Extra images tab buttons
extra_btn_frame = ttk.Frame(extra_images_tab)
extra_btn_frame.pack(fill="x", padx=10, pady=10)
ttk.Button(extra_btn_frame, text="Delete Selected", command=lambda: delete_extra_images()).pack(side="left", padx=5)

# ---------- Counter ----------
counter_var = tk.StringVar(value="")
counter_label = ttk.Label(analyzer_tab, textvariable=counter_var)
counter_label.pack(anchor="w", padx=10, pady=(0, 5))

# ---------- Run Analysis ----------
def run_analysis():
    global current_img_folder, image_files_all, image_map, selected_rows, extra_selected_rows

    sql_file = sql_path_var.get()
    img_folder = img_folder_var.get()
    if not os.path.isfile(sql_file) or not os.path.isdir(img_folder):
        messagebox.showwarning("Missing info", "Please select SQL file and image folder.")
        return

    current_img_folder = img_folder
    sql_items, descriptions = parse_sql_items(sql_file)
    matched, missing, extra, image_files_all, image_map = analyze(sql_items, img_folder)

    selected_rows.clear()
    extra_selected_rows.clear()
    for row in tree.get_children():
        tree.delete(row)
    for row in extra_tree.get_children():
        extra_tree.delete(row)

    # ---------- COUNTER INIT ----------
    total = len(matched) + len(missing)
    done = 0
    counter_var.set(f"Building results… 0/{total}")
    root.update_idletasks()
    # ---------------------------------


    # ---------- RENAMED STATUS (filesystem truth) ----------
    # If {item}.png exists in old_images_backup, treat as already renamed.
    renamed_folder = os.path.join(current_img_folder, "new_rename_output")
    renamed_items = set()
    if os.path.isdir(renamed_folder):
        for fn in os.listdir(renamed_folder):
            if fn.lower().endswith(".png"):
                renamed_items.add(os.path.splitext(fn)[0].lower())
    # -------------------------------------------------------

    claimed_images_lower = set()

    # ---------- MATCHED ----------
    for i in matched:
        i_lower = i.lower()
        if i_lower in image_map:
            claimed_images_lower.add(i_lower)

        # Status: prefer filesystem "Renamed" over analysis result
        status = "Renamed ✓" if i.lower() in renamed_items else "Exact match"
        reasons = []
        if ignore_underscore_var.get() and ("_" in i or "-" in i):
            for img_name_lower in image_map:
                if normalize_name(i).lower() == normalize_name(img_name_lower).lower():
                    reasons.append("ignore _/-")
                    break

        if reasons:
            status = f"Matched: {', '.join(reasons)}"

        row_tag = "renamed" if i.lower() in renamed_items else "ok"

        tree.insert("", "end", values=(
            status,
            descriptions.get(i, ""),
            i,
            "",
            i,
            ""
        ), tags=(row_tag,))

        done += 1
        counter_var.set(f"Building results… {done}/{total}")
        root.update_idletasks()

    # ---------- MISSING ----------
    available_images_for_suggestion = [
        img for img in image_files_all
        if img.lower() not in claimed_images_lower
    ]

    for i in missing:
        suggestions, match_reasons = suggest_match(i, available_images_for_suggestion)

        best_match = suggestions[0] if suggestions else "None"
        # If already renamed (exists in new_rename_output), mark as renamed
        if i.lower() in renamed_items:
            status = "Renamed ✓"
        
        # Status: filesystem "Renamed" overrides suggestion/missing
        if i.lower() in renamed_items:
            status = "Renamed ✓"
        elif best_match != "None" and best_match in match_reasons:
            status = f"Suggested: {', '.join(match_reasons[best_match])}"
        else:
            status = "Missing Image"

        row_tag = "renamed" if i.lower() in renamed_items else "missing"

        tree.insert("", "end", values=(
            status,
            descriptions.get(i, ""),
            i,
            "",
            best_match,
            ""
        ), tags=(row_tag,))

        done += 1
        counter_var.set(f"Building results… {done}/{total}")
        root.update_idletasks()

    # ---------- EXTRA ----------
    for f in extra:
        path = image_map.get(f.lower(), f"{f}.png")
        extra_tree.insert("", "end", values=(
            "",
            f,
            path
        ), tags=("extra",))

    tree.tag_configure("ok", background="#d4fcdc")
    tree.tag_configure("missing", background="#fff2cc")
    tree.tag_configure("renamed", background="#cce5ff")
    extra_tree.tag_configure("extra", background="#fcdada")

    counter_var.set(
        f"Done. Matched: {len(matched)} | Missing: {len(missing)} | Extra: {len(extra)}"
    )
# ---------- Auto-rename ----------
# ---------- Auto-rename ----------
def auto_rename_images():
    if not current_img_folder:
        messagebox.showwarning("No folder","Please select an image folder first.")
        return

    rename_backup = os.path.join(current_img_folder, "old_images_backup")
    output_folder = os.path.join(current_img_folder, "new_rename_output")

    os.makedirs(rename_backup, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    renamed_count = 0

    for row_id in tree.get_children():
        if not selected_rows.get(row_id, False):
            continue

        values = tree.item(row_id)['values']
        sql_item = values[2]
        suggestion = values[4]

        if not suggestion or suggestion == "None":
            continue

        rel_path = image_map.get(suggestion.lower())
        if not rel_path:
            continue

        orig_path = os.path.join(current_img_folder, rel_path)
        if not os.path.isfile(orig_path):
            continue

        # Move original → rename_backup
        backup_path = os.path.join(rename_backup, os.path.basename(orig_path))
        if not os.path.exists(backup_path):
            os.rename(orig_path, backup_path)
        else:
            os.remove(orig_path)

        # Save final output → output
        new_path = os.path.join(output_folder, f"{sql_item}.png")
        img = Image.open(backup_path)
        img = img.resize((96, 96), Image.LANCZOS)
        img.save(new_path)

        renamed_count += 1

        # Update UI status in-place (no full rescan)
        try:
            tree.set(row_id, "Status", "Renamed ✓")
            tree.item(row_id, tags=("renamed",))
            tree.set(row_id, "Select", "")
            selected_rows[row_id] = False
        except Exception:
            pass

    messagebox.showinfo(
        "Done",
        f"Renamed and resized {renamed_count} images.\n"
        f"Output → /new_rename_output\n"
        f"Backed up originals → /old_images_backup"
    )

    # Refresh statuses in the UI
    #run_analysis()

# ---------- Delete Extra Images ----------
def delete_extra_images():
    if not current_img_folder:
        messagebox.showwarning("No folder","Please select an image folder first.")
        return
    
    to_delete = []
    for row_id in extra_tree.get_children():
        if extra_selected_rows.get(row_id, False):
            values = extra_tree.item(row_id)['values']
            img_name = values[1]
            to_delete.append(img_name)
    
    if not to_delete:
        messagebox.showinfo("No Selection", "Please select images to delete.")
        return
    
    if not messagebox.askyesno("Confirm Delete", f"Delete {len(to_delete)} selected images?\n\nThey will be moved to the backup folder."):
        return
    
    backup_folder = os.path.join(current_img_folder, "old_images_backup")
    os.makedirs(backup_folder, exist_ok=True)
    deleted_count = 0
    
    for img_name in to_delete:
        img_path = os.path.join(current_img_folder, image_map.get(img_name.lower(), f"{img_name}.png"))
        if os.path.isfile(img_path):
            backup_path = os.path.join(backup_folder, os.path.basename(img_path))
            try:
                os.rename(img_path, backup_path)
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {img_name}: {e}")
    
    messagebox.showinfo("Done", f"Moved {deleted_count} images to backup folder.")
root.mainloop()
