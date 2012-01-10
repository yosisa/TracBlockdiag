Introduction
============
TracBlockdiag is a trac plugin that integrate blockdiag series into wiki pages.
It's provide wiki macros for blockdiag, seqdiag, actdiag, nwdiag and rackdiag.

This software is available under the MIT license.

Features
========
TracBlockdiag has several features.

- Support almost blockdiag features (fontmap is not supported).
- Support PNG/SVG output (SVG support is Trac 0.12 only).
- Fastest wiki rendering.
- Multi thread/process safe.
- Check installed blockdiag series and provide only supported macros.
- Don't create temporary file.

Requirements
============
- Python >= 2.5
- Trac >= 0.11

If you need all features, you must use Trac 0.12 or later.

Install
=======
First, clone the repository. ::

  $ git clone https://github.com/yosisa/TracBlockdiag.git
  $ cd TracBlockdiag

Then, you can install globally ::

  # python setup.py install

or install to a specific Trac environment. ::

  $ python setup.py bdist_egg
  $ cp dist/*.egg /path/to/tracenv/plugins

Moreover, you must install blockdiag series which you want to integrate.
For example, below command will install all blockdiag series
(rackdiag is currently included in nwdiag). ::

  $ pip install blockdiag seqdiag actdiag nwdiag

Optionally, you can use blockdiag plugins.
If you need a plugin, you simply install it.
For example, below command will install new shapes. ::

  $ pip install blockdiagcontrib-cisco

Usage
=====
If you are not familiar with blockdiag, you should read the `blockdiag documentation <http://blockdiag.com/en/blockdiag/>`_ first.

for Trac 0.12 or later
----------------------
Macro synopsis like this::

  {{{#!(block|seq|act|nw|rack)diag [type=(png|svg)] [IMG_TAG_ATTR=VALUE ...]
  *DIAG_SOURCE_TEXT
  }}}

You can write blockdiag source text as a wiki macro like below. ::

  {{{#!blockdiag
  {
    A -> B -> C;
         B -> D;
  }
  }}}

You can specify output format and width. ::

  {{{#!blockdiag type=svg width=800px
  {
    A -> B -> C;
         B -> D;
  }
  }}}

for Trac 0.11
-------------
Macro synopsis like this::

  {{{
  #!(block|seq|act|nw|rack)diag
  *DIAG_SOURCE_TEXT
  }}}

**In Trac 0.11, macro arguments is not supported.
So, all diagrams is generated with PNG format.**

You can write blockdiag source text as a wiki macro like below. ::

  {{{
  #!blockdiag
  {
    A -> B -> C;
         B -> D;
  }
  }}}

Options
=======
TracBlockdiag has several configuration parameters.
These parameters are specify in `[tracblockdiag]` section of the `trac.ini` config file.
These parameters are defined as follows.

=========== ======= ===========================================================================
name        default description
=========== ======= ===========================================================================
font        (auto)  Path to font file which is used in PNG generation.
cachetime   300     Time in seconds which the plugin caches a generated diagram in.
gc_interval 100     The number of diagram generation. Unused cache is cleared every this count.
=========== ======= ===========================================================================
