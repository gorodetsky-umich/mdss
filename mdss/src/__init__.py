# src/__init__.py
from .main import simulation, custom_sim, post_process
try:
    from .aerostruct import Problem
except:
    pass

__all__ = ["simulation", "custom_sim", "post_process", "Problem"]