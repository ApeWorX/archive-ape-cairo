from ape import plugins

from .compiler import CairoCompiler


@plugins.register(plugins.CompilerPlugin)
def register_compiler():
    return (".cairo",), CairoCompiler
