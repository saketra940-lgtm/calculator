#!/usr/bin/env python3
"""
Scientific Calculator (tkinter)

Essential features included:
● Core mathematical operations: addition, subtraction, multiplication, division
● Execute calculations with '=' and clear equation display with 'C'
● Safe evaluation environment with math functions and controlled namespace
● Keyboard support, history, angle mode (rad/deg), simple About dialog with Learning Outcomes

Learning Outcomes:
1. Core Python
2. tkinter Library
3. Visual Studio Code[IDE]
4. GitHub
5. Application development using Python programming language
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import re

# --- Safe evaluation environment ---
ALLOWED_NAMES = {k: getattr(math, k) for k in dir(math) if not k.startswith("__")}
ALLOWED_NAMES.update({
    'pi': math.pi,
    'e': math.e,
    'sqrt': math.sqrt,
    'ln': math.log,
    'log': math.log10,
    'fact': math.factorial,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'gamma': math.gamma,
})

def safe_eval(expr, angle_mode='rad'):
    """Evaluate mathematical expression with a controlled namespace.

    angle_mode: 'rad' or 'deg' — affects sin/cos/tan and their inverses.
    """
    expr = expr.replace('×', '*').replace('÷', '/')
    expr = expr.replace('^', '**')
    expr = expr.replace('π', 'pi')

    expr = re.sub(
        r'(?P<a>\d+(?:\.\d+)?)[ \t]*%[ \t]*(?=(\d+(?:\.\d+)?|\())',
        lambda m: f"({m.group('a')}/100)*",
        expr
    )
    expr = re.sub(r'(?P<a>\d+(?:\.\d+)?)\s*%', r'(\g<a>/100)', expr)

    local_names = ALLOWED_NAMES.copy()

    def make_forward(fn):
        if angle_mode == 'deg':
            return lambda x: fn(math.radians(x))
        else:
            return lambda x: fn(x)

    def make_inverse(fn):
        if angle_mode == 'deg':
            return lambda x: math.degrees(fn(x))
        else:
            return lambda x: fn(x)

    local_names['sin'] = make_forward(math.sin)
    local_names['cos'] = make_forward(math.cos)
    local_names['tan'] = make_forward(math.tan)
    local_names['asin'] = make_inverse(math.asin)
    local_names['acos'] = make_inverse(math.acos)
    local_names['atan'] = make_inverse(math.atan)

    safe_builtin_names = {'abs', 'round'}

    try:
        code = compile(expr, '<string>', 'eval')
        for name in code.co_names:
            if name not in local_names and name not in safe_builtin_names:
                raise NameError(f"Use of '{name}' not allowed")
        return eval(code, {"__builtins__": {}}, local_names)
    except Exception:
        raise

# --- GUI ---
class SciCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Scientific Calculator')
        self.resizable(False, False)

        self.expression = tk.StringVar()
        self.history = []
        self.angle_mode_var = tk.StringVar(value='rad')

        self._build_menu()
        self._build_ui()

        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        self.geometry(f"{w}x{h}")
        self.minsize(w, h)
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_menu(self):
        menubar = tk.Menu(self)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label='About', command=self._show_about)
        menubar.add_cascade(label='Help', menu=help_menu)
        self.config(menu=menubar)

    def _show_about(self):
        about_text = (
            "Scientific Calculator\n\n"
            "Essential features:\n"
            "• Addition, Subtraction, Multiplication, Division\n"
            "• Evaluate (=) and Clear (C)\n\n"
            "Learning Outcomes:\n"
            "1. Core Python\n"
            "2. tkinter Library\n"
            "3. Visual Studio Code[IDE]\n"
            "4. GitHub\n"
            "5. Application development using Python programming language\n"
        )
        messagebox.showinfo('About', about_text)

    def _build_ui(self):
        main = ttk.Frame(self, padding=0)
        main.pack(fill='both', expand=True)

        main.grid_rowconfigure(0, weight=0)
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=0)

        display_frame = ttk.Frame(main)
        display_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 6))

        self.entry = ttk.Entry(display_frame, textvariable=self.expression, font=('Consolas', 20), justify='right')
        self.entry.pack(fill='x', ipady=10)
        self.entry.focus()

        mode_frame = ttk.Frame(main)
        mode_frame.grid(row=0, column=1, sticky='ne', padx=(0,8), pady=(4,0))

        ttk.Label(mode_frame, text='Angle:').grid(row=0, column=0, padx=(0,6))
        rb_rad = ttk.Radiobutton(mode_frame, text='Rad', value='rad', variable=self.angle_mode_var, command=self._on_mode_change)
        rb_deg = ttk.Radiobutton(mode_frame, text='Deg', value='deg', variable=self.angle_mode_var, command=self._on_mode_change)
        rb_rad.grid(row=0, column=1)
        rb_deg.grid(row=0, column=2)

        left_frame = ttk.Frame(main)
        left_frame.grid(row=1, column=0, sticky='nsew')

        buttons = [
            ['7','8','9','C','⌫'],
            ['4','5','6','×','^'],
            ['1','2','3','-','('],
            ['.','0','=','+',')'],
            ['sin','cos','tan','÷','sqrt'],
            ['asin','acos','atan','%','gamma'],
            ['pi','e','fact','log','ln']
        ]

        for r, row in enumerate(buttons):
            for c, label in enumerate(row):
                btn = ttk.Button(left_frame, text=label, command=lambda v=label: self.on_button(v))
                btn.grid(row=r, column=c, ipadx=6, ipady=10, padx=4, pady=4, sticky='nsew')

        for i in range(len(buttons)):
            left_frame.rowconfigure(i, weight=1)
        for i in range(max(len(r) for r in buttons)):
            left_frame.columnconfigure(i, weight=1)

        right_frame = ttk.Frame(main)
        right_frame.grid(row=1, column=1, sticky='nsew', padx=(8,0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        history_label = ttk.Label(right_frame, text='History', font=('Segoe UI', 12, 'bold'))
        history_label.grid(row=0, column=0, sticky='w')

        self.history_listbox = tk.Listbox(right_frame, height=20)
        self.history_listbox.grid(row=1, column=0, sticky='nsew', pady=6)
        self.history_listbox.bind('<Double-Button-1>', self.on_history_double_click)

        history_btn_frame = ttk.Frame(right_frame)
        history_btn_frame.grid(row=2, column=0, sticky='ew')

        clear_hist_btn = ttk.Button(history_btn_frame, text='Clear History', command=self.clear_history)
        clear_hist_btn.pack(side='left', padx=(0,6))

        use_selected_btn = ttk.Button(history_btn_frame, text='Use Selected', command=self.use_selected_history)
        use_selected_btn.pack(side='left')

        # keyboard bindings
        self.bind_all('<Return>', lambda e: self.on_button('='))
        self.bind_all('<BackSpace>', lambda e: self.on_button('⌫'))
        self.bind_all('<Escape>', lambda e: self.on_button('C'))

        # allow number/operator typing
        allowed_chars = set('0123456789+-*/().%')
        def key_insert(event):
            ch = event.char
            if ch in allowed_chars:
                # use standard symbols for keyboard (buttons may use Unicode × ÷)
                if ch == '*':
                    self.expression.set(self.expression.get() + '*')
                elif ch == '/':
                    self.expression.set(self.expression.get() + '/')
                else:
                    self.expression.set(self.expression.get() + ch)
                return "break"
            # allow Enter/Return, handled above
            return None

        # bind to the entry for text insertion
        self.entry.bind('<Key>', key_insert)

    def _on_mode_change(self):
        mode = self.angle_mode_var.get()
        self.title(f'Scientific Calculator ({"Degrees" if mode=="deg" else "Radians"})')

    def on_button(self, label):
        if label == 'C':
            self.expression.set('')
            return
        if label == '⌫':
            cur = self.expression.get()
            self.expression.set(cur[:-1])
            return
        if label == '=':
            expr = self.expression.get().strip()
            if not expr:
                return
            try:
                result = safe_eval(expr, angle_mode=self.angle_mode_var.get())
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                self.expression.set(str(result))
                self._add_history(expr, result)
            except ZeroDivisionError:
                messagebox.showerror('Error', 'Division by zero is not allowed.')
            except Exception as e:
                messagebox.showerror('Error', f'Invalid expression:\n{e}')
            return

        insert_text = label
        if label in {'sin','cos','tan','log','ln','sqrt','fact','asin','acos','atan','gamma'}:
            if label == 'fact':
                insert_text = 'fact('
            else:
                insert_text = f'{label}('
        elif label == '%':
            insert_text = '%'
        elif label == 'pi':
            insert_text = 'pi'
        elif label == 'e':
            insert_text = 'e'
        elif label in {'×','÷','^','+','-','(',')','.'}:
            insert_text = label
        elif label.isdigit():
            insert_text = label
        else:
            insert_text = label

        self.expression.set(self.expression.get() + insert_text)

    def _add_history(self, expr, result):
        item = f"{expr} = {result}"
        self.history.insert(0, item)
        self._refresh_history()

    def _refresh_history(self):
        self.history_listbox.delete(0, tk.END)
        for item in self.history:
            self.history_listbox.insert(tk.END, item)

    def clear_history(self):
        if messagebox.askyesno('Clear History', 'Clear all history?'):
            self.history.clear()
            self._refresh_history()

    def on_history_double_click(self, event):
        sel = self.history_listbox.curselection()
        if not sel:
            return
        text = self.history_listbox.get(sel[0])
        if '=' in text:
            expr = text.split('=')[0].strip()
            self.expression.set(expr)

    def use_selected_history(self):
        sel = self.history_listbox.curselection()
        if not sel:
            messagebox.showinfo('Use Selected', 'No history item selected')
            return
        self.on_history_double_click(None)


if __name__ == '__main__':
    app = SciCalculator()
    app.mainloop()
