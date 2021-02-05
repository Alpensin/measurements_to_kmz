import legends as __legends
from collections import namedtuple as __namedtuple

LONGITUDE_PATTERNS = ("Lon.", "Longitude")
LATITUDE_PATTERNS = ("Lat.", "Latitude")
CHANNEL_PATTERNS = (
    "BCCH",  # None is possible
    "Ch",
    "ARFCN",
)

CELL_IDENTIFICATION_PATTERNS = (
    "PSC",
    "PCI",
    "BSIC",
    "Cell",
)
__param_options = (
    ("RxLev", __legends.RX_LEV_LEGEND, "RxLev"),
    ("RxQual", __legends.RX_QUAL_LEGEND, "RxQual"),
    ("RSCP", __legends.RSCP_LEGEND, "RSCP"),
    (r"Ec\b", __legends.RSCP_LEGEND, "RSCP"),
    ("EcIo", __legends.ECNO_LEGEND, "EcNo"),
    ("RSCP", __legends.RSCP_LEGEND, "RSCP"),
    ("RSRP", __legends.RSRP_LEGEND, "RSRP"),
    ("CINR", __legends.SINR_LEGEND, "CINR"),
    ("PCI_PARAM", __legends.PCI_LEGEND, "PCI"),
)
__Param = __namedtuple("ParamOptions", ["pattern", "legend", "suffix"])
_params = (__Param(*i) for i in __param_options)

PARAMETER_PATTERNS = dict((param.pattern, param) for param in _params)


def get_patterns():
    return dict((k, v) for k, v in globals().items() if "_PATTERNS" in k)
