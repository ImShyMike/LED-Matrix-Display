import time

import board
import displayio
import framebufferio
import requests
import rgbmatrix
import terminalio
from adafruit_display_text import label

# This is an example configuration

# INFO: each line has a maximum of 10 characters
CONFIG = {
    "api_url": "https://test.shymike.tech/data",  # Replace with the actual endpoint
    "size": [64, 32, 3],  # width, height, bit_depth
    "font": terminalio.FONT,
    "background_color": 0x000000,
    "update_interval": 1,  # in seconds
    "keep_values_on_fail": 5, # Dont reset to placeholder if data fetch fails for X retries
    "data": { # Maximum of 3 items
        "CPU": {
            "color": 0xFFFFFF, # Also acts as color if thresholds are not met
            "unit": "%",
            "placeholder": "0",  # Can be None to disable if not available
            "max_length": 3,
            "thresholds": {
                "high": [90, 0xFF0000],
                "med": [50, 0xFFFF00],
                "low": [0, 0x00FF00],
            },
        },
        "RAM": {
            "color": 0xFFFFFF,
            "unit": "%",
            "placeholder": "0",
            "max_length": 3,
            "thresholds": {
                "high": [70, 0xFF0000],
                "med": [50, 0xFFFF00],
                "low": [10, 0x00FF00],
            },
        },
        "Temp": {
            "color": 0xFFFFFF,
            "unit": "C",
            "placeholder": "0",
            "max_length": 3,
            "thresholds": {
                "high": [70, 0xFF0000],
                "med": [60, 0xFFFF00],
                "low": [40, 0x00FF00],
            },
        },
    },
}


def generate_labels(config):
    """Generate labels based on the config."""
    if len(config["data"]) > 3:
        raise ValueError("Maximum of 3 labels allowed.")
    labels = []
    for i, (key, value) in enumerate(config["data"].items()):
        label_size = len(key) + 2
        value_size = value["max_length"] + len(value["unit"])
        total_size = (
            label_size + value_size
        )
        if total_size > 10:
            raise ValueError(f"Size of {key} is too long. Max size is 10 characters.")
        label_text = f"%VALUE%{value['unit']}"
        key_label = label.Label(
            config["font"],
            text=f"{key}: ",
            color=value["color"],
            scale=1,
            x=2,
            y=5 + (i * 10),
        )
        new_label = label.Label(
            config["font"],
            text=label_text.replace("%VALUE%", value["placeholder"]).rjust(10),
            color=value["color"],
            scale=1,
            x=2,
            y=5 + (i * 10),
        )
        labels.append((new_label, label_text, key, key_label))
    return labels


def get_data_from_api() -> None | dict:
    """Fetch data from the an external API."""
    try:
        response = requests.get(CONFIG["api_url"], timeout=5)
        if response.status_code == 200:
            data = response.json()
            server_data = {}
            for item in CONFIG["data"]:
                if item in data:
                    server_data[item] = data[item]
            return server_data
        else:
            return None
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error fetching system data from API: {e}")
        return None


def get_color(value, thresholds, default_color):
    """Get color based on the value and thresholds."""
    try:
        value = int(value)
        if value >= thresholds["high"][0]:
            return thresholds["high"][1]  # High
        if value >= thresholds["med"][0]:
            return thresholds["med"][1]  # Medium
        if value >= thresholds["low"][0]:
            return thresholds["low"][1]  # low
        return default_color  # Default color
    except ValueError:
        return default_color  # If value is not an integer, use default color


def main():
    """Main function."""
    matrix = rgbmatrix.RGBMatrix(
        width=CONFIG["size"][0],
        height=CONFIG["size"][1],
        bit_depth=CONFIG["size"][2],
        rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
        addr_pins=[board.A5, board.A4, board.A3, board.A2],
        clock_pin=board.D13,
        latch_pin=board.D0,
        output_enable_pin=board.D1,
    )

    display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)
    main_screen = displayio.Group()

    # Create background once, no need to recreate it every loop
    background = displayio.TileGrid(
        displayio.Bitmap(display.width, display.height, 1),
        pixel_shader=displayio.Palette(1),
    )
    background.pixel_shader[0] = CONFIG["background_color"]  # Black background

    # Add background to the main screen group (just once)
    main_screen.append(background)

    labels = generate_labels(CONFIG)
    for item in labels:
        main_screen.append(item[3]) # Add the key label
        main_screen.append(item[0]) # Add the value label

    fail_count = 0

    while True:
        data = get_data_from_api()

        for label_item, label_text, label_name, key_label in labels:
            if not data:
                fail_count += 1
                if fail_count < CONFIG["keep_values_on_fail"]:
                    continue
                if CONFIG["data"][label_name]["placeholder"] is None:
                    label_item.text = ""
                    key_label.text = ""
                    continue
                data_str = CONFIG["data"][label_name]["placeholder"]
            else:
                data_str = data[label_name]
                fail_count = 0

            if key_label.text == "":
                key_label.text = f"{label_name}: "

            label_item.color = get_color(
                data_str,
                CONFIG["data"][label_name]["thresholds"],
                CONFIG["data"][label_name]["color"],
            )
            value = str(data_str)
            label_item.text = label_text.replace(
                "%VALUE%", value
            ).rjust(10)

        # Update display
        display.root_group = main_screen
        display.refresh()

        time.sleep(CONFIG["update_interval"])


if __name__ == "__main__":
    main()
