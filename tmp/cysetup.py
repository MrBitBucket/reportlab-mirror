from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension("reportlab.lib._rl_accel_cy", ["src/reportlab/lib/_rl_accel.pyx"])]

setup(
      name = 'Hello world app',
      cmdclass = {'build_ext': build_ext},
      ext_modules = ext_modules
      )
