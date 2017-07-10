# pullhashes
Extract hashes from a ntds.dit file


# Description
Windows Active Directory servers store domain user password hashes in a file named 'ntds.dit'.  This script automates the process of extracting usable hashes from this file (in a format that can be used with password cracking programs like John the Ripper).


After performing a couple password audits, I found it cumbersome to go through the process of dumping hashes from the ntds.dit file so I created this script to simplify the process.  It automatically installs depencencies and runs the necessary programs in order; just input the ntds.dit and SYSTEM files.


# Instructions
```Usage: './pullhashes.py <ntds.dit file> <SYSTEM file>'```



1. Input ntds.dit and SYSTEM files
2. Three files will be created:
  * "LM.out" - LM hashes
  * "NT.out" - NT hashes
  * "userlist.txt" - full list of users and associated permissions, etc.


# Dependencies
This script uses two external programs (already included in this repo under 'resources'): [libesedb](https://github.com/libyal/libesedb) and [ntdsxtract](https://github.com/csababarta/ntdsxtract)
