"""
    Scientific Calculator   """
"""
Scientific Calculator (tkinter) with Tabbed Converter in the same main window.

- Main window contains a ttk.Notebook with two tabs:
    * Calculator
    * Converter (which contains its own Notebook: Weight, Length, Temperature)
- Calculator UI and safe_eval preserved from your original script.
- Converter supports Convert and Swap functions.

- Run: python3 sci_converter_azure_theme.py
"""
import tkinter as tk
from tkinter import ttk, messagebox
import math
import re
import os

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
    angle_mode: 'rad' or 'deg' — affects trig functions and inverses.
    """
    expr = expr.replace('×', '*').replace('÷', '/')
    expr = expr.replace('^', '**')
    expr = expr.replace('π', 'pi')

    # handle percentage like `50%` or `50 %` or `50%*2`
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


# --- Main App ---
class SciConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- Try to load Azure theme (place `azure` folder next to this script) ---
        self._azure_loaded = False
        try:
            azure_path = os.path.join(os.path.dirname(__file__), 'azure', 'azure.tcl')
        except Exception:
            azure_path = 'azure/azure.tcl'

        try:
            if os.path.exists(azure_path):
                self.tk.call('source', azure_path)
                # prefer dark mode by default
                ttk.Style(self).theme_use('azure-dark')
                self._azure_loaded = True
            else:
                # fallback to a modern available theme
                style = ttk.Style(self)
                # try to pick a good cross-platform theme
                for t in ('clam', 'vista', 'xpnative', 'alt'):
                    try:
                        style.theme_use(t)
                        break
                    except Exception:
                        continue
        except Exception:
            pass

        # Minor global style tweaks
        style = ttk.Style(self)
        try:
            # set a pleasant default font for ttk widgets
            style.configure('.', font=('Segoe UI', 10))
            # add a bit more padding for buttons and notebook tabs
            style.configure('TButton', padding=(6, 6))
            style.configure('TNotebook.Tab', padding=(8, 6))
        except Exception:
            pass

        self.title('Scientific Calculator + Converter')
        self.resizable(False, False)

        self.expression = tk.StringVar()
        self.history = []
        self.angle_mode_var = tk.StringVar(value='rad')

        self._build_menu()
        self._build_main_notebook()

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

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label='Toggle Theme', command=self.toggle_theme)
        menubar.add_cascade(label='View', menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label='About', command=self._show_about)
        menubar.add_cascade(label='Help', menu=help_menu)
        self.config(menu=menubar)

    def toggle_theme(self):
        style = ttk.Style(self)
        try:
            current = style.theme_use()
            if self._azure_loaded:
                # toggle between azure-dark and azure-light
                if current == 'azure-dark':
                    style.theme_use('azure-light')
                else:
                    style.theme_use('azure-dark')
            else:
                # simple fallback toggle for non-azure setups
                if current in ('clam', 'alt'):
                    style.theme_use('vista')
                else:
                    style.theme_use('clam')
        except Exception:
            pass

    def _show_about(self):
        about_text = (
            "Scientific Calculator + Converter\n\n"
            "Calculator features: standard ops, trig (rad/deg), safe eval\n"
            "Converter features: Weight, Length, Temperature (on separate converter tabs)\n"
        )
        messagebox.showinfo('About', about_text)

    def _build_main_notebook(self):
        """Create main notebook with two tabs: Calculator and Converter."""
        main_notebook = ttk.Notebook(self)
        main_notebook.pack(fill='both', expand=True, padx=8, pady=8)

        calc_frame = ttk.Frame(main_notebook)
        converter_frame = ttk.Frame(main_notebook)

        main_notebook.add(calc_frame, text='Calculator')
        main_notebook.add(converter_frame, text='Converter')

        # build calculator in calc_frame
        self._build_calc_ui(calc_frame)

        # build tabbed converter inside converter_frame
        self._build_converter_notebook(converter_frame)

    # --- Calculator UI (moved into a frame) ---
    def _build_calc_ui(self, parent):
        main = parent
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
                # use Accent.TButton for primary action '=' and utility buttons where it looks good
                style_name = 'TButton'
                if label == '=' and self._azure_loaded:
                    style_name = 'Accent.TButton'
                btn = ttk.Button(left_frame, text=label, style=style_name, command=lambda v=label: self.on_button(v))
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

        # keyboard bindings (apply to whole app)
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
            return None
        self.entry.bind('<Key>', key_insert)

    def _on_mode_change(self):
        mode = self.angle_mode_var.get()
        self.title(f'Scientific Calculator + Converter ({"Degrees" if mode=="deg" else "Radians"})')

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
            insert_text = 'fact(' if label == 'fact' else f'{label}('
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

    # --- Converter Notebook inside main window ---
    def _build_converter_notebook(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True, padx=8, pady=8)

        # Weight tab
        weight_frame = ttk.Frame(notebook)
        notebook.add(weight_frame, text='Weight')
        weight_units = {
            "Kilogram (kg)": 1.0,
            "Gram (g)": 0.001,
            "Pound (lb)": 0.45359237,
            "Ounce (oz)": 0.028349523125,
        }
        self._build_converter_tab(weight_frame, weight_units)

        # Length tab
        length_frame = ttk.Frame(notebook)
        notebook.add(length_frame, text='Length')
        length_units = {
            "Meter (m)": 1.0,
            "Centimeter (cm)": 0.01,
            "Millimeter (mm)": 0.001,
            "Kilometer (km)": 1000.0,
            "Inch (in)": 0.0254,
            "Foot (ft)": 0.3048,
        }
        self._build_converter_tab(length_frame, length_units)

        # Temperature tab
        temp_frame = ttk.Frame(notebook)
        notebook.add(temp_frame, text='Temperature')
        self._build_temperature_tab(temp_frame)

    def _build_converter_tab(self, parent, units_dict):
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text='Value:').grid(row=0, column=0, padx=6, pady=6, sticky='w')
        value_entry = ttk.Entry(parent)
        value_entry.grid(row=0, column=1, padx=6, pady=6, sticky='ew')

        ttk.Label(parent, text='From:').grid(row=1, column=0, padx=6, sticky='w')
        from_unit = ttk.Combobox(parent, values=list(units_dict.keys()), state='readonly')
        from_unit.grid(row=1, column=1, padx=6, pady=4, sticky='ew')
        from_unit.current(0)

        ttk.Label(parent, text='To:').grid(row=2, column=0, padx=6, sticky='w')
        to_unit = ttk.Combobox(parent, values=list(units_dict.keys()), state='readonly')
        to_unit.grid(row=2, column=1, padx=6, pady=4, sticky='ew')
        to_unit.current(1 if len(units_dict) > 1 else 0)

        result_label = ttk.Label(parent, text='Result: ')
        result_label.grid(row=4, column=0, columnspan=2, padx=6, pady=10, sticky='w')

        def convert():
            try:
                val = float(value_entry.get())
                base = val * units_dict[from_unit.get()]  # convert to base unit (e.g. kg or m)
                result = base / units_dict[to_unit.get()]
                result_label.config(text=f'Result: {result:.6g}')
            except Exception:
                messagebox.showerror('Error', 'Invalid input')

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(4,8))
        ttk.Button(btn_frame, text='Convert', style=('Accent.TButton' if self._azure_loaded else 'TButton'), command=convert).pack(side='left', padx=(0,6))
        ttk.Button(btn_frame, text='Swap', command=lambda: self._swap_units(value_entry, from_unit, to_unit)).pack(side='left')

    def _swap_units(self, value_entry, from_cb, to_cb):
        f = from_cb.get()
        t = to_cb.get()
        if not f or not t:
            return
        from_cb.set(t)
        to_cb.set(f)
        # leave numeric value as-is so user may press Convert again

    def _build_temperature_tab(self, parent):
        parent.columnconfigure(1, weight=1)
        units = ['Celsius (°C)', 'Fahrenheit (°F)', 'Kelvin (K)']

        ttk.Label(parent, text='Value:').grid(row=0, column=0, padx=6, pady=6, sticky='w')
        entry = ttk.Entry(parent)
        entry.grid(row=0, column=1, padx=6, pady=6, sticky='ew')

        ttk.Label(parent, text='From:').grid(row=1, column=0, padx=6, sticky='w')
        from_unit = ttk.Combobox(parent, values=units, state='readonly')
        from_unit.grid(row=1, column=1, padx=6, pady=4, sticky='ew')
        from_unit.current(0)

        ttk.Label(parent, text='To:').grid(row=2, column=0, padx=6, sticky='w')
        to_unit = ttk.Combobox(parent, values=units, state='readonly')
        to_unit.grid(row=2, column=1, padx=6, pady=4, sticky='ew')
        to_unit.current(1)

        result_label = ttk.Label(parent, text='Result: ')
        result_label.grid(row=4, column=0, columnspan=2, padx=6, pady=10, sticky='w')

        def convert_temp():
            try:
                val = float(entry.get())
                f = from_unit.get()
                t = to_unit.get()

                if f.startswith('C'):
                    c = val
                elif f.startswith('F'):
                    c = (val - 32) * 5.0/9.0
                elif f.startswith('K'):
                    c = val - 273.15
                else:
                    raise ValueError('Unknown unit')

                if t.startswith('C'):
                    result = c
                elif t.startswith('F'):
                    result = (c * 9.0/5.0) + 32
                elif t.startswith('K'):
                    result = c + 273.15
                else:
                    raise ValueError('Unknown unit')

                result_label.config(text=f'Result: {result:.6g}')
            except Exception:
                messagebox.showerror('Error', 'Invalid input')

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(4,8))
        ttk.Button(btn_frame, text='Convert', style=('Accent.TButton' if self._azure_loaded else 'TButton'), command=convert_temp).pack(side='left', padx=(0,6))
        ttk.Button(btn_frame, text='Swap', command=lambda: self._swap_units(entry, from_unit, to_unit)).pack(side='left')


if __name__ == '__main__':
    app = SciConverterApp()
    app.mainloop()
