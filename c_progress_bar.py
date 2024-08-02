#!/usr/bin/python
import sys
import datetime

##############################################################################
class progress_bar:
  progress_bar_is_completed = False

  def __init__(self):
    self.log_zip_filename = ""
    self.flog         = object()

  def print_progress_bar(self, iteration, total, prefix = 'Progress:', suffix = 'Complete', decimals = 1, length = 50, fill = "#"):
    """
    Call in a loop to create terminal progress bar
    @params:
      iteration   - Required  : current iteration (Int)
      total       - Required  : total iterations (Int)
      prefix      - Optional  : prefix string (Str)
      suffix      - Optional  : suffix string (Str)
      decimals    - Optional  : positive number of decimals in percent complete (Int)
      length      - Optional  : character length of bar (Int)
      fill        - Optional  : bar fill character (Str)
    """
    if self.progress_bar_is_completed:
      self.progress_bar_is_completed = False
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write("\r" + prefix + " |" + bar + "| " + percent + " " + suffix + "\r")
    sys.stdout.flush()
#   print "\r%s |%s| %s%% %s" % (prefix, bar, percent, suffix), end = '\r'
    # Print New Line on Complete
    if iteration == total:
      sys.stdout.write("\n")
      self.progress_bar_is_completed = True

  def print_progress_bar_completed(self):
    if not self.progress_bar_is_completed: self.print_progress_bar(257, 257)

  def resume_log_file(self, filename_inp):
    self.flog = open(self.log_zip_filename, "a", 0)
    self.flog.write("\tSkipped!\n")
    self.flog.write("Resume File: " + filename_inp + " ... ")
    self.flog.close()

  def done_log_file(self):
    self.flog = open(self.log_zip_filename, "a", 0)
    self.flog.write("\tDone!\n")
    self.flog.close()

  def write_log_file(self, message_inp):
    self.flog = open(self.log_zip_filename, "a", 0)
    self.flog.write(message_inp)
    self.flog.close()

  def start_time_log_file(self, message_inp):
    self.flog = open(self.log_zip_filename, "a", 0)
    self.flog.write("\nSTART TIME: " + str(datetime.datetime.now()) + "\n")
    self.flog.write(message_inp + '\n')
    self.flog.close()

  def endTimeLogFile(self, filename_inp):
    self.flog = open(self.log_zip_filename, "a", 0)
    self.flog.write("Process completed!\n")
    if filename_inp:
        self.flog.write("Final result file: " + filename_inp + "\n")

    self.flog.write("END TIME: " + str(datetime.datetime.now()))
    self.flog.close()

