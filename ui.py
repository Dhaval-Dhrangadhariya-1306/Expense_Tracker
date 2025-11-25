import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import add_expense, fetch_expenses, delete_expense, init_db, update_expense, fetch_monthly_summary
from utils import export_to_csv_pandas, safe_float, format_date_for_input
from datetime import datetime
import os

class ExpenseApp:
    def __init__(self, root):
        self.root = root
        root.title("Expense Tracker")
        root.geometry("900x600")
        root.resizable(True, True)

        init_db()
        self.create_widgets()
        self.load_expenses()

    def create_widgets(self):
        frame_top = ttk.Frame(self.root, padding=10)
        frame_top.pack(fill="x")

        # Input row
        ttk.Label(frame_top, text="Date (YYYY-MM-DD)").grid(row=0, column=0, padx=5, pady=5)
        self.date_var = tk.StringVar(value=format_date_for_input(datetime.now()))
        ttk.Entry(frame_top, textvariable=self.date_var, width=15).grid(row=0, column=1)

        ttk.Label(frame_top, text="Category").grid(row=0, column=2, padx=5)
        self.cat_var = tk.StringVar()
        ttk.Combobox(frame_top, textvariable=self.cat_var, values=["Food","Transport","Utilities","Shopping","Other"], width=20).grid(row=0, column=3)

        ttk.Label(frame_top, text="Amount").grid(row=0, column=4, padx=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(frame_top, textvariable=self.amount_var, width=12).grid(row=0, column=5)

        ttk.Label(frame_top, text="Note").grid(row=1, column=0, padx=5, pady=5)
        self.note_var = tk.StringVar()
        ttk.Entry(frame_top, textvariable=self.note_var, width=60).grid(row=1, column=1, columnspan=4, sticky="w")

        ttk.Button(frame_top, text="Add Expense", command=self.add_expense_click).grid(row=0, column=6, padx=10)
        ttk.Button(frame_top, text="Update Selected", command=self.update_selected).grid(row=1, column=6, padx=10)
        ttk.Button(frame_top, text="Delete Selected", command=self.delete_selected).grid(row=2, column=6, padx=10)

        # Filters
        frame_filter = ttk.Frame(self.root, padding=10)
        frame_filter.pack(fill="x")
        ttk.Label(frame_filter, text="Filter by Category").pack(side="left")
        self.filter_cat = tk.StringVar(value="All")
        comb = ttk.Combobox(frame_filter, textvariable=self.filter_cat, values=["All","Food","Transport","Utilities","Shopping","Other"], width=20)
        comb.pack(side="left", padx=5)
        ttk.Label(frame_filter, text="From").pack(side="left", padx=5)
        self.from_var = tk.StringVar()
        ttk.Entry(frame_filter, textvariable=self.from_var, width=12).pack(side="left")
        ttk.Label(frame_filter, text="To").pack(side="left", padx=5)
        self.to_var = tk.StringVar()
        ttk.Entry(frame_filter, textvariable=self.to_var, width=12).pack(side="left")
        ttk.Button(frame_filter, text="Apply Filter", command=self.apply_filter).pack(side="left", padx=10)
        ttk.Button(frame_filter, text="Clear Filter", command=self.clear_filter).pack(side="left")

        # Table
        frame_table = ttk.Frame(self.root, padding=10)
        frame_table.pack(fill="both", expand=True)

        columns = ("id","date","category","amount","note")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, anchor="w", width=120 if col!="note" else 300)
        self.tree.pack(fill="both", expand=True, side="left")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Bottom actions
        frame_bottom = ttk.Frame(self.root, padding=10)
        frame_bottom.pack(fill="x")
        ttk.Button(frame_bottom, text="Export CSV", command=self.export_csv).pack(side="left")
        ttk.Button(frame_bottom, text="Monthly Summary", command=self.show_monthly_summary).pack(side="left", padx=5)

    def add_expense_click(self):
        date = self.date_var.get().strip()
        cat = self.cat_var.get().strip() or "Other"
        amt = safe_float(self.amount_var.get().strip())
        note = self.note_var.get().strip()
        if not date or amt <= 0:
            messagebox.showwarning("Invalid", "Please enter valid date and amount.")
            return
        add_expense(date, cat, amt, note)
        self.clear_inputs()
        self.load_expenses()

    def load_expenses(self, where="", params=()):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = fetch_expenses(where, params)
        for r in rows:
            self.tree.insert("", "end", values=r)

    def clear_inputs(self):
        self.date_var.set(format_date_for_input(datetime.now()))
        self.cat_var.set("")
        self.amount_var.set("")
        self.note_var.set("")

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        # id, date, category, amount, note
        self.date_var.set(vals[1])
        self.cat_var.set(vals[2])
        self.amount_var.set(str(vals[3]))
        self.note_var.set(vals[4])

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a row to delete.")
            return
        vals = self.tree.item(sel[0])["values"]
        if messagebox.askyesno("Confirm", f"Delete expense {vals[0]}?"):
            delete_expense(vals[0])
            self.load_expenses()

    def update_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a row to update.")
            return
        vals = self.tree.item(sel[0])["values"]
        expense_id = vals[0]
        date = self.date_var.get().strip()
        cat = self.cat_var.get().strip() or "Other"
        amt = safe_float(self.amount_var.get().strip())
        note = self.note_var.get().strip()
        if amt <= 0:
            messagebox.showwarning("Invalid", "Enter valid amount.")
            return
        update_expense(expense_id, date, cat, amt, note)
        self.load_expenses()

    def apply_filter(self):
        cat = self.filter_cat.get()
        ffrom = self.from_var.get().strip()
        tto = self.to_var.get().strip()
        where_parts = []
        params = []
        if cat and cat != "All":
            where_parts.append("category = ?")
            params.append(cat)
        if ffrom:
            where_parts.append("date >= ?")
            params.append(ffrom)
        if tto:
            where_parts.append("date <= ?")
            params.append(tto)
        where = " AND ".join(where_parts)
        self.load_expenses(where, tuple(params))

    def clear_filter(self):
        self.filter_cat.set("All")
        self.from_var.set("")
        self.to_var.set("")
        self.load_expenses()

    def export_csv(self):
        rows = fetch_expenses()
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not file:
            return
        try:
            export_to_csv_pandas(rows, file)
            messagebox.showinfo("Exported", f"Exported to {file}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_monthly_summary(self):
        # Ask user for year-month
        ans = tk.simpledialog.askstring("Month", "Enter month (YYYY-MM):", parent=self.root)
        if not ans:
            return
        try:
            summary = fetch_monthly_summary(ans)
            text = "\n".join([f"{cat}: {amt:.2f}" for cat, amt in summary])
            total = sum([amt for _, amt in summary]) if summary else 0.0
            messagebox.showinfo(f"Summary {ans}", f"{text}\n\nTotal: {total:.2f}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
