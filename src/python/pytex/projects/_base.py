import os

import numpy as np
import matplotlib.pyplot as plt

from pytex.utils.cache import Cache

class BaseProject(object):

    def __init__(self, engine):
        self.engine   = engine
        self.settings = {}
        self.full_env = {}
        self.sql_path = None

    def log(self, *args, **pwargs):
        self.engine.log(*args, **pwargs)

    def setup(self, settings):
        self.settings = settings.copy()
        return True

    def project_environment(self):
        raise Exception("Not yet implemented")

    def load_environment(self):
        environment = self.project_environment()
        self.engine.write_data("project_environment.json", environment)
        self.full_env = self.settings.copy()
        self.full_env.update(environment)
        self.engine.write_data("full_environment.json", self.full_env)
        return self.full_env

    def from_db_template(self, template_name, mapped = False, local_env = None):
        sql_query = self.engine.render_sql_query(template_name+".sql", local_env)
        result = None
        with Cache(sql_query, self.engine.project_cache_path) as cache:
            if cache.data is not None:
                return cache.data
            result = self.query_db(template_name, sql_query, mapped = mapped, local_env = local_env)
            cache.persist(result)
        return result

    def query_db(self, template_name, sql_query, **pwargs):
        if self.engine.dummy_db:
            return self.query_dummy_db(template_name, **pwargs)
        raise Exception("Not yet implemented")

    def query_dummy_db(self, template_name, mapped = False, local_env = None):
        raise Exception("Not yet implemented")

    def generate_bar_plot(self, x, curves, rows, paths, title=None, ylabel=None, **pwargs):
        n_groups = len(rows)
        n_colors = len(curves)

        index = np.arange(n_groups)
        bar_width  = 1.0/(n_colors+0.5)
        bar_offset = (1.0-n_colors*bar_width)*0.5

        OPACITY = 1.0
        COLORS  = [
            "r",
            "b",
            "g",
        ]

        fig, ax = plt.subplots()

        for icolor, (curve_key, curve_title) in enumerate(curves):
            values = [ row.get(curve_key) for row in rows ]

            rects = plt.bar(index + bar_width*icolor+bar_offset, values, bar_width*0.9,
                alpha=OPACITY,
                color=COLORS[icolor%3],
                label=curve_title
            )

        x_key,x_title = x
        if x_title:
            plt.xlabel(x_title)
        if ylabel:
            plt.ylabel(ylabel)
        if title:
            plt.title(title)
        plt.xticks(index + bar_width*(n_colors-0.1)*0.5 + bar_offset, [ row.get(x_key) for row in rows ])
        plt.legend()

        plt.tight_layout()
        plt.savefig(paths["full"])
