# LED Matrix Display Stuff

This project was made for the [neon YSWS](https://github.com/hackclub/neon) and allows you to display up to 3 data points from an API. It's highly customizeable and can be tweaked to show many things.

## How to use

### Setup the server

First set up an api that will serve the metrics you want via a GET request (the data needs to be in the json format).
An example can be found [here](./server.py).

The example returns the following:

```json5
{ // Example data
    "CPU": 21,
    "RAM": 36,
    "Temp": 70
}
```

(the endpoint can return more than 3 data points but only 3 can be used)

### Configure the shown data

The default configuration will show CPU, RAM and Temperature values using the example server.

```json5
{
    "api_url": "http://example.com/data",  // Replace with the actual endpoint
    "size": [64, 32, 3],  // width, height, bit_depth
    "font": terminalio.FONT,
    "background_color": 0x000000,
    "update_interval": 1,  // in seconds
    "keep_values_on_fail": 5, // Persist data if the request fails (X times)
    "request_timeout": 5,  // in seconds
    "data": { // Maximum of 3 items
        "CPU": {
            "color": 0xFFFFFF, // Also acts as color if thresholds are not met
            "unit": "%", // Unit for the datapoint
            "placeholder": "0",  // Can be None to disable if not available
            "max_length": 3, // Max length of the data
            "thresholds": {
                "high": [90, 0xFF0000],
                "med": [50, 0xFFFF00],
                "low": [0, 0x00FF00], // If below this, the default color will be used
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
```
