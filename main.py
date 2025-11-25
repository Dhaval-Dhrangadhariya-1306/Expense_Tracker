import tkinter as tk
from ui import ExpenseApp

def main():
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
