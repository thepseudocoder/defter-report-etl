import xlrd
import csv
import io
import sys
import os
import datetime
from os import walk


#### Some variables

# The list of categories to be discarded from final 
DeleteCategories = ["TRANSFER"]

# First # of rows to be omitted
OmitFirstRows = 3

#### ETL processes ####

# Each process takes a csv row and returns a processed row to be
# appended to the result file.

# the first arg is the row to be processed
# the secong arg is row number
# the third arg is account name

# If a row should be omitted, processes return 0 instead.

# determine if the row is empty or a seperator row
def omitRow(*args):
	row = args[0]
	row_num = args[1]

	cell_list = row.split(",")
	empty_cell_count = cell_list.count("")

	# first 3 rows of the file are automatically omitted
	if row_num < OmitFirstRows:
		return 0
	# if there are less than 6 cells, then its probably an empty row
	elif len(cell_list) < 6:
		return 0
	# if there are more than 2 empty cells, then its probably a seperator row
	elif empty_cell_count >= 2:
		return 0
	else:
		return row

# adds account name to the first column
def addAccountName(*args):
	row = args[0]
	account_name = args[2]

	row = account_name + "," + row

	return row

# takes the absolute value of amount column
# note: changing the ProcessList may broke this function
# since it exclusively takes the absoulte value of 5th cell
def absAmount(*args):
	row = args[0]
	cell_list = row.split(",")

	# 5th cell contains the amount
	cell_list[4] = float(cell_list[4])
	cell_list[4] = abs(cell_list[4])

	row = ','.join(map(str,cell_list))

	return row

# deletes the last column (total sum)
def deleteSumCol(*args):
	row = args[0]
	cell_list = row.split(",")

	cell_list.pop()

	row = ','.join(map(str,cell_list))

	return row

# delete the row if the category is listed in deleteCategories
def deleteIfUnwatedCategory(*args):
	row = args[0]
	cell_list = row.split(",")
	
	for item in cell_list:
		if item in DeleteCategories:
			return 0

	return row

# convert date integers to dates
# note: changing the ProcessList may broke this function
# since it exclusively converts the value of 0th cell
def convertDates(*args):
	row = args[0]
	cell_list = row.split(",")

	datefloat = float(cell_list[0])
	adjusteddate = (datefloat - 25569) * 86400.0

	resultdate = datetime.datetime.utcfromtimestamp(adjusteddate)
	cell_list[0] = resultdate.strftime('%Y-%m-%d')

	row = ','.join(map(str,cell_list))
	
	return row

#######################

# Take a workbook and return csv string
def convertCSV(workbookpath):

	output = io.StringIO()

	with xlrd.open_workbook(workbookpath) as wb:
		sh = wb.sheet_by_index(0)

		c = csv.writer(output)
		for r in range(sh.nrows):
			c.writerow(sh.row_values(r))

	return output.getvalue()

# Get account name from the file path
def deriveAccountName(filePath):
	return filePath.split(".")[0].split("\\")[-1]

## ETL process list
# The list of functions to be applied each row. Can be modified.
ProcessList = [
	omitRow,
	absAmount,
	convertDates, 
	deleteSumCol,
	addAccountName
	]

if __name__ == '__main__':
	
	path = sys.argv[1]
	filelist = []

	# get only xlsx files
	for (dirpath, dirnames, filenames) in walk(path):
		for a_file in filenames:
			if ".xlsx" in a_file:
				filelist.append(os.path.join(dirpath, a_file))
	
	# extra check for temporary/hidden files
	for item in filelist:
		if "~$" in item or item.split("\\")[-1][0] == ".":
			filelist.remove(item)

	resultCSV = ""

	for each_file in filelist:
		output = convertCSV(each_file)
		rows = output.split("\n")
		
		# account name is derived from the filename
		accountname = deriveAccountName(each_file)
    
		print("Processing account: " + accountname)

		rowNum = 0

		for row in rows:
			processedRow = row

			for func in ProcessList:
				result = func(processedRow, rowNum, accountname)
				
				if result == 0:
					processedRow = 0
					break
				else:
					processedRow = result
			
			rowNum+=1

			if processedRow == 0:
				continue
			else:
				resultCSV += processedRow + "\n"
	
	with open('result.csv', 'w', newline="", encoding="utf-8") as f:
		f.write(resultCSV)
	