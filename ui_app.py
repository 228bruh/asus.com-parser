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

        self.selectionTree = ttk.Treeview(root, columns=("ID", "Date", "Count"), show="headings", height=25)
        self.selectionTree.heading("ID", text="ID")
        self.selectionTree.heading("Date", text="Date")
        self.selectionTree.heading("Count", text="Count")
        self.selectionTree.column("ID", width=30)
        self.selectionTree.column("Date", width=180)
        self.selectionTree.column("Count", width=60)
        self.selectionTree.place(x=10, y=10)
        self.selectionTree.bind("<<TreeviewSelect>>", lambda event: self._on_selection_change())

        self.productsTree = ttk.Treeview(root, columns=("ID", "Name", "Price"), show="headings", height=28)
        self.productsTree.heading("ID", text="ID")
        self.productsTree.heading("Name", text="Name")
        self.productsTree.heading("Price", text="Price")
        self.productsTree.column("ID", width=30)
        self.productsTree.column("Name", width=1070)
        self.productsTree.column("Price", width=90)
        self.productsTree.place(x=300, y=10)

        self.syncBtn = tkinter.Button(root, text="Sync Parse", command=self._run_sync_parse)
        self.syncBtn.place(width=130, x=10, y=560)
        self.asyncBtn = tkinter.Button(root, text="Async Parse", command=self._run_async_parse)
        self.asyncBtn.place(width=130, x=153, y=560)

        self.sortCBox = ttk.Combobox(root, state="readonly", values=[
            "Name A-Z", "Name Z-A", "Price Low-High", "Price High-Low", "ID Low-High", "ID High-Low"])
        self.sortCBox.set("Name A-Z")
        self.sortCBox.place(x=1342, y=610, width=150, height=30)
        self.sortCBox.bind("<<ComboboxSelected>>", lambda event: self._load_sorted_products())

        self.searchEntry = tkinter.Entry(root, foreground="grey")
        self.searchEntry.insert(0, "Search")
        self.searchEntry.place(x=300, y=610, width=300, height=30)
        self.searchEntry.bind("<FocusIn>", lambda event: self._clear_placeholder())
        self.searchEntry.bind("<FocusOut>", lambda event: self._set_placeholder())
        self.searchEntry.bind("<Return>", lambda event: self._run_search())

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
        sortType = self.sortCBox.get()
        products = list(self.currentProducts)

        match sortType:
            case "Name A-Z":
                products.sort(key=lambda x: x[1].lower())
            case "Name Z-A":
                products.sort(key=lambda x: x[1].lower(), reverse=True)
            case "Price Low-High":
                products.sort(key=lambda x: float(x[2].replace("£", "").replace(",", "")))
            case "Price High-Low":
                products.sort(key=lambda x: float(x[2].replace("£", "").replace(",", "")), reverse=True)
            case "ID Low-High":
                products.sort(key=lambda x: int(x[0]))
            case "ID High-Low":
                products.sort(key=lambda x: int(x[0]), reverse=True)

        for row in self.productsTree.get_children():
            self.productsTree.delete(row)
        for id, name, price in products:
            self.productsTree.insert("", tkinter.END, values=(id, name, price))

    def _clear_placeholder(self):
        if self.searchEntry.get() == "Search":
            self.searchEntry.delete(0, tkinter.END)
            self.searchEntry.config(foreground="black")

    def _set_placeholder(self):
        if not self.searchEntry.get():
            self.searchEntry.insert(0, "Search")
            self.searchEntry.config(foreground="grey")

    def _run_search(self):
        query = self.searchEntry.get().strip()
        if not query or query == "Search":
            return

        products = self.db.search_products(query)
        self.currentProducts = products
        self._load_sorted_products()

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


root = tkinter.Tk()
root.geometry("1500x700")
app = App(root)
root.mainloop()