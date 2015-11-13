==============
 Introduction
==============

At `Oscar`_, we wanted to address settings and configuration with a
system that would improve operability, solve the need to change values
deep in the code-base, and consume a variety of sources
(i.e. command-line arguments, environment variables, configuration
files). ``oscar.flag`` is not a module for creating user-friendly
command-line interfaces, but it is a module for faceting a large
code-base for configuration.

Goals
=====

- Allow any module-level constants and values to be configurable. Any
  constant value should be a flag, and there should be no penalty for
  doing so.

- Eliminate collisions and reduce clutter by providing
  namespaces. Each flag should be namespaced to its containing module.

- Move flags in code close to the places they are used. Avoid central
  "config" or "settings" modules. Flags should be consumed in code
  similar to module constants.

  .. code-block:: python
     :caption: :py:mod:`utils.aurora`

     ZK_ENSEMBLE = 'zookeeper-1:2181,zookeeper-2:2181,zookeeper-3:2181'
     # Becomes this.
     FLAGS.zk_ensemble = oscar.flag.String('zookeeper ensemble')

- Provide clarity from the outside (i.e. command-line). Where a
  value/flag is used in code should be in the flag name.
  
  .. code-block:: shell

     # We know immediately that this value is set to a flag that resides in utils.aurora
     $ ps u | grep 'zookeeper-1'
     ian  72838   0.0  0.0  2423356    240 s003  R+    6:31PM   0:00.00 python my_app.py --utils.aurora.zk_ensemble="zookeeper-1:2181"

- Allow flags to be set and read from anywhere.

  .. code-block:: python
     :caption: :py:mod:`test.utils.aurora`

     import utils.aurora

     # Run tests against local zookeeper.
     utils.aurora.FLAGS.zk_ensemble = 'localhost:2181'
  
Non-Goals
=========

- Provide a set of tools for creating command-line user
  interfaces. Services and applications are managed through automation
  (e.g. configuration management).

- Validate flag values. Flag values must marshall, but no further
  validation is provided.

.. _Oscar: https://hioscar.com
