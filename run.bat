@echo off
chcp 65001 >nul
title Запуск сайта Пламенея
color 0A

echo ============================================
echo   Запуск сайта Пламенея
echo ============================================
echo.

:: Переходим в папку с venv
cd /d "C:\Users\videooperator1\Desktop\CorpSite"

:: Активируем виртуальное окружение
echo [*] Активируем виртуальное окружение...
call CorpSite\Scripts\activate.bat

:: Переходим в папку с проектом
cd /d "C:\Users\videooperator1\Desktop\CorpSite\CorpSiteProject"

:: Запускаем сервер
echo.
echo ============================================
echo   Запускаем сервер...
echo   http://127.0.0.1:8000
echo   Нажми Ctrl+C для остановки
echo ============================================
echo.

python manage.py runserver

pause