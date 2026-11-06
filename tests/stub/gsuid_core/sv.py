"""gsuid_core.sv 的最小桩：模拟 Plugins 前缀展开，便于检查命令是否重复注册。"""

HANDLERS = {}
PLUGIN_KWARGS = {}
SV_LIST = {}

_CURRENT = {}


class Plugins:
    def __init__(
        self,
        name="",
        pm=6,
        priority=5,
        enabled=True,
        area="SV",
        black_list=None,
        white_list=None,
        sv=None,
        prefix=None,
        force_prefix=None,
        disable_force_prefix=False,
        allow_empty_prefix=None,
        force=False,
        alias=None,
        **kwargs,
    ):
        prefix = [prefix] if isinstance(prefix, str) else list(prefix or [])
        force_prefix = list(force_prefix or [])
        if allow_empty_prefix is None:
            _pf = [p for p in prefix + force_prefix if p != ""]
            allow_empty_prefix = not _pf

        self.name = name
        self.prefix = prefix
        self.force_prefix = force_prefix
        self.allow_empty_prefix = allow_empty_prefix
        self.disable_force_prefix = disable_force_prefix

        PLUGIN_KWARGS[name] = {
            "prefix": prefix,
            "force_prefix": force_prefix,
            "allow_empty_prefix": allow_empty_prefix,
        }
        _CURRENT[name] = self


def _expand_prefixes() -> list[str]:
    """复刻 gsuid_core.sv.SV._on 的前缀展开逻辑（含空前缀）。"""
    cfg = next(iter(_CURRENT.values()), None)
    if cfg is None:
        return [""]
    prefixes = [p for p in cfg.prefix if p != ""]
    if not cfg.disable_force_prefix:
        prefixes.extend(cfg.force_prefix)
    if cfg.allow_empty_prefix:
        prefixes.append("")
    return list(dict.fromkeys(prefixes))


class SV:
    def __init__(self, name="", pm=6, priority=5, enabled=True, area="ALL", **kwargs):
        self.name = name
        self.pm = pm
        self.priority = priority
        self.enabled = enabled
        SV_LIST[name] = self

    def _register(self, kind, keyword, func, block, to_ai):
        keywords = (keyword,) if isinstance(keyword, str) else tuple(keyword)
        prefixes = _expand_prefixes()
        for kw in keywords:
            for prefix in prefixes or [""]:
                HANDLERS[f"{prefix}{kw}"] = {
                    "func": func,
                    "kind": kind,
                    "block": block,
                    "to_ai": to_ai,
                    "sv": self.name,
                    "pm": self.pm,
                }
        return func

    def on_command(
        self,
        keyword,
        block=False,
        to_me=False,
        prefix=True,
        to_ai="",
        covers=None,
        aliases=None,
        aside=None,
    ):
        def deco(func):
            return self._register("command", keyword, func, block, to_ai)

        return deco

    on_prefix = on_suffix = on_keyword = on_fullmatch = on_regex = on_command
