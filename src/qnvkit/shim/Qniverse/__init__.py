"""
Local stand-in for the C-DAC ``Qniverse`` package.

The real QSDK is not published on PyPI; it is available inside Qniverse JupyterLab.
``qnvkit.qsdk_adapter`` puts this folder on ``sys.path`` only when ``import Qniverse`` fails,
so the same code runs against the real SDK on the platform and against this stand-in locally.
"""

IS_LOCAL_STAND_IN = True
