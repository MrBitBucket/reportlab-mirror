# -*- coding: UTF-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

long_description = """
The ReportLab Toolkit.
An Open Source Python library for generating PDFs and graphics.
""".strip()

setup(
    name="reportlab",
    version = "VERSION{2.2}VERSION"[8: - 8],
    license="BSD license (see license.txt for details), Copyright (c) 2000-2008, ReportLab Inc.",
    description="The Reportlab Toolkit",
    long_description=long_description,

    #classifiers = [x.strip() for x in """
    #    """.strip().splitlines()],

    author="Robinson, Watters, Lee, Precedo, Becker and many more...",
    author_email="info@reportlab.com",
    url="http://www.reportlab.com/",
    download_url = "http://www.reportlab.com/",

    install_requires = [
        "PIL>=1.1.6",
        ],

    package_dir = {
        '': 'src'
        },

    # packages = find_packages(exclude=['ez_setup']),

    packages=[ # include anything with an __init__
            'reportlab',
            'reportlab.extensions',
            'reportlab.graphics.charts',
            'reportlab.graphics.samples',
            'reportlab.graphics.widgets',
            'reportlab.graphics.barcode',
            'reportlab.graphics',
            'reportlab.lib',
            'reportlab.pdfbase',
            'reportlab.pdfgen',
            'reportlab.platypus',
             ],

    include_package_data = True,

    test_suite = "tests",

    #data_files = DATA_FILES.items(),
    #libraries = LIBRARIES,
    #ext_modules =   EXT_MODULES,

)
