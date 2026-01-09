@echo off
:START

::生成vhdx镜像文件生成路径和文件名
set /p VHDX_PATH=请输入vhdx镜像文件存储位置（例：c:\vdisk.vhdx）:
if /i not "%VHDX_PATH:~-5%"==".vhdx" echo 您设置的镜像扩展名有误，请重输。 & pause>nul & cls & goto START
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

:: 执行并检查结果
call :CHECK_RESULT %errorlevel% %DRIVE_LETTER% %VHDX_SIZE_MB%
if errorlevel 1 exit /b 1

:: 使用提示
echo;
echo 卸载命令：diskpart ^> select vdisk file="%VHDX_PATH%" ^> detach vdisk
pause>nul
goto :EOF

:CHECK_RESULT
cls
if %1 equ 0 (
    echo [创建成功] vhdx镜像文件已创建，挂载驱动器为 %2:  容量为 %3 MB
    exit /b 0
) else (
    echo [错误] 操作失败（检查驱动器号冲突或管理员权限）
    pause>nul
    exit /b 1
)