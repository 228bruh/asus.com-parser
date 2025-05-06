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

        self.selectionTree = ttk.Treeview(root, columns=("ID", "Date", "Count"), show="headings", height=20)
        self.selectionTree.heading("ID", text="ID")
        self.selectionTree.heading("Date", text="Date")
        self.selectionTree.heading("Count", text="Count")
        self.selectionTree.column("ID", width=30)
        self.selectionTree.column("Date", width=180)
        self.selectionTree.column("Count", width=60)
        self.selectionTree.place(x=10, y=10)
        self.selectionTree.bind("<<TreeviewSelect>>", lambda event: self._on_selection_change())

        self.productsTree = ttk.Treeview(root, columns=("Name", "Price"), show="headings", height=23)
        self.productsTree.heading("Name", text="Name")
        self.productsTree.heading("Price", text="Price")
        self.productsTree.column("Name", width=1100)
        self.productsTree.column("Price", width=90)
        self.productsTree.place(x=300, y=10)

        self.syncBtn = tkinter.Button(root, text="Sync Parse", command=self._run_sync_parse)
        self.syncBtn.place(width=130, x=10, y=460)
        self.asyncBtn = tkinter.Button(root, text="Async Parse", command=self._run_async_parse)
        self.asyncBtn.place(width=130, x=153, y=460)

        self.sortVar = tkinter.StringVar(value="Name A-Z")
        self.sortCBox = ttk.Combobox(root, textvariable=self.sortVar, state="readonly", values=[
            "Name A-Z", "Name Z-A", "Price Low-High", "Price High-Low"])
        self.sortCBox.place(x=1342, y=510, width=150, height=30)
        self.sortCBox.bind("<<ComboboxSelected>>", lambda event: self._load_sorted_products())

        self.currentProducts = []

        self._load_selections()

        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)
        self.root.bind("<Control-q>", lambda event: self._on_exit())

    def _load_selections(self):
        for row in self.selectionTree.get_children():
            self.selectionTree.delete(row)

        selections = self.db.get_selections()
        for sel in selections:
            self.selectionTree.insert("", tkinter.END, values=sel)

    def _on_selection_change(self):
        selected = self.selectionTree.selection()
        if not selected:
            return
        item = self.selectionTree.item(selected[0])
        selectionID = item["values"][0]

        self.currentProducts = self.db.get_products_by_selecID(selectionID)
        self._load_sorted_products()

    def _load_sorted_products(self):
        sortType = self.sortVar.get()
        products = list(self.currentProducts)

        match sortType:
            case "Name A-Z":
                products.sort(key=lambda x: x[0].lower())
            case "Name Z-A":
                products.sort(key=lambda x: x[0].lower(), reverse=True)
            case "Price Low-High":
                products.sort(key=lambda x: float(x[1].replace("£", "").replace(",", "")))
            case "Price High-Low":
                products.sort(key=lambda x: float(x[1].replace("£", "").replace(",", "")), reverse=True)

        for row in self.productsTree.get_children():
            self.productsTree.delete(row)
        for name, price in products:
            self.productsTree.insert("", tkinter.END, values=(name, price))

    def _run_sync_parse(self):
        products = self.parser.sync_parse()
        self.db.insert_parsing_results(products)
        self._load_selections()

    def _run_async_parse(self):
        products = self.parser.async_parse()
        self.db.insert_parsing_results(products)
        self._load_selections()

    def _on_exit(self):
        self.db.close()
        self.root.destroy()


# root = tkinter.Tk()
# root.geometry("1500x700")
# app = App(root)
# root.mainloop()