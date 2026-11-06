from typing import Any, Dict, List, Optional, Union


class GsConfig:
    def __init__(self, title="", desc="", data=None, **kwargs):
        self.title = title
        self.desc = desc
        self.data = data
        for k, v in kwargs.items():
            setattr(self, k, v)


class GsStrConfig(GsConfig):
    pass


class GsIntConfig(GsConfig):
    pass


class GsFloatConfig(GsConfig):
    pass


class GsBoolConfig(GsConfig):
    pass


class GsDictConfig(GsConfig):
    pass


class GsListStrConfig(GsConfig):
    pass


class GsDivider(GsConfig):
    pass


GSC = Union[
    GsStrConfig,
    GsIntConfig,
    GsFloatConfig,
    GsBoolConfig,
    GsDictConfig,
    GsListStrConfig,
    GsDivider,
]
