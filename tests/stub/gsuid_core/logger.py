class _Logger:
    def info(self, msg, *a, **k): print("[info]", msg)
    def success(self, msg, *a, **k): print("[ok]", msg)
    def warning(self, msg, *a, **k): print("[warn]", msg)
    def error(self, msg, *a, **k): print("[err]", msg)
    def debug(self, msg, *a, **k): pass
    def trace(self, msg, *a, **k): pass
    def exception(self, msg, *a, **k): print("[exc]", msg)

logger = _Logger()
