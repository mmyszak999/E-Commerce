from copy import copy

PAGINATION_PARAMS_HEADERS = ["page", "size"]
SORT_PARAMS_HEADER = "sort"

PAGINATION_PARAMS_HEADERS_COPY = copy(PAGINATION_PARAMS_HEADERS)
PARAM_HEADERS_WITHOUT_FILTERS = PAGINATION_PARAMS_HEADERS_COPY + [SORT_PARAMS_HEADER]
