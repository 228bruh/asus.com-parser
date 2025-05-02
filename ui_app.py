import tkinter
from tkinter import ttk
from parse_page import Parser
from db_manager import DatabaseManager

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("laptopsdirect.co.uk parser")

        self.db = DatabaseManager()
        self.parser = Parser()

        self.selection_tree = ttk.Treeview(root, columns=("ID", "Date", "Count"), show="headings", height=20)
        self.selection_tree.heading("ID", text="ID")
        self.selection_tree.heading("Date", text="Date")
        self.selection_tree.heading("Count", text="Count")
        self.selection_tree.column("ID", width=30)
        self.selection_tree.column("Date", width=180)
        self.selection_tree.column("Count", width=60)
        self.selection_tree.place(x=10, y=10)
        self.selection_tree.bind("<<TreeviewSelect>>", self.on_selection_change)

        self.product_tree = ttk.Treeview(root, columns=("Name", "Price"), show="headings", height=23)
        self.product_tree.heading("Name", text="Name")
        self.product_tree.heading("Price", text="Price")
        self.product_tree.column("Name", width=1100)
        self.product_tree.column("Price", width=90)
        self.product_tree.place(x=300, y=10)

        self.sync_btn = tkinter.Button(root, text="Sync Parse", command=self.run_sync_parse)
        self.sync_btn.place(width=130, x=10, y=460)
        self.async_btn = tkinter.Button(root, text="Async Parse", command=self.run_async_parse)
        self.async_btn.place(width=130, x=153, y=460)

        self.load_selections()

        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.root.bind("<Control-q>", lambda event: self.on_exit())

    def load_selections(self):
        for row in self.selection_tree.get_children():
            self.selection_tree.delete(row)

        selections = self.db.get_selections()
        for sel in selections:
            self.selection_tree.insert("", tkinter.END, values=sel)

    def on_selection_change(self, event):
        selected = self.selection_tree.selection()
        if not selected:
            return
        item = self.selection_tree.item(selected[0])
        selectionID = item["values"][0]

        for row in self.product_tree.get_children():
            self.product_tree.delete(row)
            
        products = self.db.get_products_by_selecID(selectionID)
        for name, price in products:
            self.product_tree.insert("", tkinter.END, values=(name, price))

    def run_sync_parse(self):
        products = self.parser.sync_parse()
        self.db.insert_parsing_results(products)
        self.load_selections()

    def run_async_parse(self):
        products = self.parser.async_parse()
        self.db.insert_parsing_results(products)
        self.load_selections()

    def on_exit(self):
        self.db.close()
        self.root.destroy()


# root = tkinter.Tk()
# root.geometry("1500x700")
# app = App(root)
# root.mainloop()