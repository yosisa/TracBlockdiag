from setuptools import find_packages, setup

setup(name='TracBlockdiagPlugin',
      version='0.1.0',
      packages=find_packages(exclude=['*.tests*']),
      install_requires=['blockdiag>=0.8.1'],
      entry_points = """
      [trac.plugins]
      tracblockdiag = tracblockdiag.plugin
      """
      )
