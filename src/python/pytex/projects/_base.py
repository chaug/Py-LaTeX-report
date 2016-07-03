import os

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
        if template_name == "get_networks":
            return [ ("DOMESTIC",), ("INTER",), ]
        if template_name == "get_top10_AU":
            return [
                { "FLIGHT_DATE" : "10-Jun-2016", "FLIGHT_NUMBER" : "255", "KPI" : 10.1, },
                { "FLIGHT_DATE" : "11-Jun-2016", "FLIGHT_NUMBER" : "974", "KPI" :  0.1, },
                { "FLIGHT_DATE" : "12-Jun-2016", "FLIGHT_NUMBER" : "371", "KPI" : 40.1, },
            ]
        if template_name.startswith("get_top10"):
            if local_env.get("network"):
                return [
                    { "FLIGHT_DATE" : "10-Jun-2015", "FLIGHT_NUMBER" : "255", "KPI" : 18.4, },
                    { "FLIGHT_DATE" : "11-Jun-2015", "FLIGHT_NUMBER" : "974", "KPI" :  8.4, },
                    { "FLIGHT_DATE" : "12-Jun-2015", "FLIGHT_NUMBER" : "371", "KPI" : 48.4, },
                ]
            else:
                return [
                    { "FLIGHT_DATE" : "10-Mar-2015", "FLIGHT_NUMBER" :  "55", "KPI" : 17.14, },
                    { "FLIGHT_DATE" : "11-Mar-2015", "FLIGHT_NUMBER" :  "74", "KPI" :  7.14, },
                    { "FLIGHT_DATE" : "12-Mar-2015", "FLIGHT_NUMBER" :  "71", "KPI" : 47.14, },
                ]
        # TODO
        return []
