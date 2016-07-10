from pytex.projects._base import BaseProject

import itertools
import os

class Project(BaseProject):

    AVAILABLE_KPI = [
        ("OB"  , "Overbooking"),
        ("AU"  , "Authorisation Level"),
        ("Prot", "Protection"),
    ]

    def setup_config(self, config, sql_path):
        if not super(Project,self).setup_config(config, sql_path):
            return False

        self.airline = config.get("airline")
        if not self.airline:
            raise Exception("Airline not in config")

        self.excluded_kpis     = config.get("excluded_kpis")     or []
        self.excluded_networks = config.get("excluded_networks") or []

        return True

    def scafold_environment(self):
        self.log(0,"Scafold Environment")
        environment = {}

        self.log(1,"Retrieve KPIs")
        environment["kpi"] = [
            {
                "key"     : key,
                "display" : display,
            }
            for key, display in self.AVAILABLE_KPI
            if  key      not in self.excluded_kpis
        ]

        self.log(1,"Retrieve Networks")
        environment["network"] = [
            {
                "key"     : row[0].replace(" ","_"),
                "display" : row[0].replace("_"," "),
            }
            for row        in self.from_db_template("get_networks")
            if  row[0] not in self.excluded_networks
        ]

        return environment

    ###############################################################################
    # Actions

    def top10(self, src, dest, env = None):
        loop = dict(env.get("loop") or {})
        self.log(1, "TOP 10 for {0}".format(
            ",".join(
                "{0}={1}".format(k,v.get("key"))
                for k,v in loop.items()
            )
        ))

        kpi = loop["kpi"]
        env["local"] = {
            "top10" : {
                "header" : ["Flight Number", "Flight Date", kpi["display"]],
                "rows"   : self.from_db_template("get_top10_{0}".format(kpi["key"]), mapped = True, local_env = loop),
            },
        }
        self.engine.render_mustache(src,dest, env = env)

    def curves_AU(self, src, dest, env = None):
        loop = dict(env.get("loop") or {})
        self.log(1, "Curves of AU for {0}".format(
            ",".join(
                "{0}={1}".format(k,v.get("key"))
                for k,v in loop.items()
            )
        ))

        network = loop["network"]["key"]
        allRows = filter(
            lambda x: x["NETWORK"] == network,
            self.from_db_template("get_AU", mapped = True, local_env = loop)
        )
        self.log(2, "get_AU %d rows" % len(allRows))
        key = lambda x : x.get("CABIN_CODE")
        rowsByCabin = [ (cabin_code, list(rows)) for cabin_code, rows in itertools.groupby(sorted(allRows, key=key), key=key)]
        self.log(2, "get_AU %d cabins" % len(rowsByCabin))

        folder, filename = os.path.split(dest)
        basename, ext    = os.path.splitext(filename)
        env["local"] = {
            "curves_AU" : [
                {
                    "cabin_code"    : cabin_code,
                    "rows"          : rows,
                    "plot_filename" : "{0}/{1}-{2}.png".format(folder,basename,cabin_code),
                    "title"         : "Network {0}, Cabin {1}".format(network,cabin_code),
                    "ylabel"        : "Authorisation Level",
                }
                for cabin_code, rows in rowsByCabin
            ],
        }
        for cabin_env in env["local"]["curves_AU"]:
            self.generate_bar_plot(
                x = ("BOOKING_CLASS_CODE", None),
                curves = [
                    ("AU_LEGACY", "Legacy AU"),
                    ("AU_SHADOW", "Altea AU"),
                ],
                **cabin_env
            )
        self.engine.render_mustache(src,dest, env = env)

    ###############################################################################
    # Dummy sources

    def from_dummy_db(self, template_name, mapped = False, local_env = None):
        if template_name == "get_networks":
            return [ ("DOMESTIC",), ("INTER",), ]
        if template_name == "get_AU":
            return [
                { "NETWORK" : "DOMESTIC", "CABIN_CODE" : "Y", "BOOKING_CLASS_CODE" : "Y", "AU_LEGACY" : 80.0, "AU_SHADOW" : 84.0, },
                { "NETWORK" : "DOMESTIC", "CABIN_CODE" : "Y", "BOOKING_CLASS_CODE" : "B", "AU_LEGACY" : 70.0, "AU_SHADOW" : 72.0, },
                { "NETWORK" : "DOMESTIC", "CABIN_CODE" : "Y", "BOOKING_CLASS_CODE" : "H", "AU_LEGACY" : 65.0, "AU_SHADOW" : 68.0, },
                { "NETWORK" : "DOMESTIC", "CABIN_CODE" : "Y", "BOOKING_CLASS_CODE" : "L", "AU_LEGACY" : 62.0, "AU_SHADOW" : 42.0, },
                { "NETWORK" : "DOMESTIC", "CABIN_CODE" : "Y", "BOOKING_CLASS_CODE" : "V", "AU_LEGACY" : 60.0, "AU_SHADOW" : 40.0, },
                { "NETWORK" : "DOMESTIC", "CABIN_CODE" : "Y", "BOOKING_CLASS_CODE" : "U", "AU_LEGACY" : 60.0, "AU_SHADOW" : 40.0, },
                { "NETWORK" : "DOMESTIC", "CABIN_CODE" : "Y", "BOOKING_CLASS_CODE" : "Q", "AU_LEGACY" : 40.0, "AU_SHADOW" : 30.0, },
                { "NETWORK" : "INTER"   , "CABIN_CODE" : "J", "BOOKING_CLASS_CODE" : "J", "AU_LEGACY" : 15.0, "AU_SHADOW" : 11.0, },
                { "NETWORK" : "INTER"   , "CABIN_CODE" : "J", "BOOKING_CLASS_CODE" : "C", "AU_LEGACY" : 10.0, "AU_SHADOW" : 10.0, },
                { "NETWORK" : "INTER"   , "CABIN_CODE" : "J", "BOOKING_CLASS_CODE" : "D", "AU_LEGACY" : 10.0, "AU_SHADOW" : 10.0, },
                { "NETWORK" : "INTER"   , "CABIN_CODE" : "J", "BOOKING_CLASS_CODE" : "I", "AU_LEGACY" :  2.0, "AU_SHADOW" :  8.0, },
                { "NETWORK" : "INTER"   , "CABIN_CODE" : "Y", "BOOKING_CLASS_CODE" : "Y", "AU_LEGACY" : 60.0, "AU_SHADOW" : 70.0, },
                { "NETWORK" : "INTER"   , "CABIN_CODE" : "Y", "BOOKING_CLASS_CODE" : "B", "AU_LEGACY" : 50.0, "AU_SHADOW" : 40.0, },
                { "NETWORK" : "INTER"   , "CABIN_CODE" : "Y", "BOOKING_CLASS_CODE" : "H", "AU_LEGACY" : 40.0, "AU_SHADOW" : 30.0, },
                { "NETWORK" : "INTER"   , "CABIN_CODE" : "Y", "BOOKING_CLASS_CODE" : "L", "AU_LEGACY" : 20.0, "AU_SHADOW" : 10.0, },
            ]
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
