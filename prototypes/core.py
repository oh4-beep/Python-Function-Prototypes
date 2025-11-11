# prototypes/core.py
import inspect

_declared = {}

class _PrototypePlaceholder:
    """Callable placeholder for undeclared functions."""
    def __init__(self, name, argnames):
        self.__name__ = name
        self.argnames = argnames

    def __call__(self, *args, **kwargs):
        real = globals().get(self.__name__)
        if callable(real) and not isinstance(real, _PrototypePlaceholder):
            return real(*args, **kwargs)
        arglist = ", ".join(map(str, args))
        print(f"[prototype] '{self.__name__}' called before definition (args: {arglist})")

    def __repr__(self):
        return f"<prototype {self.__name__}({', '.join(self.argnames)})>"

def prototype(signature: str):
    """
    Declare a function prototype at runtime.
    Example:
        import prototypes as prototype
        prototype.prototype("greet(name)")
    """
    if "(" not in signature or not signature.endswith(")"):
        raise SyntaxError("Prototype must look like 'name(arg1, arg2)'")

    name, args_str = signature.split("(", 1)
    name = name.strip()
    args_str = args_str[:-1].strip()
    argnames = [a.strip() for a in args_str.split(",")] if args_str else []

    placeholder = _PrototypePlaceholder(name, argnames)
    _declared[name] = placeholder

    # Inject placeholder into the caller's global namespace
    frame = inspect.currentframe().f_back
    frame.f_globals[name] = placeholder

    return placeholder
