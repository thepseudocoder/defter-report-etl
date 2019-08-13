import xlrd
import csv
import io

## ETL process list
# The list of functions to be applied each line. Can be modified.

processList = [illegalLine, addAccountName, absAmount, deleteSumCol]


## ETL processes ##
# Each process takes a csv line and returns a processes line to be
# appended to the result file.

# If a processed line's result is Null, processes return 0.

# determine if the line is empty or a seperator line
def illegalLine(line):
        pass

# adds account name to the first column
def addAccountName(line):
        pass

# takes the absolute value of amount column 
def absAmount(line):
        pass

# deletes the last column (total sum)
def deleteSumCol(line):
        pass

# Take a workbook and return csv string
def convertCSV(workbookpath):

    output = io.StringIO()

    with xlrd.open_workbook(workbookpath) as wb:
        sh = wb.sheet_by_index(0)

        c = csv.writer(output)
        for r in range(sh.nrows):
            c.writerow(sh.row_values(r))

    return output.getvalue()

