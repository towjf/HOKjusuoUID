HANDLERS = {}
PLUGIN_KWARGS = {}


class Plugins:
    def __init__(self, name="", force_prefix=None, allow_empty_prefix=None, **kwargs):
        self.name = name
        self.force_prefix = force_prefix or []
        self.allow_empty_prefix = allow_empty_prefix
        PLUGIN_KWARGS[name] = kwargs | {
            "force_prefix": self.force_prefix,
            "allow_empty_prefix": self.allow_empty_prefix,
        }


class SV:
    def __init__(self, name="", pm=6, priority=5, **kwargs):
        self.name = name
        self.pm = pm
        self.priority = priority

    def _register(self, kind, keyword, func, block, to_ai):
        key = keyword if isinstance(keyword, str) else keyword[0]
        HANDLERS[key] = {
            "func": func,
            "kind": kind,
            "block": block,
            "to_ai": to_ai,
            "sv": self.name,
        }
        return func

    def on_command(self, keyword, block=False, to_me=False, prefix=True, to_ai="",
                  covers=None, aliases=None, aside=None):
        def deco(func):
            result = self._register("command", keyword, func, block, to_ai)
            for alias in aliases or []:
                HANDLERS[alias] = HANDLERS[keyword if isinstance(keyword, str) else keyword[0]]
            return result
        return deco

    on_prefix = on_suffix = on_keyword = on_fullmatch = on_regex = on_command
