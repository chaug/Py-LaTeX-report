from pytex.projects._base import BaseProject

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
