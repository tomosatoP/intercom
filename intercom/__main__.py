"""Application Entry"""

from pathlib import Path
from kivy.config import Config

log_dir = str(Path().absolute()) + "/logs"

# Kivy
# fullscreen: 0, 1, "auto", "fake"
# borderless: 0, 1
# custom_titlebar: 0, 1
# width: not used if fullscreen is set to "auto".
# height: not used if fullscreen is set to "auto".
# log_level: "trace", "debug", "info", "warning", "error", "critical"
Config.set("graphics", "fullscreen", "auto")
# Config.set("graphics", "borderless", 0)
# Config.set("graphics", "custom_titlebar", 1)
# Config.set("graphics", "width", 800)
# Config.set("graphics", "height", 480)
Config.set("graphics", "show_cursor", 0)  # 0, 1
Config.set("kivy", "log_dir", log_dir)
Config.set("kivy", "log_level", "info")
Config.set("kivy", "keyboard_mode", "dock")

# Kivy: Using Official RPi touch display
Config.set("input", "mouse", "mouse")
Config.set("input", "%(name)s", "")
Config.set("input", "hid_%(name)s", "probesysfs,provider=hidinput")


if __name__ == "__main__":
    # To use japanese font in Kivy
    from kivy.core.text import LabelBase, DEFAULT_FONT
    from kivy.resources import resource_add_path

    resource_add_path("/usr/share/fonts/opentype/ipaexfont-gothic")
    LabelBase.register(DEFAULT_FONT, "ipaexg.ttf")

    from intercom import IntercomApp

    IntercomApp().run()
