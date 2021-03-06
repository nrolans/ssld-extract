#!/usr/bin/env python
#
# { ssld-extract.py }
# Copyright (C) 2012 Alex Kozadaev [akozadaev at yahoo com]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.#

import sys, getopt

conf = { 'ports': set(), 'conns': set() }
version = '0.12f' # python < 2.7 compatible

# =======================================================================
def parse(infile):
    needclose = False
    inside = False

    if infile == '-':
        fh = sys.stdin
    else:
        try:
            fh = open(infile, 'r')
        except IOError:
            die("cannot open file %s" % infile)
        needclose = True

    # main logic here
    for line in fh: 
        if line[:3] == 'New':
            try:
                port = line[ line.index('(')+1 : line.index(')') ]
                conn = line[ line.index('#')+1 : line.index(':') ]
            except ValueError:
                print >> sys.stderr, "error: cannot parse connection record"
                next

            if ((conn.isdigit() and int(conn) in conf['conns']) or 
                (port.isdigit() and int(port) in conf['ports'])):
                print line,
                conf['conns'].add(int(conn))
                inside = True
        elif line[0].isspace():
            if inside: print line,
        elif line[0].isdigit():
            try:
                val = line[: line.index(' ') ]
            except ValueError:
                inside = False
                next

            if val.isdigit() and (int(val) in conf['conns']):
                print line,
                inside = True
            else:
                inside = False

    if needclose:
        fh.close()

# =======================================================================
def readargs():
    if (len(sys.argv) == 1): usage()

    sys.argv.pop(0)
    opts, infile = getopt.getopt(sys.argv, "hp:n:")

    for k,v in opts:
        if k == '-p':
            readvalues(v, 'ports')
        elif k == '-n':
           readvalues(v, 'conns')
        elif k == '-h':
           usage()
           exit()
    if len(infile) == 0:
        die("no source given")

    return infile[0]

# =======================================================================
def readvalues(values, cfgset):
    for p in values.split(','):
        if (p.isdigit()):
            conf[cfgset].add(int(p))
        else:
            die("Invalid format %s" % p)

# =======================================================================
def usage():
    print """ssld-extract (python-edition) v%s Alex Kozadaev(C)

    ssld-extact [-n x,y | -p n,m] [ssldump filename | - to read from pipe]

    Extract one or more connections from a SSL dump file.

        Usage:
            -n    comma separated list of connections (no spaces allowed)
            -p    comma separated list of client ports (no spaces allowed)
            -h    this text

    Firstly python version was as twise as slower then the perl version.
    But after refactoring I managed  to make it even faster. I tested both
    versions by parsing 173 megabyte ssldump file and python was ~0.7sec
    faster this time.\n """ % version
    exit(0)

# =======================================================================
def die(msg):
    print >> sys.stderr, "error: %s" % msg
    exit(1)

# ==[ main ]=============================================================
if __name__ == '__main__':
    try:
        parse(readargs())
    except KeyboardInterrupt:
        print >> sys.stderr, "\ninterrupted..."
        exit(1)
    except IOError, e:
        exit(0) # SIGPIPE handling

# vim: set tabstop=4 softtabstop=4 shiftwidth=4 smarttab ai expandtab
