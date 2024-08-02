#!/usr/bin/python
import re
from c_big_zip_file import big_zip_file


#############################################################################
class dat_zip_file(big_zip_file):
#Read:Customer (CustomerId, ServiceProviderId, billCycleId, billCycleIdAfterSwitch, billCycleSwitch, category, prefetchFilter, BillCycleHistory{BillCycleId, InvalidFrom}, IMSI, OperationalType, ParentCustomerId, vValidFrom, vInvalidFrom, BillingType, Classifications, HomeTimeZoneId, PackageAdminRole, TaxCategory, TaxJurisdiction, bCategory, bSeriesId, bValidFrom, bInvalidFrom, EventTimeOfLastRatedEvent, IsChronologyViolated, LastReratingID, ReratingHistory{ReratingId, ReratingTime});

  REGEX_DAT_CUSTOMER_ID    = '^Read:Customer\s+\(CustomerId'
  REGEX_PARENT_CUSTOMER_ID = 'ParentCustomerId'
  REGEX_WHITE_SPACE        = '^\s*$'
  dat_file_counter         = 0                                  # DAT file have been opened
  write_customer_detail    = False
  display_log_summary      = False

  def __init__(self, myfile):
    big_zip_file.__init__(self, myfile)
    self.dat_filename      = ""                                         # current DAT file name
    self.report_filename   = ""
    self.dat_subs_found    = False
    self.base_progress_bar = 0
    self.dat_progress_bar  = 0
    self.dat_customer_id_to_be_checked = []                             # list of cust id to be search in current DAT file
    self.dat_profile_detail            = []                             # All profile dump for 1 cust

  def open_big_zip_file(self, filename_inp):
    big_zip_file.__init__(self, filename_inp)

  def set_display_log_bar_status(self, status):
    self.display_log_bar_status = status

  def set_write_customer_detail(self, status):
    self.write_customer_detail = status

  def set_report_filename(self, filename_inp):
    self.write_customer_detail = (True if filename_inp else False)
    self.report_filename = filename_inp

  def print_dat_profile_detail(self):                             # its belongs to the same cust
    if self.write_customer_detail:
      if self.dat_profile_detail:                            # print all Dump Line <DatProfileDetail[]>
        fout = open(self.report_filename, "a+")        # to file <ReportFileName>
        for line in self.dat_profile_detail: fout.write(line + "\n")
        self.dat_profile_detail = []

  def get_parent_id(self, customer_id):
    len_customer_id = len(customer_id)
    if len_customer_id > 14:
      parent_customer_id = customer_id[:(len_customer_id - 6)]
      return parent_customer_id
    else:
      return None

  def append_parent_id_from_customer_id_to_be_checked(self, customer_id):
    parent_id = self.get_parent_id(customer_id)
    if parent_id: self.dat_customer_id_to_be_checked.append(parent_id)

  def remove_parent_id_from_customer_id_to_be_checked(self, customer_id):
    parent_id = self.get_parent_id(customer_id)
    if parent_id:
      if parent_id in self.dat_customer_id_to_be_checked: self.dat_customer_id_to_be_checked.remove(parent_id)

  def find_customer_from_dat_zip_file(self, customer_to_be_checked=()):
    if customer_to_be_checked: self.dat_customer_id_to_be_checked = customer_to_be_checked
    self.dat_subs_found    = False    # TRUE if subs found in current DAT file
    subs_matched           = False    # flag to inform that the Line Dump is belong to the same cust
    self.dat_file_counter += 1
    subs_profile_counter   = 0
    self.dat_progress_bar  = 0
    first_line_customer    = False

    self.dat_profile_detail = []
    if self.display_log_bar_status:
      self.print_progress_bar_dat()

#        print("-->" + str(self.dat_customer_id_to_be_checked) + "<--")

    for dat_line in self.get_zip_content(self.dat_filename).split("\n"):
      pline = re.search(self.REGEX_DAT_CUSTOMER_ID, dat_line)
      if pline: # if pattern match, then this is first Line Dump of NEW cust
        first_line_customer = True
        if subs_matched:               # if TRUE then print ALL Line Dump that belongs to the last cust
          self.print_dat_profile_detail()
          if not self.dat_customer_id_to_be_checked: break  # is there any cust left? if yes exit BLUE loop
          subs_matched = False       # we don't know wheter current cust is matched with <DatCustToBeChecked[]>
        else:
          self.dat_profile_detail = []

        self.dat_profile_detail.append(dat_line)
        continue

      if subs_matched:
        self.dat_profile_detail.append(dat_line)
        continue

      if first_line_customer:
        qline = re.search('CustomerId="(\w+)"', dat_line)
        if qline: # if pattern match, then this is first Line Dump of NEW cust
          first_line_customer = False
          dat_customer_id     = qline.group(1)
          if self.display_log_bar_status:
            subs_profile_counter += 1
            if subs_profile_counter > 1000:
              subs_profile_counter   = 1
              self.dat_progress_bar += 1
              self.print_progress_bar_dat()

          if dat_customer_id in self.dat_customer_id_to_be_checked:  # find <dat_cust_id> in <DatCustToBeChecked[]>
            self.dat_subs_found = True                # since current cust already found
            subs_matched        = True                # and this Dump Line belongs to cust
            self.dat_customer_id_to_be_checked.remove(dat_customer_id)
            rline = re.match(self.REGEX_PARENT_CUSTOMER_ID, dat_line)
            if not rline: self.remove_parent_id_from_customer_id_to_be_checked(dat_customer_id)

      if subs_matched:                                          # if this Dump Line belongs to cust
        rline = re.match(self.REGEX_WHITE_SPACE, dat_line)
        if not rline: self.dat_profile_detail.append(dat_line)

# Its at the end of Dump Line, check if its belong to cust
    if subs_matched:
      self.print_dat_profile_detail()                # then print all Dump Line to file ReportFileName

  def print_progress_bar_dat(self):
    self.print_progress_bar((self.base_progress_bar * 280) + self.dat_progress_bar, 257 * 280)

