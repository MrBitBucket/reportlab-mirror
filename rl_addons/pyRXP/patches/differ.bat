@echo off
rem command used to get patch differences
diff -rc -I"Copyright (c)" -I"\$"Header: -I"\$"Id: -x"Entries" %1 %2 > %3
