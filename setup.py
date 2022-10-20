#!/usr/bin/env python

from distutils.core import setup
deps = [
            "watchdog(==0.9.0)",
            "parse(==1.9.0)",
            "boto3(==1.9.79)",
            "docker(==3.7.0)",
            "datajoint(==0.11.3)",
            "wtforms(==2.3.3)",
            "cwltool"
      ]
setup(name='conduit',
      version='1.0',
      description='Conduit tool for SABER',
      author='Raphael Norman-Tenazas',
      author_email='raphael.norman-tenazas@jhuapl.edu',
      url='https://github.com/aplbrain/saber',
      packages=['conduit', 'conduit.utils'],
      scripts=['conduit/conduit'],
      install_requires=deps,
      setup_requires=deps

     )
