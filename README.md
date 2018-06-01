Fractus
=======
[![Build Status](https://travis-ci.com/gtmanfred/fractus.svg?branch=develop)](https://travis-ci.com/gtmanfred/fractus)

The goal of Fractus is to move cloud execution modules and states out of salt
and into a new project so that they can be iterated on and released more
quickly.

This project can be installed with salt, and the modules here will override the
modules provided by salt.

The following is information about using this library on it's own.

Config
------

Default: ~/.config/fractus/config.yml

Example
-------

    import fractus.loader
    import fractus.config
    opts = fractus.config.fractus_config()
    mods = fractus.loader.cloudmodules(opts)
    print(mods['boto_ec2.find_instances']())
