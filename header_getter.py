import logging
import re
from collections import namedtuple
from typing import Dict, List

import configs

Conf = namedtuple(
    "Conf", ["channel", "bsic_sc_pci", "param", "legend", "name_suffix"]
)


class HeaderResolver:
    def __init__(
        self,
        column_headers: List[str],
        patterns: Dict,
        specific_pattern: str = None,
    ):
        self.column_headers = column_headers
        self.column_headers_to_search = list(column_headers)
        self.patterns = patterns
        self.confs = list()
        self.specific_pattern = specific_pattern

    def searching(self, pattern):
        for header in self.column_headers_to_search:
            if re.search(pattern, header):
                self.column_headers_to_search.remove(header)
                return header

    def get_column_patterns(self, columns_patterns_name):
        try:
            column_patterns = self.patterns[columns_patterns_name]
        except:
            logging.critical(f"patterns: {self.patterns}")
            raise
        return column_patterns

    def get_header(self, column_patterns, obligatory=True):
        for pattern in column_patterns:
            search_result = self.searching(pattern)
            if search_result is not None:
                return search_result
        if obligatory:
            raise Exception(
                f"Шаблоны {column_patterns} не найдены в заголовках файла: "
                f"{self.column_headers}\n"
                f"Нераспределённые заголовки: {self.column_headers_to_search}"
            )

    def choose_coordinates_headers(self):
        longitude = self.get_header(configs.LONGITUDE_PATTERNS)
        latitude = self.get_header(configs.LATITUDE_PATTERNS)
        return longitude, latitude

    def fill_confs(self):
        confs = list()
        param_patterns = list(configs.PARAMETER_PATTERNS)
        if self.specific_pattern:
            param_patterns = [
                pattern
                for pattern in param_patterns
                if pattern == self.specific_pattern
            ]
        params = dict()
        while param_patterns:
            pattern = param_patterns.pop()
            param = self.searching(pattern)
            if param is not None:
                param_options = configs.PARAMETER_PATTERNS[pattern]
                params[param] = param_options
        if not params:
            raise Exception(
                "Не найдено ни одного параметра в заголовках файла:"
                f"{self.column_headers}\n"
                f"Нераспределённые заголовки: {self.column_headers_to_search}"
            )
        channel = self.get_header(configs.CHANNEL_PATTERNS, obligatory=False)
        bsic_sc_pci = self.get_header(configs.CELL_IDENTIFICATION_PATTERNS)
        for param, param_options in params.items():
            conf = Conf(
                channel,
                bsic_sc_pci,
                param,
                param_options.legend,
                param_options.suffix,
            )
            confs.append(conf)
        return confs
