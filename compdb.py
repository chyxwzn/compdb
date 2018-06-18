#
#   compiledb-generator: Tool for generating LLVM Compilation Database
#   files for make-based build systems.
#
#   Copyright (c) 2017 Nick Diego Yamane <nick.diego@gmail.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ex: ts=2 sw=4 et filetype=python


import click
import os
import sys
import json

from parser import parse_build_log, Error

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def generate_json_compdb(instream, proj_dir, extra_flags, verbose=False):
    if not os.path.isdir(proj_dir):
        raise Error("Project dir '{}' does not exists!".format(proj_dir))

    print("## Processing build commands from {}".format(instream.name))
    result = parse_build_log(instream, os.path.abspath(proj_dir), extra_flags, verbose)
    return result


def write_json_compdb(compdb, outstream, verbose=False,
                      force=False, pretty_output=True):
    print("## Writing compilation database with {} entries to {}".format(
        len(compdb), outstream.name))

    json.dump(compdb, outstream, indent=pretty_output)
    outstream.write(os.linesep)

class Options(object):
    """ Simple data class used to store command line options
    shared by all compiledb subcommands"""

    def __init__(self, infile, outfile, verbose):
        self.infile = infile
        self.outfile = outfile
        self.verbose = verbose


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-p', '--parse', 'infile', type=click.File('r'),
              help='Build log file to parse compilation commands from.' +
              '(Default: stdin)', required=False, default=sys.stdin)
@click.option('-o', '--output', 'outfile', type=click.File('w'),
              help="Output file path (Default: std output)",
              required=False, default='compile_commands.json')
@click.option('-d', '--build-dir', 'build_dir', type=click.Path(),
              help="Path to be used as initial build dir", default=os.getcwd())
@click.option('-e', '--extra-flags', 'extra_flags',
              help="extra flags to be added, joined with comma", default="")
@click.option('-v', '--verbose', is_flag=True, default=False,
              help='Print verbose messages.')
@click.pass_context
def compdb(ctx, infile, outfile, build_dir, extra_flags, verbose):
    """Clang's Compilation Database generator for make-based build systems.
       When no subcommand is used it will parse build log/commands and generates
       its corresponding Compilation database."""
    assert not sys.platform.startswith("win32")
    try:
        r = generate_json_compdb(infile, build_dir, extra_flags.split(','), verbose=verbose)
        write_json_compdb(r.compdb, outfile, verbose=verbose)
        print("## Done.")
        sys.exit(0)
    except Error as e:
        print(str(e))
        sys.exit(1)


if(__name__ == "__main__"):
    compdb()
