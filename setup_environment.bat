@echo off
echo 设置统一虚拟环境 - Real Python 项目集合
echo ==========================================

REM 检查虚拟环境是否存在
if not exist "shared_venv" (
    echo 创建虚拟环境...
    python -m venv shared_venv
    if errorlevel 1 (
        echo 创建虚拟环境失败！请检查Python是否正确安装。
        pause
        exit /b 1
    )
)

echo 激活虚拟环境...
call shared_venv\Scripts\activate.bat
if errorlevel 1 (
    echo 激活虚拟环境失败！
    pause
    exit /b 1
)

echo 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 依赖包安装失败！
    pause
    exit /b 1
)

echo 下载Spacy英文模型...
python -m spacy download en_core_web_sm

echo.
echo ==========================================
echo 环境设置完成！
echo 使用以下命令激活虚拟环境：
echo   shared_venv\Scripts\activate.bat
echo ==========================================
pause 