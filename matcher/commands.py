import sys
import contextlib
from operator import itemgetter

from flask import url_for
from flask_script import Command, Option, prompt_bool


class RoutesCommand(Command):
    """List registered routes"""

    def __init__(self, app):
        self.app = app

    def run(self):
        from urllib.parse import unquote
        output = []
        for rule in self.app.url_map.iter_rules():

            options = {}
            for arg in rule.arguments:
                options[arg] = "[{0}]".format(arg)

            methods = ','.join(rule.methods)
            url = url_for(rule.endpoint, **options)
            line = unquote("{:35s} {:35s} {}"
                           .format(rule.endpoint, methods, url))
            output.append((line, url))

        # Sort output by url not name
        for (line, _) in sorted(output, key=itemgetter(1)):
            print(line)


class NukeCommand(Command):
    """Nuke the database (except the platform table)"""

    def __init__(self, db):
        self.db = db

    def run(self):
        if prompt_bool(
            "This will remove all data (excluding platforms). Are you sure?",
            default=False
        ):
            with contextlib.closing(self.db.engine.connect()) as con:
                trans = con.begin()
                for table in reversed(self.db.metadata.sorted_tables):
                    if table.name not in ['platform', 'platform_group']:
                        con.execute(table.delete())
                trans.commit()
            print("Done.")
        else:
            print("Aborted.")


class MatchCommand(Command):
    """Run the matcher for a given scrap"""

    option_list = (
        Option('--scrap', '-s', dest='scrap'),
    )

    def run(self, scrap=None):
        from .scheme.platform import Scrap
        if scrap is None:
            scrap = Scrap.query.order_by(Scrap.id.desc()).first()
        else:
            scrap = Scrap.query.filter(Scrap.id == scrap).first()

        if scrap is None:
            print("Scrap not found")
            sys.exit(1)

        scrap.match_objects()
