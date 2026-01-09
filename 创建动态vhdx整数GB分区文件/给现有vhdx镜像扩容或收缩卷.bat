@echo off
if "%1"=="" (goto :eof)

(echo select vdisk file="%1" & echo attach vdisk & echo exit) | diskpart

for /f "tokens=1-3" %%a in ('echo list volume^|diskpart ^| findstr /c:"卷"') do set "last_volume=%%b"

::收缩卷
(echo select volume %last_volume% & echo shrink desired=10240 & echo select vdisk file="%1" & echo detach vdisk & echo exit) | diskpart

::扩展分区
rem (echo select vdisk file="%1" & echo expand vdisk maximum=10240 & echo exit) | diskpart
::扩容
rem (echo select volume %last_volume% & echo extend size=10240 & echo select vdisk file="%1" & echo detach vdisk & echo exit) | diskpart

pause