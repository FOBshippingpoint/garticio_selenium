from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from my_webdriver import MyWebDriver
from threading import Thread
import gettext
import locale
import tomlkit
import webbrowser

rootdir = Path().resolve()
localedir = rootdir / "locale"
settings_path = Path(rootdir / "settings.toml")
settings = tomlkit.parse(settings_path.read_text(encoding="utf-8"))

available_langs = settings["preferences"]["available_languages"]

langs = {}
for l in available_langs:
    langs[l] = gettext.translation("messages", localedir, languages=[l])

# set lang:
# order: preferred > user_locale > default (en_US)
if settings["preferences"]["language"] != "":
    preferred_lang = settings["preferences"]["language"]
else:
    user_locale, encoding = locale.getdefaultlocale()
    preferred_lang = user_locale
try:
    langs[preferred_lang].install()
except:
    langs["en_US"].install()


class Gartic(tk.Tk):
    def __init__(self):
        super().__init__()

        rule = settings["control"]["rule"]
        default = settings["control"]["default"]

        self.title(_("Gartic Printer"))
        self.minsize(260, 200)
        self.option_add("*tearOff", False)

        menubar = tk.Menu(self)
        self.configure(menu=menubar)

        menu_pref = tk.Menu(menubar)
        menu_help = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_pref, label=_("Preferences"))
        menubar.add_cascade(menu=menu_help, label=_("Help"))
        menu_langs = tk.Menu(menubar)
        menu_pref.add_command(
            label=_("Save current settings"),
            command=self.save_current_control_to_default,
            underline=1,
        )
        menu_pref.add_cascade(menu=menu_langs, label=_("Languages"))
        for lang, native_name in settings["preferences"]["available_languages"].items():
            menu_langs.add_command(
                label=native_name + " (" + lang + ")",
                command=lambda l=lang: self.save_pref_lang(
                    l
                ),  # ref: https://stackoverflow.com/questions/66294226/why-for-sentence-in-add-command-does-not-work-properly
            )
        menu_help.add_command(
            label=_("Online User Manual"),
            command=lambda: self.event_generate("<<OpenOnlineUserManual>>"),
        )
        menu_help.add_command(
            label=_("About"), command=lambda: self.event_generate("<<OpenAbout>>")
        )

        mainframe = ttk.Frame(self, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky="nesw")
        self.rowconfigure(3, weight=1)
        self.columnconfigure(2, weight=1)

        # many duplicates code, not good
        # suffix
        self.suffix = tk.StringVar(value=default["suffix"])
        self.suffix.trace_add("write", self.on_value_change_wrapper("suffix"))
        self.suffix_entry = ttk.Entry(mainframe, textvariable=self.suffix)
        self.suffix_entry.grid(column=1, row=0, sticky="nesw")

        # color_num
        self.color_num = tk.StringVar()
        self.color_num.trace_add("write", self.on_value_change_wrapper("color_num"))
        okay_color_num_vcmd = self.register(self.is_okay_color_num)
        self.color_num_spinbox = ttk.Spinbox(
            mainframe,
            from_=rule["color_num"]["from"],
            to=rule["color_num"]["to"],
            validate="all",
            validatecommand=(okay_color_num_vcmd, "%P"),
            textvariable=self.color_num,
        )
        self.color_num_spinbox.set(default["color_num"])
        self.color_num_spinbox.grid(column=1, row=1, sticky="nesw")

        # zoom
        self.zoom = tk.StringVar()
        self.zoom.trace_add("write", self.on_value_change_wrapper("zoom"))
        okay_zoom_vcmd = self.register(self.is_okay_zoom)
        self.zoom_spinbox = ttk.Spinbox(
            mainframe,
            from_=rule["zoom"]["from"],
            to=rule["zoom"]["to"],
            validate="all",
            validatecommand=(okay_zoom_vcmd, "%P"),
            textvariable=self.zoom,
        )
        self.zoom_spinbox.set(default["zoom"])
        self.zoom_spinbox.grid(column=1, row=2, sticky="nesw")

        # sleep_ms
        self.sleep_ms = tk.StringVar()
        self.sleep_ms.trace_add("write", self.on_value_change_wrapper("sleep_ms"))
        okay_sleep_ms_vcmd = self.register(self.is_okay_sleep_ms)

        # 0.01 to 100
        sleep_ms_values = []
        start = int(rule["sleep_ms"]["from"] * 100)
        stop = int(rule["sleep_ms"]["to"] * 100 + 1)
        for num in range(start, stop):
            sleep_ms_values.append(str(num / 100))

        self.sleep_ms_spinbox = ttk.Spinbox(
            mainframe,
            values=sleep_ms_values,
            validate="all",
            validatecommand=(okay_sleep_ms_vcmd, "%P"),
            textvariable=self.sleep_ms,
        )
        self.sleep_ms_spinbox.set(default["sleep_ms"])
        self.sleep_ms_spinbox.grid(column=1, row=3, sticky="nesw")

        # btn
        self.btn = ttk.Button(
            mainframe, text=_("Open Browser"), command=self.run_driver_thread
        )
        self.btn.grid(column=0, row=4, columnspan=2, sticky="nesw")

        # status_lbl
        self.status_lbl = ttk.Label(mainframe, text="")
        self.status_lbl.grid(column=0, row=5, columnspan=2, sticky="w")

        # control labels
        ttk.Label(mainframe, text=_("Search suffix")).grid(column=0, row=0, sticky="e")
        ttk.Label(mainframe, text=_("Colors")).grid(column=0, row=1, sticky="e")
        ttk.Label(mainframe, text=_("Zoom")).grid(column=0, row=2, sticky="e")
        ttk.Label(mainframe, text=_("Sleep ms")).grid(column=0, row=3, sticky="e")

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.protocol("WM_DELETE_WINDOW", self.close)
        # why use wrapper?
        # bind func should accept parameter "event", so I set wrapper with *_ to omit it.
        self.bind(
            "<<OpenImageSearch>>",
            self.set_message_wrapper(_("please select target image.")),
        )
        self.bind(
            "<<StartPrint>>",
            self.set_message_wrapper(_("start printing. F3: pause/resume, F4: stop")),
        )
        self.bind("<<EndPrint>>", self.set_message_wrapper(_("print complete.")))
        self.bind(
            "<<Time'sUp>>",
            self.set_message_wrapper(_("time's up. interrupt printing.")),
        )
        self.bind(
            "<<UserPause>>",
            self.set_message_wrapper(_("pause printing.")),
        )
        self.bind(
            "<<UserStop>>",
            self.set_message_wrapper(_("stop printing.")),
        )
        self.bind("<<Waiting>>", self.set_message_wrapper(_("waiting for your turn.")))
        self.bind(
            "<<ImageFetchError>>",
            self.set_message_wrapper(
                _("error while fetching image, please try again.")
            ),
        )

        self.bind(
            "<<OpenOnlineUserManual>>",
            lambda _: webbrowser.open(settings["help"]["online_user_manual"]),
        )
        self.bind(
            "<<OpenAbout>>",
            lambda *args: messagebox.showinfo(
                message=_(
                    "Authors: CC Lan, Felian 1999, Elmer Chou\nLicense: MIT\nHome page: https://github.com/FOBshippingpoint/garticio_selenium"
                )
            ),
        )
        self.attributes("-topmost", True)

    def run_driver_thread(self):
        self.driver_thread = Thread(target=self.set_driver)
        self.driver_thread.start()

    def set_driver(self):
        def close():
            self.close_driver()
            self.btn.config(text=_("Open Browser"), command=self.run_driver_thread)

        self.btn.config(text=_("Close Browser"), command=close)
        self.set_message(_("starting browser."))
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
        from_ = settings["control"]["rule"]["color_num"]["from"]
        to = settings["control"]["rule"]["color_num"]["to"]
        return from_ <= int(text) <= to

    def is_okay_sleep_ms(self, text):
        if not text.isnumeric():
            return False
        from_ = settings["control"]["rule"]["sleep_ms"]["from"]
        to = settings["control"]["rule"]["sleep_ms"]["to"]
        return from_ <= float(text) <= to

    def is_okay_zoom(self, text):
        if not text.isnumeric():
            return False
        from_ = settings["control"]["rule"]["zoom"]["from"]
        to = settings["control"]["rule"]["zoom"]["to"]
        return from_ <= int(text) <= to

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

    def save_pref_lang(self, lang):
        messagebox.showinfo(
            message=_("Please restart the program to apply language settings.")
        )
        settings["preferences"]["language"] = lang
        settings_path.write_text(tomlkit.dumps(settings), encoding="utf-8")

    def save_current_control_to_default(self):
        default = settings["control"]["default"]
        default["suffix"] = self.suffix.get()
        default["color_num"] = int(self.color_num.get())
        default["sleep_ms"] = float(self.sleep_ms.get())
        default["zoom"] = int(self.zoom.get())
        settings_path.write_text(tomlkit.dumps(settings), encoding="utf-8")


def main():
    app = Gartic()
    app.mainloop()


if __name__ == "__main__":
    main()
