import tkinter as tk
from tkinter import ttk
from my_webdriver import MyWebDriver
from threading import Thread


class Gartic:
    def __init__(self, root):
        self.root = root

        root.title("Gartic Printer")
        root.minsize(250, 100)

        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky="nsew")
        root.rowconfigure(3, weight=1)

        self.btn = ttk.Button(
            mainframe, text="Open Browser", command=self.run_driver_thread
        )
        self.btn.grid(column=0, row=0)
        self.btn.focus_set()
        self.search_suffix = tk.StringVar()
        self.search_suffix.set("")
        self.search_suffix.trace_add("write", self.on_entry_change)
        self.search_suffix_entry = ttk.Entry(mainframe, textvariable=self.search_suffix)
        self.search_suffix_entry.grid(column=0, row=1)

        self.lbl = ttk.Label(mainframe, text="")
        self.lbl.grid(column=0, row=2)

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        root.protocol("WM_DELETE_WINDOW", self.close)
        # why use lambda _:
        # bind func should accept parameter "event", so I set _ to omit it.
        root.bind(
            "<<OpenImageSearch>>",
            lambda _: self.set_message("please select target image."),
        )
        root.bind("<<StartPrint>>", lambda _: self.set_message("start printing."))
        root.bind("<<EndPrint>>", lambda _: self.set_message("print complete."))
        root.bind(
            "<<Time'sUp>>",
            lambda _: self.set_message("time's up. interrupt printing."),
        )
        root.bind(
            "<<UserPause>>",
            lambda _: self.set_message("pause printing."),
        )
        root.bind(
            "<<UserStop>>",
            lambda _: self.set_message("stop printing."),
        )
        root.bind("<<Waiting>>", lambda _: self.set_message("waiting for your turn."))
        root.bind(
            "<<ImageFetchError>>",
            lambda _: self.set_message("error while fetching image, please try again."),
        )

        root.attributes("-topmost", True)

    def run_driver_thread(self):
        self.driver_thread = Thread(target=self.set_driver)
        self.driver_thread.start()

    def set_driver(self):
        def close():
            self.close_driver()
            self.btn.config(text="Open Browser", command=self.run_driver_thread)

        self.btn.config(text="Close Browser", command=close)
        self.set_message("starting browser.")
        self.driver = MyWebDriver(self.root)

        self.driver.start()

    def close(self):
        self.root.destroy()
        self.close_driver()

    def close_driver(self):
        try:
            Thread(target=lambda: self.driver.close()).start()
        except:
            pass

    def set_message(self, message):
        self.lbl.configure(text=message)

    def on_entry_change(self, *args):
        suffix = self.search_suffix_entry.get()
        try:
            self.driver.set_suffix(suffix)
        except:
            pass


def main():
    root = tk.Tk()
    Gartic(root)
    root.mainloop()


if __name__ == "__main__":
    main()
