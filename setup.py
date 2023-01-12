from setuptools import setup, find_packages

setup(
    name='plater3d',
    version='0.0.1',
    install_requires=[],
    packages=find_packages(),
    scripts=['bin/plater3d', 'bin/parse_cli.py', 'bin/platepacker', 'bin/printplate', 'bin/vispackings', 'bin/diff_cura_settings.py', 'bin/pj3d', 'bin/adjpacking']
)
