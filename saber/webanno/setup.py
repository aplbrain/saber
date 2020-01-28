import os
from distutils.core import setup

"""
git tag {VERSION}
git push --tags
python setup.py sdist upload -r pypi
"""

VERSION = "0.1.0"

setup(
    name="webanno",
    version=VERSION,
    author="Jordan Matelsky",
    author_email="j6k4m8@gmail.com",
    description=("Web annotation plugin platform"),
    license="Apache 2.0",
    keywords=[
    ],
    url="https://github.com/aplbrain/webanno/tarball/" + VERSION,
    packages=['webanno'],
    scripts=[
        'scripts/webanno'
    ],
    classifiers=[],
    install_requires=[
        'flask', 'flask_cors'
    ],
)
