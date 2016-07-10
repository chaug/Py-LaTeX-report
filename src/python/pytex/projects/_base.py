import os

import numpy as np
import matplotlib.pyplot as plt

class BaseProject(object):

    def __init__(self, engine):
        self.engine   = engine
        self.config   = {}
        self.sql_path = None

    def log(self, *args, **pwargs):
        self.engine.log(*args, **pwargs)

    def setup_config(self, config, sql_path):
        self.config   = dict(config)
        self.sql_path = sql_path
        if not os.path.isdir(self.sql_path):
            raise Exception("SQL path doesn't exist {0}".format(sql_path))
        return True

    def scafold_environment(self, config):
        raise Exception("Not yet implemented")

    def from_db_template(self, template_name, mapped = False, local_env = None):
        if self.engine.dummy_db:
            return self.from_dummy_db(template_name, mapped = mapped, local_env = local_env)

        sql_query = self.engine.render_sql_query(template_name+".sql", local_env)

        raise Exception("Not yet implemented")

    def from_dummy_db(self, template_name, mapped = False, local_env = None):
        raise Exception("Not yet implemented")

    def generate_bar_plot(self, x, curves, rows, plot_filename, title=None, ylabel=None, **pwargs):
        n_groups = len(rows)
        n_colors = len(curves)

        index = np.arange(n_groups)
        bar_width = 1.0/(n_colors+0.5)

        OPACITY = 0.4
        COLORS  = [
            "r",
            "b",
        ]

        fig, ax = plt.subplots()

        for icolor, (curve_key, curve_title) in enumerate(curves):
            values = [ row.get(curve_key) for row in rows ]

            rects = plt.bar(index + bar_width*icolor, values, bar_width*0.9,
                alpha=OPACITY,
                color=COLORS[icolor%2],
                label=curve_title
            )

        x_key,x_title = x
        if x_title:
            plt.xlabel(x_title)
        if ylabel:
            plt.ylabel(ylabel)
        if title:
            plt.title(title)
        plt.xticks(index + (bar_width*n_colors)*0.5, [ row.get(x_key) for row in rows ])
        plt.legend()

        plt.tight_layout()
        plt.savefig(plot_filename)
