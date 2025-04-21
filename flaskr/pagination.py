import math

from flask import url_for


class Pagination:
    def __init__(self, pagination_params, endpoint=None, extra_args=None):
        self.per_page = pagination_params["per_page"]
        self.range_size = pagination_params["range_size"]
        self.total_items = pagination_params["total_items"]

        self._current_page = max(1, pagination_params["current_page"])
        page_count = math.ceil(self.total_items / self.per_page)
        self._current_page = min(self._current_page, page_count)
        self._total_pages = (self.total_items + self.per_page - 1) // self.per_page

        self._page_range_start = ((self._current_page - 1) // self.range_size) * self.range_size + 1
        self._page_range_end = min(self._page_range_start + self.range_size - 1, self._total_pages)
        self._endpoint = endpoint
        self._extra_args = extra_args

    @property
    def current_page(self):
        return self._current_page

    @property
    def total_pages(self):
        return self._total_pages

    @property
    def page_range(self):
        return range(self._page_range_start, self._page_range_end + 1)

    @property
    def has_previous_range(self):
        return self._page_range_start > 1

    @property
    def has_next_range(self):
        return self._page_range_end < self._total_pages

    @property
    def previous_range_page(self):
        return max(1, self._page_range_start - 1)

    @property
    def next_range_page(self):
        return min(self._total_pages, self._page_range_end + 1)

    def url_for_page(self, page):
        return url_for(self._endpoint, page=page, **self._extra_args)
