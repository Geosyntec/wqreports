import sys
import os
import glob
import gc

# Temporary until I know how Paul plans to install wqreports
try:
    from wqreports import PdfReport
except ImportError as e:
    sys.path.append(r'Data_Summary\nsqdpdfs')
    from wqreports import PdfReport

msg = """
This script looks for all `.csv` files in a specified directory and produces
`.pdf` reports for each analyte in each of the `.csv` files.

This script creates sub-folders in the destination directory using the names of
the `.csv` files. If the destination folder does not exist the script will
attempt to create it.

Example:
--------
$ run.bat
What is the source directory of the `.csv` data?
    C:\My_Data

What is the destination directory for the `.pdf` files?
    C:\My_pdfs

End of documentation
--------------------
"""

print(msg)

src = input("What is the source directory of the `.csv` data?\n\t")
print('\n')
outpath = input("What is the destination directory for the `.pdf` files?\n\t")
print('\n')

# I think they should feed .csv files, as that is the format pandas is expecting
# not .txt.
srcpath = glob.glob(os.path.join(src, '*.csv'))

for s in srcpath:
    acrp = PdfReport(s)

    # If they give multiple data files with the same analytes we don't want
    # to overwrite anything, so we will make folders with the data file names
    suboutpath = os.path.join(outpath, s.rpartition('\\')[-1].split('.')[0])
    acrp.export_pdfs(suboutpath)

    # Here to reduce weird css error
    del acrp
    gc.collect()

print('\n')
