"""Microwave device template: defines common regions, controls, intents, and aliases."""

MICROWAVE_TEMPLATE = {
    "appliance_type": "microwave",
    "expected_regions": [
        {
            "id": "number_pad",
            "label": "Number Pad",
            "description": "Grid of number buttons 0-9, typically arranged in a 3x3+1 layout.",
        },
        {
            "id": "action_buttons",
            "label": "Action Buttons",
            "description": "Primary action controls like Start, Stop, Cancel.",
        },
        {
            "id": "mode_buttons",
            "label": "Mode Buttons",
            "description": "Cooking mode presets like Defrost, Reheat, Popcorn.",
        },
        {
            "id": "settings_row",
            "label": "Settings",
            "description": "Settings controls like Power Level, Clock, Timer.",
        },
        {
            "id": "display_area",
            "label": "Display",
            "description": "LCD or LED display showing time, power, or status.",
        },
    ],
    "common_controls": [
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "Start", "Stop", "Cancel", "Clear",
        "Time Cook", "Defrost", "Power Level", "Clock",
        "+30 Sec",
    ],
    "alias_map": {
        "start": ["begin", "go", "run", "+30 sec"],
        "stop": ["cancel", "clear", "off", "reset"],
        "time cook": ["cook time", "timed cook", "time", "manual cook", "manual"],
        "defrost": ["thaw", "defrost by weight", "defrost by time"],
        "power level": ["power", "power setting"],
        "clock": ["time of day", "set clock"],
        "+30 sec": ["30 sec", "+30", "add 30", "quick start"],
        "reheat": ["warm", "reheat"],
        "popcorn": ["popcorn"],
    },
    "known_intents": {
        "heat_for_time": {
            "description": "Cook/heat for a specified duration",
            "required_params": ["duration_seconds"],
            "typical_sequence": ["time_cook", "digits", "start"],
        },
        "defrost": {
            "description": "Defrost food",
            "required_params": [],
            "optional_params": ["duration_seconds", "weight"],
            "typical_sequence": ["defrost", "digits", "start"],
        },
        "set_power": {
            "description": "Set the power level",
            "required_params": ["power_level"],
            "typical_sequence": ["power_level", "digit"],
        },
        "quick_start": {
            "description": "Quick 30-second cook",
            "required_params": [],
            "typical_sequence": ["+30_sec"],
        },
        "stop": {
            "description": "Stop or cancel current operation",
            "required_params": [],
            "typical_sequence": ["stop"],
        },
        "start": {
            "description": "Start the microwave",
            "required_params": [],
            "typical_sequence": ["start"],
        },
    },
    "number_pad_layout": {
        "rows": [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["0"],
        ],
    },
}
