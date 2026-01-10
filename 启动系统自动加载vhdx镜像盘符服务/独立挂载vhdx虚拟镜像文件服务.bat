@echo off
::挂载vhdx虚拟磁盘
if "%1"=="" (goto :eof) else (echo select vdisk file="%1"&echo attach vdisk&echo exit)|diskpart

::设置变量key解BitLocker锁
if not exist %~dpn1.key (goto inst) else certutil -decode "%~dpn1.key" "%temp%\%VDService%1.txt" >nul & certutil -decode "%temp%\%VDService%1.txt" "%temp%\%VDService%2.txt" >nul & for /f "delims=" %%i in ('type "%temp%\%VDService%2.txt"') do set "data=%%i" & call set "key=%%data:*#=%%" & del "%temp%\%VDService%1.txt" "%temp%\%VDService%2.txt" 2>nul & for /f "tokens=1,2,3,4,5" %%a in ('^(echo select vdisk file="%1"^&echo detail disk^&echo exit^)^|diskpart^|find "正常"') do call manage-bde -unlock %%c: -rp %%key%%

:inst
::安装镜像自启动服务提示
cls
choice /c yn /m "安装镜像BitLocker解密自启动服务请选Y，否则请选N？"
if errorlevel 2 goto :eof

::设置系统服务名
for %%I in ("%1") do set VDService=%%~nI

::任务计划添加自启动
if not exist %~dpn1.key (schtasks /create /tn "%VDService%" /tr "cmd /c (echo select vdisk file=\"%1\"&echo attach vdisk&echo exit)|diskpart" /sc onstart /ru SYSTEM /rl HIGHEST /f) else echo ^<?xml version="1.0" encoding="UTF-16"?^>>"%temp%\%VDService%.xml" & echo ^<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^>>>"%temp%\%VDService%.xml" & echo   ^<Triggers^>>>"%temp%\%VDService%.xml" & echo     ^<BootTrigger /^>>>"%temp%\%VDService%.xml" & echo   ^</Triggers^>>>"%temp%\%VDService%.xml" & echo   ^<Principals^>>>"%temp%\%VDService%.xml" & echo     ^<Principal id="System"^>>>"%temp%\%VDService%.xml" & echo       ^<UserId^>S-1-5-18^</UserId^>>>"%temp%\%VDService%.xml" & echo       ^<RunLevel^>HighestAvailable^</RunLevel^>>>"%temp%\%VDService%.xml" & echo     ^</Principal^>>>"%temp%\%VDService%.xml" & echo   ^</Principals^>>>"%temp%\%VDService%.xml" & echo   ^<Actions Context="System"^>>>"%temp%\%VDService%.xml" & echo     ^<Exec^>>>"%temp%\%VDService%.xml" & echo       ^<Command^>cmd.exe^</Command^>>>"%temp%\%VDService%.xml" & echo       ^<Arguments^>/c @echo off ^&amp; (echo select vdisk file="%1"^&amp;echo attach vdisk^&amp;echo exit)^|diskpart ^&amp; certutil -decode "%~dpn1.key" "%%temp%%\%VDService%1.txt" ^&gt;nul ^&amp; certutil -decode "%%temp%%\%VDService%1.txt" "%%temp%%\%VDService%2.txt" ^&gt;nul ^&amp; for /f "delims=" %%i in ('type "%%temp%%\%VDService%2.txt"') do set "data=%%i" ^&amp; call set "key=%%data:*#=%%" ^&amp; del "%%temp%%\%VDService%1.txt" "%%temp%%\%VDService%2.txt" 2^&gt;nul ^&amp; for /f "tokens=1,2,3,4,5" %%a in ('^^(echo select vdisk file="%1"^^^&amp;echo detail disk^^^&amp;echo exit^^)^^^|diskpart^^^|find "正常"') do call manage-bde -unlock %%c: -rp %%key%% ^&amp; exit^</Arguments^>>>"%temp%\%VDService%.xml" & echo     ^</Exec^>>>"%temp%\%VDService%.xml" & echo   ^</Actions^>>>"%temp%\%VDService%.xml" & echo ^</Task^>>>"%temp%\%VDService%.xml" & schtasks /create /xml "%temp%\%VDService%.xml" /tn "%VDService%" /f & del "%temp%\%VDService%.xml" 2>nul

::卸载镜像自启动服务
reg add "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\%VDService%" /f /v "DisplayName" /t REG_SZ /d "%VDService%镜像磁盘"
reg add "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\%VDService%" /f /v "DisplayIcon" /t REG_SZ /d "\"%SystemRoot%\System32\RecoveryDrive.exe\""
reg add "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\%VDService%" /f /v "Publisher" /t REG_SZ /d "虚拟磁盘"
reg add "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\%VDService%" /f /v "DisplayVersion" /t REG_SZ /d "1.0"
reg add "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\%VDService%" /f /v "UninstallString" /t REG_SZ /d "cmd /c @echo off & (echo select vdisk file=\"%1\"&echo detach vdisk&echo exit)|diskpart & schtasks /delete /tn "%VDService%" /f & reg query \"HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\%VDService%\" >nul 2>&1 && (REG DELETE \"HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\%VDService%\" /f)"

::注册表添加驱动器鼠标右键加BitLocker锁菜单
reg add "HKLM\SOFTWARE\Classes\Drive\shell\加 BitLocker 锁" /f /v "AppliesTo" /t REG_SZ /d "System.Volume.BitLockerProtection:=1 OR System.Volume.BitLockerProtection:=3 OR System.Volume.BitLockerProtection:=5"
reg add "HKLM\SOFTWARE\Classes\Drive\shell\加 BitLocker 锁\command" /f /ve /t REG_SZ /d "cmd /c for %%%%i in (%%1) do manage-bde.exe -lock %%%%~di"