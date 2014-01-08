# -*- coding: cp1252 -*-

##
# Module/script example of the xlrd API for extracting information
# about named references, named constants, etc.
#
# <p>Copyright © 2006 Stephen John Machin, Lingfo Pty Ltd</p>
# <p>This module is part of the xlrd package, which is released under a BSD-style licence.</p>
##
from __future__ import print_function

import xlrd
import sys
import glob

def scope_as_string(book, scope):
    if 0 <= scope < book.nsheets:
        return "sheet #%d (%r)" % (scope, book.sheet_names()[scope])
    if scope == -1:
        return "Global"
    if scope == -2:
        return "Macro/VBA"
    return "Unknown scope value (%r)" % scope

def do_scope_query(book, scope_strg, show_contents=0, f=sys.stdout):
    try:
        qscope = int(scope_strg)
    except ValueError:
        if scope_strg == "*":
            qscope = None # means "all'
        else:
            # so assume it's a sheet name ...
            qscope = book.sheet_names().index(scope_strg)
            print("%r => %d" % (scope_strg, qscope), file=f)
    for nobj in book.name_obj_list:
        if qscope is None or nobj.scope == qscope:
            show_name_object(book, nobj, show_contents, f)

def show_name_details(book, name, show_contents=0, f=sys.stdout):
    """
    book -- Book object obtained from xlrd.open_workbook().
    name -- The name that's being investigated.
    show_contents -- 0: Don't; 1: Non-empty cells only; 2: All cells
    f -- Open output file handle.
    """
    name_lcase = name.lower() # Excel names are case-insensitive.
    nobj_list = book.name_map.get(name_lcase)
    if not nobj_list:
        print("%r: unknown name" % name, file=f)
        return
    for nobj in nobj_list:
        show_name_object(book, nobj, show_contents, f)

def show_name_details_in_scope(
    book, name, scope_strg, show_contents=0, f=sys.stdout,
    ):
    try:
        scope = int(scope_strg)
    except ValueError:
        # so assume it's a sheet name ...
        scope = book.sheet_names().index(scope_strg)
        print("%r => %d" % (scope_strg, scope), file=f)
    name_lcase = name.lower() # Excel names are case-insensitive.
    while 1:
        nobj = book.name_and_scope_map.get((name_lcase, scope))
        if nobj:
            break
        print("Name %r not found in scope %d" % (name, scope), file=f)
        if scope == -1:
            return
        scope = -1 # Try again with global scope
    print("Name %r found in scope %d" % (name, scope), file=f)
    show_name_object(book, nobj, show_contents, f)

def showable_cell_value(celltype, cellvalue, datemode):
    if celltype == xlrd.XL_CELL_DATE:
        try:
            showval = xlrd.xldate_as_tuple(cellvalue, datemode)
        except xlrd.XLDateError:
            e1, e2 = sys.exc_info()[:2]
            showval = "%s:%s" % (e1.__name__, e2)
    elif celltype == xlrd.XL_CELL_ERROR:
        showval = xlrd.error_text_from_code.get(
            cellvalue, '<Unknown error code 0x%02x>' % cellvalue)
    else:
        showval = cellvalue
    return showval

def show_name_object(book, nobj, show_contents=0, f=sys.stdout):
    print("\nName: %r, scope: %r (%s)" \
        % (nobj.name, nobj.scope, scope_as_string(book, nobj.scope)), file=f)
    res = nobj.result
    print("Formula eval result: %r" % res, file=f)
    if res is None:
        return
    # result should be an instance of the Operand class
    kind = res.kind
    value = res.value
    if kind >= 0:
        # A scalar, or unknown ... you've seen all there is to see.
        pass
    elif kind == xlrd.oREL:
        # A list of Ref3D objects representing *relative* ranges
        for i in range(len(value)):
            ref3d = value[i]
            print("Range %d: %r ==> %s"% (i, ref3d.coords, xlrd.rangename3drel(book, ref3d)), file=f)
    elif kind == xlrd.oREF:
        # A list of Ref3D objects
        for i in range(len(value)):
            ref3d = value[i]
            print("Range %d: %r ==> %s"% (i, ref3d.coords, xlrd.rangename3d(book, ref3d)), file=f)
            if not show_contents:
                continue
            datemode = book.datemode
            for shx in range(ref3d.shtxlo, ref3d.shtxhi):
                sh = book.sheet_by_index(shx)
                print("   Sheet #%d (%s)" % (shx, sh.name), file=f)
                rowlim = min(ref3d.rowxhi, sh.nrows)
                collim = min(ref3d.colxhi, sh.ncols)
                for rowx in range(ref3d.rowxlo, rowlim):
                    for colx in range(ref3d.colxlo, collim):
                        cty = sh.cell_type(rowx, colx)
                        if cty == xlrd.XL_CELL_EMPTY and show_contents == 1:
                            continue
                        cval = sh.cell_value(rowx, colx)
                        sval = showable_cell_value(cty, cval, datemode)
                        print("      (%3d,%3d) %-5s: %r" \
                            % (rowx, colx, xlrd.cellname(rowx, colx), sval), file=f)

if __name__ == "__main__":
    def usage():
        text = """
usage: xlrdnameAIPdemo.py glob_pattern name scope show_contents

where:
    "glob_pattern" designates a set of files
    "name" is a name or '*' (all names)
    "scope" is -1 (global) or a sheet number
        or a sheet name or * (all scopes)
    "show_contents" is one of 0 (no show),
       1 (only non-empty cells), or 2 (all cells)

Examples (script name and glob_pattern arg omitted for brevity)
    [Searching through book.name_obj_list]
    * * 0 lists all names
    * * 1 lists all names, showing referenced non-empty cells
    * 1 0 lists all names local to the 2nd sheet
    * Northern 0 lists all names local to the 'Northern' sheet
    * -1 0 lists all names with global scope
    [Initial direct access through book.name_map]
    Sales * 0 lists all occurrences of "Sales" in any scope
    [Direct access through book.name_and_scope_map]
    Revenue -1 0 checks if "Revenue" exists in global scope

"""
        sys.stdout.write(text)
    
    if len(sys.argv) != 5:
        usage()
        sys.exit(0)
    arg_pattern = sys.argv[1] # glob pattern e.g. "foo*.xls"
    arg_name = sys.argv[2]    # see below
    arg_scope = sys.argv[3]   # see below
    arg_show_contents = int(sys.argv[4]) # 0: no show, 1: only non-empty cells,
                                         # 2: all cells
    for fname in glob.glob(arg_pattern):
        book = xlrd.open_workbook(fname)
        if arg_name == "*":
            # Examine book.name_obj_list to find all names
            # in a given scope ("*" => all scopes)
            do_scope_query(book, arg_scope, arg_show_contents)
        elif arg_scope == "*":
            # Using book.name_map to find all usage of a name.
            show_name_details(book, arg_name, arg_show_contents)
        else:
            # Using book.name_and_scope_map to find which if any instances
            # of a name are visible in the given scope, which can be supplied
            # as -1 (global) or a sheet number or a sheet name.
            show_name_details_in_scope(book, arg_name, arg_scope, arg_show_contents)
