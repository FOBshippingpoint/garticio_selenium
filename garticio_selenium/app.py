import tkinter as tk
from tkinter import ttk
from my_webdriver import MyWebDriver
from threading import Thread


class Gartic(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Gartic Printer")
        self.minsize(260, 200)

        mainframe = ttk.Frame(self, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky="nesw")
        self.rowconfigure(3, weight=1)
        self.columnconfigure(2, weight=1)

        # many duplicates code, not good
        # suffix
        self.suffix = tk.StringVar(value="")
        self.suffix.trace_add("write", self.on_value_change_wrapper("suffix"))
        self.suffix_entry = ttk.Entry(mainframe, textvariable=self.suffix)
        self.suffix_entry.grid(column=1, row=0, sticky="nesw")

        # color_num
        self.color_num = tk.StringVar()
        self.color_num.trace_add("write", self.on_value_change_wrapper("color_num"))
        okay_color_num_vcmd = self.register(self.is_okay_color_num)
        self.color_num_spinbox = ttk.Spinbox(
            mainframe,
            from_=1,
            to=32,
            validate="all",
            validatecommand=(okay_color_num_vcmd, "%P"),
            textvariable=self.color_num,
        )
        self.color_num_spinbox.set("16")
        self.color_num_spinbox.grid(column=1, row=1, sticky="nesw")

        # zoom
        self.zoom = tk.StringVar()
        self.zoom.trace_add("write", self.on_value_change_wrapper("zoom"))
        okay_zoom_vcmd = self.register(self.is_okay_zoom)
        self.zoom_spinbox = ttk.Spinbox(
            mainframe,
            from_=10,
            to=100,
            validate="all",
            validatecommand=(okay_zoom_vcmd, "%P"),
            textvariable=self.zoom,
        )
        self.zoom_spinbox.set("80")
        self.zoom_spinbox.grid(column=1, row=2, sticky="nesw")

        # sleep_ms
        self.sleep_ms = tk.StringVar()
        self.sleep_ms.trace_add("write", self.on_value_change_wrapper("sleep_ms"))
        okay_sleep_ms_vcmd = self.register(self.is_okay_sleep_ms)

        # 0.01 to 100
        sleep_ms_values = []
        for num in range(1, 10001):
            sleep_ms_values.append(str(num / 100))

        self.sleep_ms_spinbox = ttk.Spinbox(
            mainframe,
            values=sleep_ms_values,
            validate="all",
            validatecommand=(okay_sleep_ms_vcmd, "%P"),
            textvariable=self.sleep_ms,
        )
        self.sleep_ms_spinbox.set("0.01")
        self.sleep_ms_spinbox.grid(column=1, row=3, sticky="nesw")

        # btn
        self.btn = ttk.Button(
            mainframe, text="Open Browser", command=self.run_driver_thread
        )
        self.btn.grid(column=0, row=4, columnspan=2, sticky="nesw")

        # status_lbl
        self.status_lbl = ttk.Label(mainframe, text="")
        self.status_lbl.grid(column=0, row=5, columnspan=2, sticky="w")

        # control labels
        ttk.Label(mainframe, text="Search suffix").grid(column=0, row=0, sticky="e")
        ttk.Label(mainframe, text="Colors").grid(column=0, row=1, sticky="e")
        ttk.Label(mainframe, text="Zoom").grid(column=0, row=2, sticky="e")
        ttk.Label(mainframe, text="Sleep ms").grid(column=0, row=3, sticky="e")

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.protocol("WM_DELETE_WINDOW", self.close)
        # why use lambda _:
        # bind func should accept parameter "event", so I set _ to omit it.
        self.bind(
            "<<OpenImageSearch>>",
            self.set_message_wrapper("please select target image."),
        )
        self.bind(
            "<<StartPrint>>",
            self.set_message_wrapper("start printing. F3: pause/resume, F4: stop"),
        )
        self.bind("<<EndPrint>>", self.set_message_wrapper("print complete."))
        self.bind(
            "<<Time'sUp>>",
            self.set_message_wrapper("time's up. interrupt printing."),
        )
        self.bind(
            "<<UserPause>>",
            self.set_message_wrapper("pause printing."),
        )
        self.bind(
            "<<UserStop>>",
            self.set_message_wrapper("stop printing."),
        )
        self.bind("<<Waiting>>", self.set_message_wrapper("waiting for your turn."))
        self.bind(
            "<<ImageFetchError>>",
            self.set_message_wrapper("error while fetching image, please try again."),
        )

        self.attributes("-topmost", True)

    def run_driver_thread(self):
        self.driver_thread = Thread(target=self.set_driver)
        self.driver_thread.start()

    def set_driver(self):
        def close():
            self.close_driver()
            self.btn.config(text="Open Browser", command=self.run_driver_thread)

        self.btn.config(text="Close Browser", command=close)
        self.set_message("starting browser.")
        self.driver = MyWebDriver(
            self,
            suffix=self.suffix.get(),
            color_num=int(self.color_num.get()),
            zoom=int(self.zoom.get()),
            sleep_ms=float(self.sleep_ms.get()),
        )

        self.driver.start()

    def close(self):
        self.destroy()
        self.close_driver()

    def close_driver(self):
        try:
            Thread(target=lambda: self.driver.close()).start()
        except:
            pass

    def set_message(self, message):
        self.status_lbl.configure(text=message)

    def set_message_wrapper(self, message):
        def wrapper(*_):
            self.set_message(message)

        return wrapper

    # validation funcs
    def is_okay_color_num(self, text):
        if not text.isnumeric():
            return False
        return 1 <= int(text) <= 32

    def is_okay_sleep_ms(self, text):
        if not text.isnumeric():
            return False
        return 0.01 <= float(text) <= 1000

    def is_okay_zoom(self, text):
        if not text.isnumeric():
            return False
        return 10 <= int(text) <= 100

    def on_value_change_wrapper(self, val_name):
        # ref: https://www.tcl.tk/man/tcl8.4/TclCmd/trace.html#M6
        def wrapper(*_):
            try:
                val = ""
                if val_name == "suffix":
                    val = self.suffix.get()
                elif val_name == "color_num":
                    val = int(self.color_num.get())
                elif val_name == "sleep_ms":
                    val = float(self.sleep_ms.get())
                elif val_name == "zoom":
                    val = int(self.zoom.get())
                setattr(self.driver, val_name, val)
            except Exception as e:
                print(e)
                pass

        return wrapper


def main():
    app = Gartic()
    app.mainloop()


if __name__ == "__main__":
    main()
