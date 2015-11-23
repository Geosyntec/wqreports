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
        print("File found... Creating .pdf files\n")
        filefound = True
    else:
        print("Could not find the file, please try again... \n")


basedir = os.path.split(src)[0]
reports = wqreports.PdfReport(src)
reports.export_pdfs(output_path=basedir)

gc.collect()
print('\n')
