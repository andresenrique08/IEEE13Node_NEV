""" This script contains constants to handle the analysis of IEEE 13 nodes network."""

NODES_ORDER = {
    'sourcebus': 0,
    '650': 1,
    'rg60': 2,
    '632': 3,
    '645': 4,
    '646': 5,
    '633': 6,
    '634': 7,
    '670': 8,
    '671': 9,
    '684': 10,
    '611': 11,
    '652': 12,
    '692': 13,
    '675': 14,
    '680': 15
}

NODES_NUMBER_NAME = {
    1: "a",
    2: "b",
    3: "c",
    4: "n"
}

NODES_NUMBER = list(NODES_NUMBER_NAME.keys())
NODES_NAME = list(NODES_NUMBER_NAME.values())