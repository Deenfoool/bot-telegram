@echo off
echo.
echo ========================================
echo    Выполняется очистка диска C: ...
echo ========================================
echo.

echo 1. Выполняется проверка целостности системных файлов (SFC /scannow)...
sfc /scannow

echo.
echo 2. Запускаем DISM для восстановления компонентов...
dism /online /cleanup-image /restorehealth

echo.
echo 3. Запускаем очистку диска (CleanMgr)...
cleanmgr /sagerun:1

echo.
echo 4. Отключение файла гибернации (освобождает место на диске)...
powercfg /h off

echo.
echo 5. Очистка временных файлов через DISM...
dism /online /cleanup-image /startcomponentcleanup

echo.
echo 6. Очистка старых файлов Windows (WinSxS)...
dism /online /cleanup-image /spsuperseded

echo.
echo 7. Очистка временных файлов пользователя...
del /f /s /q "%temp%\*.*"
del /f /s /q "%systemroot%\Temp\*.*"

echo.
echo 8. Очистка кэша Windows (ресурсы, кэш обновлений)...
net stop wuauserv
net stop bits
rd /s /q %windir%\SoftwareDistribution
rd /s /q %windir%\Temp
net start wuauserv
net start bits

echo.
echo ========================================
echo    Очистка завершена!
echo    Проверьте диск C: — должно освободиться место.
echo ========================================
pause