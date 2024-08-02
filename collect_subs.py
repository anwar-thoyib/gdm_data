#!/usr/bin/python
import sys
import re
import zipfile
from io import BytesIO
from collections import Counter
from c_dat_zip_file import dat_zip_file
from c_progress_bar import progress_bar

#############################################################################
class collect_subs_from_dat_zip_file(dat_zip_file, progress_bar):

  def __init__(self, myfile):
    dat_zip_file.__init__(self, myfile)
    progress_bar.__init__(self)
    self.Customer_counter        = 0
    self.ROP_s_OfferId_Counter   = Counter()
    self.RPP_s_PackageId_Counter = Counter()
    self.AccessKey_Key_Counter   = Counter()
    self.Multiple_ROP_dict       = dict()
    self.CustomerId      = ''
    self.ROP_CustomerId  = ''
    self.RPP_CustomerId  = ''
    self.report_line     = ''
    self.log_status      = ''
    self.flog = object()

  def collect(self, log_status=True):
    self.log_status = log_status
    if self.log_status:
      print('output filename: output.log')

    curr_CustomerId = ''
    last_CustomerId = ''
    last_ROP_CustomerId = ''
    if self.log_status:
      self.flog = open('output.log', 'w')

    for main_dat_zip_filename in self.main_dat_zip_filename_list:
      main_dat_zip_file_buffer  = BytesIO(self.main_zip_file_object.read(main_dat_zip_filename))
      main_dat_zip_file_extract = zipfile.ZipFile(main_dat_zip_file_buffer)
      dat_zip_filename_list     = main_dat_zip_file_extract.namelist()

      if self.display_log_bar_status:
        self.print_progress_bar(self.dat_file_counter, 256)
        self.base_progress_bar = self.dat_file_counter

      for dat_zip_filename in dat_zip_filename_list:
        dat_content = main_dat_zip_file_extract.read(dat_zip_filename)
        self.dat_file_counter += 1

        for line in dat_content.decode('utf-8').split('\n'):
          rRPP = re.search('^Read:RPP \(CustomerId="(\w+)", s_PackageId="(\w+)"', line)
          if rRPP:
  #         self.RPP_CustomerId = rRPP.group(1)
            s_PackageId    = rRPP.group(2)
            self.RPP_s_PackageId_Counter[s_PackageId] += 1

            if self.log_status:
              self.report_line += ', s_PackageId="'+ s_PackageId +'"'

            continue

          rROP = re.search('^Read:ROP \(CustomerId="(\w+)"', line)
          if rROP:
            self.ROP_CustomerId = rROP.group(1)
            if self.ROP_CustomerId == last_ROP_CustomerId:
              if self.ROP_CustomerId in self.Multiple_ROP_dict.keys():
                self.Multiple_ROP_dict[self.CustomerId]['counter'] += 1
              else:
                self.Multiple_ROP_dict[self.CustomerId] = dict()
                self.Multiple_ROP_dict[self.CustomerId]['CustomerId'] = self.CustomerId
                self.Multiple_ROP_dict[self.CustomerId]['filename']   = dat_zip_filename
                self.Multiple_ROP_dict[self.CustomerId]['counter']    = 2

            rROP1 = re.search('^Read:ROP \(CustomerId="\w+", s_OfferId="(\w+)"', line)
            if rROP1:
              s_OfferId                         = rROP1.group(1)
              self.ROP_s_OfferId_Counter[s_OfferId] += 1

            last_ROP_CustomerId = self.ROP_CustomerId

            if self.log_status:
              self.report_line += ', s_OfferId="'+ s_OfferId +'"'

            continue

          rCustomer = re.search('^Read:Customer \(CustomerId="(\w+)"', line)
          if rCustomer:
            if self.log_status:
              if self.report_line:
                self.flog.write(self.report_line +'\n')

              self.report_line = ''

            last_CustomerId = self.CustomerId
            self.CustomerId = rCustomer.group(1)
            curr_CustomerId = self.CustomerId
            self.Customer_counter += 1

            if self.log_status:
              self.report_line += 'CustomerId="'+ self.CustomerId +'"'

            continue

          rServiceAccessKey = re.search('^Read:ServiceAccessKey \(Key="(\w+)", OwningCustomerId="(\w+)"', line)
          if rServiceAccessKey:
            OwningCustomerId = rServiceAccessKey.group(2)
            if self.log_status:
              Key = rServiceAccessKey.group(1)
              if OwningCustomerId == self.CustomerId:
                self.report_line += ', Key="'+ Key +'"'

            self.AccessKey_Key_Counter[OwningCustomerId] += 1

            continue

    if self.display_log_bar_status:
      self.print_progress_bar_completed()

    if self.log_status:
      self.flog.close()

  def report(self):
    print('-----------------------------')
    fout = open('summary.txt', 'w')
    msg = 'Total Customer: '+ str(self.Customer_counter)
    print(msg)
    fout.write(msg +'\n')

    total = 0
    for OwningCustomerId in self.AccessKey_Key_Counter.keys():
      total += self.AccessKey_Key_Counter[OwningCustomerId]
    msg = 'Total MSISDN: '+ str(total)
    print(msg)
    fout.write(msg +'\n')

    msg = 'Multiple ROP: '
    print(msg)
    fout.write(msg +'\n')
    for ROP_CustomerId in self.Multiple_ROP_dict.keys():
      msg  = '  '
      msg += self.Multiple_ROP_dict[ROP_CustomerId]['filename'] +': '
      msg += ROP_CustomerId
      msg += ' ('+ str(self.Multiple_ROP_dict[ROP_CustomerId]['counter']) +')'
      print(msg)
      fout.write(msg +'\n')

    msg = 'Total s_OfferId'
    print(msg)
    fout.write(msg +'\n')
    for s_OfferId, value in sorted(self.ROP_s_OfferId_Counter.items(), key=lambda item:item[1], reverse=True):
      msg = '  "'+ s_OfferId +'": '+ str(value)
      print(msg)
      fout.write(msg +'\n')

    fout.close()

    print('-----------------------------')
    print('summary filename: summary.txt')


##############################################################################
if __name__ == "__main__":
  source_file = ''
  log_status  = True

  if len(sys.argv) > 1:
    source_file = sys.argv[1]
    if len(sys.argv) > 2:
      if sys.argv[2].lower() == 'no_log':
        log_status = False
  else:
    print('Error: need parameter zip filename!')
    exit(0)

  myzipfile = collect_subs_from_dat_zip_file(source_file)
  myzipfile.set_display_log_bar_status(True)
  myzipfile.collect(log_status)
  myzipfile.report()

