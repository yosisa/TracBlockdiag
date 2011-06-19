from setuptools import find_packages, setup

setup(name='TracBlockdiag',
      version='0.1.0',
      packages=find_packages(exclude=['*.tests*']),
      install_requires=['blockdiag>=0.8.1'],
      extras_require={
          'full': ['seqdiag>=0.3.5', 'actdiag>=0.1.5', 'nwdiag>=0.2.4']
          },
      entry_points = """
      [trac.plugins]
      tracblockdiag = tracblockdiag.plugin
      """
      )
