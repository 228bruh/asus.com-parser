import tkinter
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
from parser import Parser
from DB_mngr import DatabaseManager

class App:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1500x655")
        self.root.title("laptopsdirect.co.uk parser")

        self.db = DatabaseManager()
        self.parser = Parser()

        self.currentProducts = []

        self._create_widgets()
        self._place_widgets()

        self._conf_dateEnries()
        self._load_selections()

        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)
        self.root.bind("<Control-q>", lambda event: self._on_exit())

    def _create_widgets(self):
        self.selectionTree = ttk.Treeview(self.root, columns=("ID", "Date", "Count"), show="headings", height=25)
        self.selectionTree.heading("ID", text="ID")
        self.selectionTree.heading("Date", text="Date")
        self.selectionTree.heading("Count", text="Count")
        self.selectionTree.column("ID", width=30)
        self.selectionTree.column("Date", width=180)
        self.selectionTree.column("Count", width=60)
        self.selectionTree.bind("<<TreeviewSelect>>", lambda event: self._on_selection_change())

        self.productsTree = ttk.Treeview(self.root, columns=("ID", "Name", "Price"), show="headings", height=28)
        self.productsTree.heading("ID", text="ID")
        self.productsTree.heading("Name", text="Name")
        self.productsTree.heading("Price", text="Price")
        self.productsTree.column("ID", width=30)
        self.productsTree.column("Name", width=1070)
        self.productsTree.column("Price", width=90)

        self.syncBtn = tkinter.Button(self.root, text="Sync Parse", command=self._run_sync_parse)
        self.asyncBtn = tkinter.Button(self.root, text="Async Parse", command=self._run_async_parse)

        self.sortCBox = ttk.Combobox(self.root, state="readonly", values=[
            "Name A-Z", "Name Z-A", "Price Low-High", "Price High-Low", "ID Low-High", "ID High-Low"])
        self.sortCBox.set("Name A-Z")
        self.sortCBox.bind("<<ComboboxSelected>>", lambda event: self._load_sorted_products())

        self.searchEntry = tkinter.Entry(self.root, foreground="grey")
        self.searchEntry.insert(0, "Search")
        self.searchEntry.bind("<FocusIn>", lambda event: self._set_placeholder(self.searchEntry, clear=True))
        self.searchEntry.bind("<FocusOut>", lambda event: self._set_placeholder(self.searchEntry, placeholder="Search"))
        self.searchEntry.bind("<Return>", lambda event: self._run_search())

        self.minPriceEntry = tkinter.Entry(self.root, foreground="grey")
        self.minPriceEntry.insert(0, "Min Price")
        self.minPriceEntry.bind("<FocusIn>", lambda event: self._set_placeholder(self.minPriceEntry, clear=True))
        self.minPriceEntry.bind("<FocusOut>", lambda event: self._set_placeholder(self.minPriceEntry, placeholder="Min Price"))
        self.minPriceEntry.bind("<Return>", lambda event: self._load_sorted_products())

        self.maxPriceEntry = tkinter.Entry(self.root, foreground="grey")
        self.maxPriceEntry.insert(0, "Max Price")
        self.maxPriceEntry.bind("<FocusIn>", lambda event: self._set_placeholder(self.maxPriceEntry, clear=True))
        self.maxPriceEntry.bind("<FocusOut>", lambda event: self._set_placeholder(self.maxPriceEntry, placeholder="Max Price"))
        self.maxPriceEntry.bind("<Return>", lambda event: self._load_sorted_products())

        self.fromDateEntry = DateEntry(self.root, date_pattern="dd.mm.yyyy", state="readonly", command=self._load_selections)
        self.fromDateEntry.bind("<<DateEntrySelected>>", lambda event: self._load_selections())

        self.toDateEntry = DateEntry(self.root, date_pattern="dd.mm.yyyy", state="readonly", command=self._load_selections)
        self.toDateEntry.bind("<<DateEntrySelected>>", lambda event: self._load_selections())

        self.vertSeparator = ttk.Separator(self.root, orient="vertical")
        self.horSeparator = ttk.Separator(self.root, orient="horizontal")
        self.horSeparator2 = ttk.Separator(self.root, orient="horizontal")
        self.fromLbl = tkinter.Label(self.root, text="From:")
        self.toLbl = tkinter.Label(self.root, text="To:")

    def _place_widgets(self):
        self.selectionTree.place(x=10, y=10)
        self.productsTree.place(x=300, y=10)

        self.syncBtn.place(width=130, height=30, x=10, y=615)
        self.asyncBtn.place(width=130, height=30, x=153, y=615)

        self.sortCBox.place(x=1342, y=615, width=150, height=30)
        self.searchEntry.place(x=300, y=615, width=300, height=30)
        self.minPriceEntry.place(x=1100, y=615, width=90, height=30)
        self.maxPriceEntry.place(x=1200, y=615, width=90, height=30)

        self.fromDateEntry.place(x=10, y=567, width=130, height=30)
        self.toDateEntry.place(x=153, y=567, width=130, height=30)

        self.vertSeparator.place(x=290, y=10, height=635)
        self.horSeparator.place(x=10, y=605, width=270)
        self.horSeparator2.place(x=300, y=605, width=1190)
        self.fromLbl.place(x=10, y=545, height=20)
        self.toLbl.place(x=153, y=545, height=20)

    def _load_selections(self):
        for row in self.selectionTree.get_children():
            self.selectionTree.delete(row)

        selections = self.db.get_selections()
        fromDate = self.fromDateEntry.get_date()
        toDate = self.toDateEntry.get_date()

        for sel in selections:
            selDate = datetime.strptime(sel[1], "%d.%m.%Y %H:%M:%S").date()
            if fromDate <= selDate <= toDate:
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
        products = list(self.currentProducts)

        # sorting
        sortType = self.sortCBox.get()
        match sortType:
            case "Name A-Z":
                products.sort(key=lambda x: x[1].lower())
            case "Name Z-A":
                products.sort(key=lambda x: x[1].lower(), reverse=True)
            case "Price Low-High":
                products.sort(key=lambda x: float(x[2].replace("£", "")) if x[2] != "Not found" else 0.0)
            case "Price High-Low":
                products.sort(key=lambda x: float(x[2].replace("£", "")) if x[2] != "Not found" else 0.0, reverse=True)
            case "ID Low-High":
                products.sort(key=lambda x: int(x[0]))
            case "ID High-Low":
                products.sort(key=lambda x: int(x[0]), reverse=True)

        # filter
        min_price_str = self.minPriceEntry.get()
        max_price_str = self.maxPriceEntry.get()
        try:
            min_price = float(min_price_str)
        except ValueError:
            min_price = None
        try:
            max_price = float(max_price_str)
        except ValueError:
            max_price = None

        if min_price is not None:
            products = [p for p in products if p[2] != "Not found" and float(p[2].replace("£", "")) >= min_price]
        if max_price is not None:
            products = [p for p in products if p[2] != "Not found" and float(p[2].replace("£", "")) <= max_price]


        for row in self.productsTree.get_children():
            self.productsTree.delete(row)
        for id, name, price in products:
            self.productsTree.insert("", tkinter.END, values=(id, name, price))

    def _set_placeholder(self, entry, placeholder="", clear=False):
        if clear == False:
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(foreground="grey")
        else:
            if entry.get() in ("Search", "Min Price", "Max Price"):
                entry.delete(0, tkinter.END)
                entry.config(foreground="black")

    def _run_search(self):
        query = self.searchEntry.get().strip()
        if not query or query == "Search":
            return

        products = self.db.search_products(query)
        self.currentProducts = products
        self._load_sorted_products()

    def _conf_dateEnries(self):
        selections = self.db.get_selections()
        if not selections: return

        minDate = datetime.strptime(selections[0][1], "%d.%m.%Y %H:%M:%S").date()
        maxDate = datetime.strptime(selections[-1][1], "%d.%m.%Y %H:%M:%S").date()
        
        self.fromDateEntry.config(mindate=minDate, maxdate=maxDate)
        self.toDateEntry.config(mindate=minDate, maxdate=maxDate)
        self.fromDateEntry.set_date(minDate)
        self.toDateEntry.set_date(maxDate)

    def _run_sync_parse(self):
        products = self.parser.sync_parse()
        self.db.insert_parsing_results(products)
        self._conf_dateEnries()
        self._load_selections()

    def _run_async_parse(self):
        products = self.parser.async_parse()
        self.db.insert_parsing_results(products)
        self._conf_dateEnries()
        self._load_selections()

    def _on_exit(self):
        self.db.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tkinter.Tk()
    app = App(root)
    root.mainloop()