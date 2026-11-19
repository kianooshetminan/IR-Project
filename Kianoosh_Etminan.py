import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, scrolledtext

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer

try:
    stop_words = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))

stemmer = PorterStemmer()
tokenizer = RegexpTokenizer(
    r"[A-Za-z](?:\.[A-Za-z])+\.?|[A-Za-z]+(?:-[A-Za-z]+)+|[A-Za-z]+(?:['\u2019]s)?"
)

samples = [
    "Friends, Romans, countrymen, lend me your ears;",
    "John's new U.S.A. laptop is a state-of-the-art device. The price is high, but the quality is amazing!",
    "The authorization for this authorized project is pending. He authorizes the payments regularly.",
]

gold = [
    ["friend", "roman", "countrymen", "lend", "ear"],
    ["john", "new", "usa", "laptop", "state-of-the-art", "devic", "price", "high", "qualiti", "amaz"],
    ["author", "author", "project", "pend", "author", "payment", "regularli"],
]


def clean_token(word):
    if len(word) > 2 and word[-2:] in ("'s", "\u2019s"):
        return word[:-2]
    return word


def normalize(word):
    bare = word.replace(".", "")
    if "." in word and bare.isalpha():
        word = bare
    return word.lower()


def preprocess(text):
    tokens = [clean_token(w) for w in tokenizer.tokenize(text)]
    tokens = [w for w in tokens if w]
    normalized = [normalize(w) for w in tokens]
    kept = [w for w in normalized if w not in stop_words]
    terms = [stemmer.stem(w) if w.isalpha() else w for w in kept]
    return tokens, normalized, kept, terms


def find_gold(text):
    folded = " ".join(text.split())
    for i, sample in enumerate(samples):
        if " ".join(sample.split()) == folded:
            return gold[i]
    return None


def pr_lines(terms, real):
    output_set = set(terms)
    gold_set = set(real)
    both = output_set & gold_set
    extra = sorted(output_set - gold_set)
    missing = sorted(gold_set - output_set)
    if output_set:
        precision = "Precision = %d/%d = %.2f" % (len(both), len(output_set), len(both) / len(output_set))
    else:
        precision = "Precision = 0"
    if gold_set:
        recall = "Recall = %d/%d = %.2f" % (len(both), len(gold_set), len(both) / len(gold_set))
    else:
        recall = "Recall = 0"
    lines = [
        "خروجی طلایی: " + str(real),
        precision,
        recall,
        "اضافه: " + (", ".join(extra) if extra else "-"),
        "جا افتاده: " + (", ".join(missing) if missing else "-"),
    ]
    return lines


def make_report(title, text):
    tokens, normalized, kept, terms = preprocess(text)
    lines = [
        title,
        text,
        "",
        "توکن: " + str(tokens),
        "یکسان سازی: " + str(normalized),
        "بدون کلمات ایست: " + str(kept),
        "نهایی: " + str(terms),
    ]
    real = find_gold(text)
    if real is not None:
        lines.append("")
        lines.extend(pr_lines(terms, real))
    return "\n".join(lines)


def show(text):
    result.configure(state="normal")
    result.delete("1.0", "end")
    result.insert("end", text)
    result.configure(state="disabled")


def put_sample(index):
    box.delete("1.0", "end")
    box.insert("1.0", samples[index])


def run_text():
    text = box.get("1.0", "end").strip()
    if not text:
        messagebox.showinfo("", "اول متن را بنویس")
        return
    show(make_report("نتیجه", text))


def run_all():
    parts = []
    for i, sample in enumerate(samples):
        parts.append(make_report("متن %d" % (i + 1), sample))
        parts.append("")
    show("\n".join(parts))


def copy_text(event=None):
    try:
        text = box.get("sel.first", "sel.last")
    except tk.TclError:
        return "break"
    root.clipboard_clear()
    root.clipboard_append(text)
    return "break"


def cut_text(event=None):
    copy_text()
    try:
        box.delete("sel.first", "sel.last")
    except tk.TclError:
        pass
    return "break"


def paste_text(event=None):
    try:
        text = root.clipboard_get()
    except tk.TclError:
        return "break"
    try:
        box.delete("sel.first", "sel.last")
    except tk.TclError:
        pass
    box.insert("insert", text)
    return "break"


def select_all(event=None):
    box.tag_add("sel", "1.0", "end-1c")
    return "break"


def show_menu(event):
    box.focus_set()
    menu.tk_popup(event.x_root, event.y_root)
    return "break"


root = tk.Tk()
root.title("پیش پردازش متن")
root.geometry("720x520")

families = set(tkfont.families())
if "Yekan Bakh" in families:
    ui = "Yekan Bakh"
elif "YekanBakh" in families:
    ui = "YekanBakh"
else:
    ui = "Arial"
ui_font = (ui, 13)
root.option_add("*Font", ui_font)

tk.Label(root, text="متن", font=ui_font).pack(anchor="w", padx=8, pady=(8, 0))
box = tk.Text(root, height=6, font=ui_font)
box.pack(fill="x", padx=8, pady=4)

row = tk.Frame(root)
row.pack()
tk.Button(row, text="متن ۱", font=ui_font, command=lambda: put_sample(0)).pack(side="left", padx=4, pady=4)
tk.Button(row, text="متن ۲", font=ui_font, command=lambda: put_sample(1)).pack(side="left", padx=4, pady=4)
tk.Button(row, text="متن ۳", font=ui_font, command=lambda: put_sample(2)).pack(side="left", padx=4, pady=4)
tk.Button(row, text="پردازش", font=ui_font, command=run_text).pack(side="left", padx=4, pady=4)
tk.Button(row, text="ارزیابی هر سه", font=ui_font, command=run_all).pack(side="left", padx=4, pady=4)

for keys, func in (
    ("<Command-c>", copy_text),
    ("<Command-C>", copy_text),
    ("<Control-c>", copy_text),
    ("<Command-x>", cut_text),
    ("<Command-X>", cut_text),
    ("<Control-x>", cut_text),
    ("<Command-v>", paste_text),
    ("<Command-V>", paste_text),
    ("<Control-v>", paste_text),
    ("<Command-a>", select_all),
    ("<Command-A>", select_all),
    ("<Control-a>", select_all),
):
    box.bind(keys, func)

menu = tk.Menu(box, tearoff=0, font=ui_font)
menu.add_command(label="کپی", command=copy_text)
menu.add_command(label="کات", command=cut_text)
menu.add_command(label="پیست", command=paste_text)
menu.add_command(label="انتخاب همه", command=select_all)
box.bind("<Button-2>", show_menu)
box.bind("<Button-3>", show_menu)
box.bind("<Control-Button-1>", show_menu)

edit = tk.Menu(root, tearoff=0, font=ui_font)
edit.add_command(label="Cut", command=cut_text)
edit.add_command(label="Copy", command=copy_text)
edit.add_command(label="Paste", command=paste_text)
edit.add_command(label="Select All", command=select_all)
bar = tk.Menu(root)
bar.add_cascade(label="Edit", menu=edit)
root.config(menu=bar)

result = scrolledtext.ScrolledText(root, font=ui_font)
result.pack(fill="both", expand=True, padx=8, pady=8)
result.configure(state="disabled")

if __name__ == "__main__":
    root.mainloop()
