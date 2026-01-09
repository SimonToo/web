@echo off
reg add "HKCR\Windows.VhdFile\shell" /f /ve /t REG_SZ /d "mount"

reg add "HKCR\Windows.VhdFile\shell\1Mountvhdx" /f /ve /t REG_SZ /d "①加载镜像驱动器"
reg add "HKCR\Windows.VhdFile\shell\1Mountvhdx\command" /f /ve /t REG_SZ /d "cmd /c (echo select vdisk file=\"%%1\"&echo attach vdisk&echo exit)|diskpart"

reg add "HKCR\Windows.VhdFile\shell\2Unmount" /f /ve /t REG_SZ /d "②卸载镜像驱动器"
reg add "HKCR\Windows.VhdFile\shell\2Unmount\command" /f /ve /t REG_SZ /d "cmd /c (echo select vdisk file=\"%%1\"&echo detach vdisk&echo exit)|diskpart"

reg add "HKCR\Windows.VhdFile\shell\3Child" /f /ve /t REG_SZ /d "③创建镜像差分"
reg add "HKCR\Windows.VhdFile\shell\3Child\command" /f /ve /t REG_SZ /d "cmd /c @echo off & for %%%%I in (%%1) do (echo create vdisk file=\"%%%%~dpI%%%%~nI_child%%%%~xI\" parent=\"%%1\"&echo exit)|diskpart"

reg add "HKCR\Windows.VhdFile\shell\4BackupChild" /f /ve /t REG_SZ /d "④创建差分备份"
reg add "HKCR\Windows.VhdFile\shell\4BackupChild\command" /f /ve /t REG_SZ /d "cmd /c @echo off & for %%%%I in (%%1) do (if exist \"%%%%~dpI%%%%~nI_child%%%%~xI\" del \"%%%%~dpI%%%%~nI_child%%%%~xI\" \"%%%%~dpI%%%%~nI_child.bak\") & (echo create vdisk file=\"%%%%~dpI%%%%~nI_child%%%%~xI\" parent=\"%%1\"&echo create vdisk file=\"%%%%~dpI%%%%~nI_child.bak%%%%~xI\" parent=\"%%1\"&echo exit)|diskpart&ren \"%%%%~dpI%%%%~nI_child.bak%%%%~xI\" \"%%%%~nI_child.bak\""

reg add "HKCR\Windows.VhdFile\shell\5RestoreChild" /f /ve /t REG_SZ /d "⑤恢复差分备份"
reg add "HKCR\Windows.VhdFile\shell\5RestoreChild\command" /f /ve /t REG_SZ /d "cmd /c @echo off & for %%%%I in (%%1) do if exist \"%%%%~dpI%%%%~nI_child.bak\" copy \"%%%%~dpI%%%%~nI_child.bak\" \"%%%%~dpI%%%%~nI_child%%%%~xI\""
