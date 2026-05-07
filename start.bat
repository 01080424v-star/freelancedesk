@echo off
chcp 65001 > nul
title FreelanceDesk

cd /d "%~dp0"

echo.
echo  ================================
echo   FreelanceDesk  —  Запуск
echo  ================================
echo.

:: Перевіряємо Python
python --version > nul 2>&1
if errorlevel 1 (
    echo  [ПОМИЛКА] Python не знайдено.
    echo  Завантажте: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Створюємо venv якщо немає
if not exist "venv\Scripts\activate.bat" (
    echo  [1/4] Створення віртуального середовища...
    python -m venv venv
    if errorlevel 1 (
        echo  [ПОМИЛКА] Не вдалося створити venv
        pause
        exit /b 1
    )
    echo         Готово.
) else (
    echo  [1/4] Віртуальне середовище OK
)

:: Активуємо
call venv\Scripts\activate.bat

:: Встановлюємо залежності
echo  [2/4] Встановлення залежностей...
pip install -r requirements.txt -q --no-warn-script-location
if errorlevel 1 (
    echo  [ПОМИЛКА] pip install провалився
    pause
    exit /b 1
)
echo         Готово.

:: Ініціалізуємо БД
if not exist "instance\app.db" (
    echo  [3/4] Ініціалізація бази даних...
    flask --app run.py seed
    echo         Готово.
) else (
    echo  [3/4] База даних OK
)

:: Запускаємо
echo  [4/4] Запуск сервера...
echo.
echo  ================================
echo   http://127.0.0.1:5001/
echo   Адмін: /admin/login
echo   Логін: admin / admin123
echo  ================================
echo.
echo  Зупинити: Ctrl+C
echo.

:: Відкриваємо браузер через 1.5 сек
start /b cmd /c "timeout /t 2 /nobreak > nul 2>&1 && start http://127.0.0.1:5001/"

flask --app run.py run --port 5001

echo.
pause
