from xlwt import ExcelFormulaParser, ExcelFormula
import sys

f = ExcelFormula.Formula(
""" -((1.80 + 2.898 * 1)/(1.80 + 2.898))*
AVERAGE((1.80 + 2.898 * 1)/(1.80 + 2.898); 
        (1.80 + 2.898 * 1)/(1.80 + 2.898); 
        (1.80 + 2.898 * 1)/(1.80 + 2.898)) + 
SIN(PI()/4)""")

#for t in f.rpn():
#    print "%15s %15s" % (ExcelFormulaParser.PtgNames[t[0]], t[1])
