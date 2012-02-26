import os
from setuptools import find_packages, setup

version = '0.2.1'
readme = os.path.join(os.path.dirname(__file__), 'README.rst')
long_description = open(readme).read()

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: System Administrators',
    'Programming Language :: Python',
    'License :: OSI Approved :: MIT License',
    'Framework :: Trac',
    'Environment :: Plugins',
]

setup(name='TracBlockdiag',
      version=version,
      description='Integrate blockdiag series into Trac wiki',
      long_description=long_description,
      classifiers=classifiers,
      keywords=['trac', 'macro', 'blockdiag'],
      author='Yoshihisa Tanaka',
      author_email='yt.hisa@gmail.com',
      license='MIT',
      url='https://github.com/yosisa/TracBlockdiag',
      install_requires=['blockdiag>=0.8.1'],
      extras_require={
          'full': ['seqdiag>=0.3.5', 'actdiag>=0.1.5', 'nwdiag>=0.2.4']
          },
      packages=find_packages(exclude=['*.tests*']),
      entry_points="""
      [trac.plugins]
      tracblockdiag = tracblockdiag.plugin
      """
)
