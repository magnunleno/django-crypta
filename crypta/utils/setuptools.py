#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of Django-Crypta.
#
# Django-Crypta is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Django-Crypta is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Django-Crypta.  If not, see <http://www.gnu.org/licenses/>.

import glob
import os
import sys
from fnmatch import fnmatchcase

import pip
from setuptools import convert_path

REQUIREMENT_TEMPLATE = "./requirements/*.txt"
STANDARD_EXCLUDE = ["*.py", "*.pyc", "*~", ".*", "*.bak", "Makefile"]
STANDARD_EXCLUDE_DIRECTORIES = [
    ".*", "./build", "./dist", "EGG-INFO", "*.egg-info", "./example",
]


# Copied from paste/util/finddata.py
def find_package_data(where=".", package="", exclude=STANDARD_EXCLUDE,
                      exclude_directories=STANDARD_EXCLUDE_DIRECTORIES,
                      only_in_packages=True, show_ignored=False):
    """
    Return a dictionary suitable for use in ``package_data``
    in a distutils ``setup.py`` file.
    The dictionary looks like::
        {"package": [files]}
    Where ``files`` is a list of all the files in that package that
    don't match anything in ``exclude``.
    If ``only_in_packages`` is true, then top-level directories that
    are not packages won't be included (but directories under packages
    will).
    Directories matching any pattern in ``exclude_directories`` will
    be ignored; by default directories with leading ``.``, ``CVS``,
    and ``_darcs`` will be ignored.
    If ``show_ignored`` is true, then all the files that aren't
    included in package data are shown on stderr (for debugging
    purposes).
    Note patterns use wildcards, or can be exact paths (including
    leading ``./``), and all searching is case-insensitive.
    """

    out = {}
    stack = [(convert_path(where), "", package, only_in_packages)]
    while stack:
        where, prefix, package, only_in_packages = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern) or
                            fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print(
                                "Directory %s ignored by pattern %s"
                                % (fn, pattern), file=sys.stderr
                            )
                        break
                if bad_name:
                    continue
                if (os.path.isfile(os.path.join(fn, "__init__.py")) and not
                        prefix):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + "." + name
                    stack.append((fn, "", new_package, False))
                else:
                    stack.append((fn, prefix + name + "/", package,
                                  only_in_packages))
            elif package or not only_in_packages:
                # is a file
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern) or
                            fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print(
                                "Directory %s ignored by pattern %s"
                                "File %s ignored by pattern %s"
                                % (fn, pattern), file=sys.stderr
                            )
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix + name)
    return out


def get_requirements(environment):
    all_files = {
        os.path.splitext(os.path.basename(path))[0]: path
        for path in glob.glob(REQUIREMENT_TEMPLATE)
    }

    if environment not in all_files:
        raise ValueError(
            "The value '{}' is invalid, please choose one of the following: {}"
            .format(environment, ', '.join(all_files.keys()))
        )

    try:
        install_reqs = pip.req.parse_requirements(all_files[environment])
        requirements = [str(ir.req) for ir in install_reqs]
    except TypeError:
        install_reqs = pip.req.parse_requirements(
            all_files[environment],
            session=pip.download.PipSession(),
        )
        requirements = [str(ir.req) for ir in install_reqs]

    return requirements
