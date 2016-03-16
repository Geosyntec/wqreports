import sys
import os
import glob
import gc

import wqreports

msg = """
This script looks for a `.csv` file in a specified directory and produces
`.pdf` reports for each analyte in the `.csv` file.


Example:
--------
$ run.bat
What is the source file name of the `.csv` data?
    C:\My_Data\PDX_Phos.csv

End of documentation
--------------------
"""

print(msg)
filefound = False

while not filefound:
    src = input("What is the source file name of the `.csv` data?\n\t")
    print('\n')

    if os.path.exists(src):
        useROS = None
        useROSstr = input(
            'Do you want to use ROS to estimate non-detect values?\n'
            'All values must be greater than zero to use this feature.\n'
            'Input (y/n):\n\t')

        print('\n')

        while useROS is None:
            if useROSstr.strip().lower()[0] == 'y':
                useROS = True
            elif useROSstr.strip().lower()[0] == 'n':
                useROS = False
            else:
                print('ROS input not understood, please try again...')

        print("File found... Creating .pdf files\n")
        filefound = True
    else:
        print("Could not find the file, please try again... \n")


basedir = os.path.split(src)[0]

reports = wqreports.PdfReport(
    src, analytecol='parameter', rescol='value',
    qualcol='qualifier', unitcol='unit', locationcol='location',
    thersholdcol='threshold', useROS=useROS)

reports.export_pdfs(output_path=basedir)

gc.collect()
print('\n')

src = input("All PDF Generated. Please close DOS window.")
