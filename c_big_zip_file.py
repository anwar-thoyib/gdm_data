#!/usr/bin/python
import zipfile
from io import BytesIO

#############################################################################
class big_zip_file:
  main_zip_filename      = ""
  main_zip_file_object   = object()
  main_zip_filename_list = []

  def __init__(self, filename_inp):
    self.main_zip_filename      = filename_inp                                   # BigZipFileName
    self.main_zip_file_object   = zipfile.ZipFile(self.main_zip_filename, "r")   # read sub achive dat file
    self.main_zip_filename_list = self.main_zip_file_object.namelist()

    self.main_dat_zip_filename_list = []
    self.main_log_zip_filename_list = []
    for zip_filename in self.main_zip_filename_list:
      if zip_filename.endswith('.dat.zip'):
        self.main_dat_zip_filename_list.append(zip_filename)
        continue

      if zip_filename.endswith('.log.zip'):
        self.main_log_zip_filename_list.append(zip_filename)
        continue

  def get_zip_content(self, filename_inp):
    zip_file_buffer  = BytesIO(self.main_zip_file_object.read(filename_inp))
    zip_file_extract = zipfile.ZipFile(zip_file_buffer)
    content = ""
    for filename in zip_file_extract.namelist():
      content += zip_file_extract.read(filename)

    return content
