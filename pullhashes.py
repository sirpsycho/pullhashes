#!/usr/bin/python

import os
import sys
import subprocess
import datetime

# Check if there are the right number of arguments
if not len(sys.argv) == 3:
	print "\033[91m[!] Use format 'pullhashes.py <ntds.dit file> <SYSTEM file>'\033[0m"
	sys.exit()

# Set variables
ntdsfile = sys.argv[1]
systemfile = sys.argv[2]
exportercomp = "libesedb.tar.gz"
exporter = "resources/libesedb-20151213/esedbtools/esedbexport"
extractor = "resources/ntdsxtract/dsusers.py"
cwd = os.getcwd()

# Make sure all files exist and are accessible
def checkfiles(ntdsfile, systemfile, exporter, extractor):
	invalidfiles = False
	# If the compressed libesedb file exists, assume it is uninstalled and prompt to install
	if os.path.isfile("resources/%s" % exportercomp):
		if yesno("First run detected. Install libesedb?"):
			print "\033[92m[*] Installing libesedb...\033[0m"
			try:
				subprocess.Popen("cd resources && tar -xzf %s && cd libesedb-20151213 && ./configure && make && make install && cd .. && rm %s && cd %s" % (exportercomp, exportercomp, cwd), shell=True).wait()
			except:
				print "\033[91m[!] Install failed. Exiting...\033[0m"
				sys.exit()
			print "\033[92m[*] Installation complete!\033[0m"
		else:
			sys.exit()
	# Make sure the exporter program file exists in the decompressed directory
	if not os.path.isfile(exporter):
		print "\033[91m[!] Cannot find file '%s' (run pullhashes.py from local directory)\033[0m" % exporter
		invalidfiles = True
	else:
		# Make sure the exporter program runs properly
		proc = subprocess.Popen(("%s -h" % exporter).split(" "), stdout=subprocess.PIPE)
		tmp = proc.stdout.read()
		if not "Usage" in tmp:
			print "\033[91m[!] Error running '%s'\033[0m" % exporter
			invalidfiles = True
	if not os.path.isfile(extractor):
		print "\033[91m[!] Cannot find file '%s' (run pullhashes.py from local directory)\033[0m" % extractor
		invalidfiles = True
	if not os.path.isfile(ntdsfile):
		print "\033[91m[!] Cannot find file '%s'\033[0m" % ntdsfile
		invalidfiles = True
	if not os.path.isfile(systemfile):
		print "\033[91m[!] Cannot find file '%s'\033[0m" % systemfile
		invalidfiles = True
	if invalidfiles:
		sys.exit()
	else:
		if not yesno("Files verified. Extract hashes now?"):
			sys.exit()

# Use esedbexport command to export hashes
def hash_export(exporter, ntdsfile):
	print "\033[92m[*] Exporting hashes with esedbexport... This may take a while for ntds.dit files with many users\033[0m"
	subprocess.Popen("rm -rf HASHTEMP; mkdir HASHTEMP", shell=True).wait()
	subprocess.Popen("%s -t HASHTEMP/ntds %s" % (exporter, ntdsfile), shell=True).wait()

# Use dsusers command to extract hashes
def hash_extract(extractor, systemfile):
	print "\033[92m[*] Extracting hashes with dsusers and dumping user info to userlist.txt...\033[0m"
	subprocess.Popen("%s HASHTEMP/ntds.export/datatable.3 HASHTEMP/ntds.export/link_table.5 HASHTEMP --passwordhashes --lmoutfile LM.out --ntoutfile NT.out --pwdformat john --syshive %s > userlist.txt" % (extractor, systemfile), shell=True).wait()

# Remove extra files and temp directory
def cleanup():
	dirnum = 1
	date = datetime.date.today()
	if os.path.isdir("HASHTEMP"):
		print "\033[92m[*] Cleaning up...\033[0m"
		if not os.path.isdir("output"):
			subprocess.Popen("mkdir output", shell=True).wait()
		for directory in os.listdir("output"):
			if os.path.isdir("output/%s" % directory):
				dirnum += 1
		subprocess.Popen("mkdir output/%s_%s" % (dirnum, date), shell=True).wait()
		subprocess.Popen("cp HASHTEMP/LM.out output/%s_%s/" % (dirnum, date), shell=True).wait()
		subprocess.Popen("cp HASHTEMP/NT.out output/%s_%s/" % (dirnum, date), shell=True).wait()
		subprocess.Popen("mv userlist.txt output/%s_%s/" % (dirnum, date), shell=True).wait()
		subprocess.Popen("rm -rf HASHTEMP", shell=True).wait()
		print "\033[92m[*] Done! Hashes saved in 'output/%s_%s/'.\033[0m" % (dirnum, date)
	else:
		print "\033[91m[!] Error extracting hashes\033[0m"

# Yes/No prompt function
def yesno(question, default="yes"):
	valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
	if default is None:
		prompt = " [y/n] "
	elif default == "yes":
		prompt = " [Y/n] "
	elif default == "no":
		prompt = " [y/N] "
	else:
		raise ValueError("invalid default answer: '%s'" % default)

	while True:
		sys.stdout.write("\033[93m" + question + prompt + "\033[0m")
		choice = raw_input().lower()
		if default is not None and choice == '':
			return valid[default]
		elif choice in valid:
			return valid[choice]
		else:
			sys.stdout.write("Please respond with 'y' or 'n'.\n")

# Call functions
try:
	checkfiles(ntdsfile, systemfile, exporter, extractor)
	hash_export(exporter, ntdsfile)
	# Make sure files were properly exported before running extractor
	if os.path.isdir("HASHTEMP/ntds.export"):
		hash_extract(extractor, systemfile)
	else:
		print "\033[91m[!] Error exporting from '%s'\033[0m" % ntdsfile
		sys.exit()
	cleanup()
except:
	print "\033[91mExiting...\033[0m"
	if os.path.isdir("HASHTEMP"):
		subprocess.Popen("rm -rf HASHTEMP", shell=True).wait()
