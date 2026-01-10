@echo off
:START
::生成vhdx镜像文件生成路径和文件名
set /p VHDX_PATH=请输入vhdx镜像文件存储位置（例：c:\vdisk.vhdx）:
if /i not "%VHDX_PATH:~-5%"==".vhdx" echo 您设置的镜像扩展名有误，请重输。 & pause>nul & cls & goto START
for %%a in ("%VHDX_PATH%") do if not exist "%%~dpa" md "%%~dpa"
echo "%VHDX_PATH%" | findstr /i "[\\/]" >nul || set "VHDX_PATH=%~dp0%VHDX_PATH%"

::设置镜像磁盘容量
set /p GB="请输入分区大小（单位: GB，范围1-2048）: "

:: 输入验证
echo %GB%|findstr /r "^[0-9][0-9]*$" >nul
if errorlevel 1 (
    echo 错误：请输入有效的正整数！
    timeout /t 2 >nul
    goto START
)

if %GB% LEQ 0 (
    echo 错误：输入值必须大于0！
    timeout /t 2 >nul
    goto START
)

:: 使用PowerShell计算
set "psCommand=$gb=%GB%; $sectorSize=512; $heads=255; $sectors=63;"
set "psCommand=%psCommand% $cylSize=$sectorSize * $heads * $sectors / 1MB;"
set "psCommand=%psCommand% $targetMB=$gb * 1024;"
set "psCommand=%psCommand% $cylCount=[math]::Ceiling($targetMB / $cylSize);"
set "psCommand=%psCommand% $actualMB=[math]::Ceiling($cylCount * $cylSize);"
set "psCommand=%psCommand% $actualMB"

for /f "delims=" %%a in ('powershell -command "%psCommand%"') do set "VHDX_SIZE_MB=%%a"

::查找当前系统最后一个驱动器号
for /f "tokens=1,2 delims=: " %%a in ('wmic logicaldisk get caption^,drivetype ^| findstr /r /c:"^[A-Za-z]"') do set "LASTDRIVE=%%a"

::在当前系统最后一个驱动器号上新增一个驱动器号
set "alphabet=abcdefghijklmnopqrstuvwxyz"
call set "string=%%alphabet:*%LASTDRIVE%=%%"
if not "%string%"=="%alphabet%" (set "DRIVE_LETTER=%string:~0,1%")

:: 创建vhdx虚拟磁盘
(echo create vdisk file="%VHDX_PATH%" maximum=%VHDX_SIZE_MB% type=expandable & echo attach vdisk & echo select vdisk file="%VHDX_PATH%" & echo convert mbr & echo create partition primary ALIGN=1024 & echo format fs=ntfs quick & echo assign letter=%DRIVE_LETTER% & echo exit)|diskpart

::设置系统服务名
for %%I in ("%VHDX_PATH%") do set VDService=%%~nI

::添加开机自启动
schtasks /create /tn "%VDService%" /tr "cmd /c (echo select vdisk file=\"%VHDX_PATH%\"&echo attach vdisk&echo exit)|diskpart" /sc onstart /ru SYSTEM /rl HIGHEST /f

::卸载镜像自启动服务
reg add "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\%VDService%" /f /v "DisplayName" /t REG_SZ /d "%VDService%镜像磁盘"
reg add "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\%VDService%" /f /v "DisplayIcon" /t REG_SZ /d "\"%SystemRoot%\System32\RecoveryDrive.exe\""
reg add "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\%VDService%" /f /v "Publisher" /t REG_SZ /d "虚拟磁盘"
reg add "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\%VDService%" /f /v "DisplayVersion" /t REG_SZ /d "1.0"
reg add "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\%VDService%" /f /v "UninstallString" /t REG_SZ /d "cmd /c @echo off & (echo select vdisk file=\"%VHDX_PATH%\"&echo detach vdisk&echo exit)|diskpart & schtasks /delete /tn "%VDService%" /f & reg query \"HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\%VDService%\" >nul 2>&1 && (REG DELETE \"HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\%VDService%\" /f)"

cls

echo 使用BitLocker加密请选择Y，否则请选择 N 。
choice /C YN /M "请选择："
if errorlevel 2 goto end
if errorlevel 1 goto BitLocker

:BitLocker
::对磁盘BitLocker加密并保存密码至key文件
for /f "skip=2 tokens=1 delims= " %%a in ('manage-bde -on %DRIVE_LETTER%: -RecoveryPassword ^| findstr /C:"-"') do set key=%%a & set "salt=%random%%random%" & call set "data=%%salt%%#%%key%%" & call echo %%data%%>"%temp%\%VDService%1.txt" & certutil -encode "%temp%\%VDService%1.txt" "%temp%\%VDService%2.txt" >nul & (for /f "skip=1 delims=" %%i in ('type "%temp%\%VDService%2.txt"') do if not "%%i"=="-----END CERTIFICATE-----" echo %%i>>"%temp%\%VDService%3.txt") & certutil -f -encode "%temp%\%VDService%3.txt" "%VHDX_PATH:~0,-5%.key" >nul & del "%temp%\%VDService%1.txt" "%temp%\%VDService%2.txt" "%temp%\%VDService%3.txt" 2>nul & attrib +h %VHDX_PATH:~0,-5%.key

::任务计划添加自启动解BitLocker锁
echo ^<?xml version="1.0" encoding="UTF-16"?^>>"%temp%\%VDService%.xml" & echo ^<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^>>>"%temp%\%VDService%.xml" & echo   ^<Triggers^>>>"%temp%\%VDService%.xml" & echo     ^<BootTrigger /^>>>"%temp%\%VDService%.xml" & echo   ^</Triggers^>>>"%temp%\%VDService%.xml" & echo   ^<Principals^>>>"%temp%\%VDService%.xml" & echo     ^<Principal id="System"^>>>"%temp%\%VDService%.xml" & echo       ^<UserId^>S-1-5-18^</UserId^>>>"%temp%\%VDService%.xml" & echo       ^<RunLevel^>HighestAvailable^</RunLevel^>>>"%temp%\%VDService%.xml" & echo     ^</Principal^>>>"%temp%\%VDService%.xml" & echo   ^</Principals^>>>"%temp%\%VDService%.xml" & echo   ^<Actions Context="System"^>>>"%temp%\%VDService%.xml" & echo     ^<Exec^>>>"%temp%\%VDService%.xml" & echo       ^<Command^>cmd.exe^</Command^>>>"%temp%\%VDService%.xml" & echo       ^<Arguments^>/c @echo off ^&amp; (echo select vdisk file="%VHDX_PATH%"^&amp;echo attach vdisk^&amp;echo exit)^|diskpart ^&amp; certutil -decode "%VHDX_PATH:~0,-5%.key" "%%temp%%\%VDService%1.txt" ^&gt;nul ^&amp; certutil -decode "%%temp%%\%VDService%1.txt" "%%temp%%\%VDService%2.txt" ^&gt;nul ^&amp; for /f "delims=" %%i in ('type "%%temp%%\%VDService%2.txt"') do set "data=%%i" ^&amp; call set "key=%%data:*#=%%" ^&amp; del "%%temp%%\%VDService%1.txt" "%%temp%%\%VDService%2.txt" 2^&gt;nul ^&amp; for /f "tokens=1,2,3,4,5" %%a in ('^^(echo select vdisk file="%VHDX_PATH%"^^^&amp;echo detail disk^^^&amp;echo exit^^)^^^|diskpart^^^|find "正常"') do call manage-bde -unlock %%c: -rp %%key%% ^&amp; exit^</Arguments^>>>"%temp%\%VDService%.xml" & echo     ^</Exec^>>>"%temp%\%VDService%.xml" & echo   ^</Actions^>>>"%temp%\%VDService%.xml" & echo ^</Task^>>>"%temp%\%VDService%.xml"

schtasks /create /xml "%temp%\%VDService%.xml" /tn "%VDService%" /f & del "%temp%\%VDService%.xml" 2>nul

::注册表添加驱动器鼠标右键加BitLocker锁菜单
reg add "HKLM\SOFTWARE\Classes\Drive\shell\加 BitLocker 锁" /f /v "AppliesTo" /t REG_SZ /d "System.Volume.BitLockerProtection:=1 OR System.Volume.BitLockerProtection:=3 OR System.Volume.BitLockerProtection:=5"
reg add "HKLM\SOFTWARE\Classes\Drive\shell\加 BitLocker 锁\command" /f /ve /t REG_SZ /d "cmd /c for %%%%i in (%%1) do manage-bde.exe -lock %%%%~di"
:end