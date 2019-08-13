import xlrd
import csv
import io

# Take a workbook and return csv string
def convertCSV(workbookpath):

    output = io.StringIO()

    with xlrd.open_workbook(workbookpath) as wb:
        sh = wb.sheet_by_index(0)

        c = csv.writer(output)
        for r in range(sh.nrows):
            c.writerow(sh.row_values(r))

    return output.getvalue()
