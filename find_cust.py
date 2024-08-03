#!/usr/bin/python
import os
import sys
import re
from c_dat_zip_file import dat_zip_file
from c_progress_bar import progress_bar

#############################################################################
class find_cust_from_zip_file(dat_zip_file, progress_bar):
  REGEX_LOG_CUSTOMER_ID = r'{CustomerId=(\w+)}\s+(\w+)'
  log_accomplished      = False                                 # TRUE if already cust found in LOG file
  log_file_counter      = 0                                     # LOG file have been opened

  def __init__(self, filename_inp):
    dat_zip_file.__init__(self, filename_inp)
    progress_bar.__init__(self)
    self.log_customer_id_to_be_checked = []                              # list of cust id to be search in current LOG file
    self.log_zip_filename                  = ""                              # current LOG file name
    self.log_customer_id_found         = False                           # TRUE if subs found in current LOG file

  def filename_log2dat(self, filename_inp):
    return re.sub('.log.zip', r'.dat.zip', filename_inp)

  def set_dat_zip_filename(self, dat_filename):
    self.dat_filename = (dat_filename if dat_filename else self.filename_log2dat(self.log_zip_filename))

  def show_log_bar(self, customer_id, customer_status):
    if self.display_log_bar_status:
      sys.stdout.write(" " * 80 + "\r")
      print(customer_id + "|" + customer_status + "|" + self.dat_filename)

  def find_customer_from_log_zip_file(self, zip_filename):
    self.log_zip_filename  = zip_filename
    self.set_dat_zip_filename(None)
    self.log_file_counter += 1
    self.log_sub_found     = False
    del self.dat_customer_id_to_be_checked[:]

# ORANGE LOOPING START: to get Line of content from LOG file ---------------->
    for log_line in self.get_zip_content(self.log_zip_filename).split("\n"):
      pline = re.search(self.REGEX_LOG_CUSTOMER_ID, log_line)
      if pline:
        log_customer_id     = pline.group(1)
        log_customer_status = pline.group(2)
        if log_customer_id in self.log_customer_id_to_be_checked:
          self.log_customer_id_found = True                         # cust found
          self.log_customer_id_to_be_checked.remove(log_customer_id)      # add founded cust id
          self.dat_customer_id_to_be_checked.append(log_customer_id)      # remove founded cust id
          self.show_log_bar(log_customer_id, log_customer_status)    # display cust summary that found
          self.append_parent_id_from_customer_id_to_be_checked(log_customer_id) # add Parent to be searched
          if not self.log_customer_id_to_be_checked: self.log_accomplished = True
# NO NEED GREEN LOOPING ENDED ------------------------------------------------------->

      if self.log_accomplished: break
# ORANGE LOOPING ENDED ------------------------------------------------------>

  def print_progress_bar_log(self):
    self.print_progress_bar(self.log_file_counter, 256)
    self.base_progress_bar = self.log_file_counter

  def find_customer_from_zip_file(self, zip_filename):
    self.find_customer_from_log_zip_file(zip_filename)
    if self.log_customer_id_found:
      self.set_dat_zip_filename(None)
      self.find_customer_from_dat_zip_file([])

  def find_customer_data(self, customer_id_to_be_checked=()):
    self.log_customer_id_to_be_checked = customer_id_to_be_checked
    if self.display_log_bar_status:
      self.print_progress_bar_log()

# RED LOOPING START: to get filename of LOG file from <ZipFileList[]> ------->
    for zip_filename in self.main_zip_filename_list:
#      uname = zip_filename.decode('gbk')
      if zip_filename.endswith('.log.zip'):
        if self.display_log_bar_status:
          self.print_progress_bar_log()

        self.find_customer_from_zip_file(zip_filename)
        if self.log_accomplished: break

    if self.display_log_bar_status:
      self.print_progress_bar_completed()
# RED LOOPING ENDED --------------------------------------------------------->

  def __del__(self):
    if self.display_log_bar_status:
      for customer_id in self.log_customer_id_to_be_checked: print(customer_id + "||")

    if self.write_customer_detail:
      if self.dat_subs_found: print("Detail subs: " + self.report_filename)
      else                  : print("Sorry, can not found the subs.\n")

    if self.display_log_bar_status:
      print(str(self.log_file_counter) + " log file(s) haved been searched")
      print(str(self.dat_file_counter) + " dat file(s) haved been searched")

  def get_customer_id_list_from_file(self, filename_inp):
    customer_id_list   = []
    finp = open(filename_inp)
    for line in finp:
      rline = re.search(r'^(\w+)$', line)
      if rline:
        customer_id_list.append(rline.group(1))

    finp.close()

    return customer_id_list

  def execute(self, input_value):
    customer_id_to_be_checked_list = []
    if os.path.exists(input_value):
      customer_id_to_be_checked_list = self.get_customer_id_list_from_file(input_value)
      output_file = 'result_'+ input_value
    else:
      customer_id_to_be_checked_list.append(input_value)
      output_file = 'subs_'+ input_value +'.txt'

    self.set_report_filename(output_file)
    self.find_customer_data(customer_id_to_be_checked_list)


##############################################################################
if __name__ == "__main__":
  source_file = ''
  input_value = ''

  if len(sys.argv) > 2:
    source_file = sys.argv[1]
    input_value = sys.argv[2]
  else:
    print('Error, need parameters: zip filename and customer id!')
    exit(0)

  myzipfile = find_cust_from_zip_file(source_file)
  myzipfile.set_display_log_bar_status(True)
  myzipfile.execute(input_value)
