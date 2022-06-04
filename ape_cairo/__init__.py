from ape import plugins

from .compiler import CairoCompiler, CairoConfig


@plugins.register(plugins.Config)
def config_class():
    return CairoConfig


@plugins.register(plugins.CompilerPlugin)
def register_compiler():
    return (".cairo",), CairoCompiler
