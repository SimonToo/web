@echo off
if "%1"=="" (goto :eof) else (echo select vdisk file="%1" & echo attach vdisk readonly & echo compact vdisk & echo detach vdisk & echo exit) | diskpart