<#
.SYNOPSIS
MetisAI 项目初始化脚本

.DESCRIPTION
这个 PowerShell 脚本用于初始化 MetisAI 项目的开发环境，包括：
- 检查必要的工具是否安装
- 创建项目目录结构
- 设置 Python 虚拟环境
- 安装前端和后端依赖
- 启动开发服务器

.PARAMETER NoDocker
不检查 Docker 依赖（用于快速开发）

.PARAMETER Clean
清理现有的虚拟环境和依赖，重新安装

.EXAMPLE
.\init.ps1
正常初始化并启动服务器

.EXAMPLE
.\init.ps1 -NoDocker
不检查 Docker 依赖，快速初始化

.EXAMPLE
.\init.ps1 -Clean
清理现有环境并重新初始化
#>

param(
    [switch]$NoDocker,
    [switch]$Clean
)

# 颜色输出函数
function Write-Color {
    param(
        [string]$Text,
        [ConsoleColor]$ForegroundColor = 'White',
        [ConsoleColor]$BackgroundColor = 'Black'
    )
    $original = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Host $Text
    $host.UI.RawUI.ForegroundColor = $original
}

Write-Color "=== MetisAI 项目初始化 ===" -ForegroundColor Green
Write-Host ""

# 检查必要的工具
function Check-Requirements {
    if (-not $NoDocker) {
        Write-Color "检查 Docker 依赖..." -ForegroundColor Yellow
        if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
            Write-Color "❌ Docker 未安装，请先安装 Docker Desktop" -ForegroundColor Red
            Write-Host "下载地址: https://www.docker.com/get-started"
            return $false
        }

        if (-not (Get-Command "docker-compose" -ErrorAction SilentlyContinue)) {
            Write-Color "❌ Docker Compose 未安装" -ForegroundColor Red
            return $false
        }

        Write-Color "✅ Docker 依赖检查通过" -ForegroundColor Green
        Write-Host ""
    }

    Write-Color "检查 Python 依赖..." -ForegroundColor Yellow
    if (-not (Get-Command "python3" -ErrorAction SilentlyContinue)) {
        if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
            Write-Color "❌ Python 未安装，请安装 Python 3.12+ 版本" -ForegroundColor Red
            Write-Host "下载地址: https://www.python.org/downloads/"
            return $false
        }
    }

    Write-Color "✅ Python 依赖检查通过" -ForegroundColor Green
    Write-Host ""

    Write-Color "检查 Node.js 依赖..." -ForegroundColor Yellow
    if (-not (Get-Command "node" -ErrorAction SilentlyContinue)) {
        Write-Color "❌ Node.js 未安装，请安装 Node.js 18+ 版本" -ForegroundColor Red
        Write-Host "下载地址: https://nodejs.org/"
        return $false
    }

    Write-Color "✅ Node.js 依赖检查通过" -ForegroundColor Green
    Write-Host ""

    return $true
}

# 创建项目目录
function Setup-Directories {
    Write-Color "创建项目目录..." -ForegroundColor Yellow

    $directories = @("backend", "frontend", "data")
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Color "  ✅ 创建目录: $dir" -ForegroundColor Green
        }
    }

    Write-Host ""
}

# 设置后端
function Setup-Backend {
    Write-Color "设置后端环境..." -ForegroundColor Yellow

    Set-Location "backend"

    if ($Clean -and (Test-Path "venv")) {
        Write-Color "清理现有虚拟环境..." -ForegroundColor Yellow
        Remove-Item -Path "venv" -Recurse -Force
    }

    if (-not (Test-Path "venv")) {
        Write-Color "创建 Python 虚拟环境..." -ForegroundColor Yellow
        if (Get-Command "python3" -ErrorAction SilentlyContinue) {
            python3 -m venv venv
        } else {
            python -m venv venv
        }
    }

    if (Test-Path "venv\Scripts\activate.ps1") {
        & ".\venv\Scripts\Activate.ps1"
    } else {
        Write-Color "❌ 虚拟环境激活脚本未找到" -ForegroundColor Red
        Set-Location ".."
        return $false
    }

    if (-not (Test-Path "requirements.txt")) {
        Write-Color "创建 requirements.txt 文件..." -ForegroundColor Yellow
        $requirements = @"
fastapi
uvicorn
sqlalchemy
pydantic
python-jose[cryptography]
python-multipart
python-socketio
litellm
"@
        $requirements | Out-File -FilePath "requirements.txt" -Encoding utf8
    }

    Write-Color "安装 Python 依赖..." -ForegroundColor Yellow
    pip install -q -r requirements.txt

    Set-Location ".."
    Write-Color "✅ 后端环境设置完成" -ForegroundColor Green
    Write-Host ""
}

# 设置前端
function Setup-Frontend {
    Write-Color "设置前端环境..." -ForegroundColor Yellow

    Set-Location "frontend"

    if (-not (Test-Path "package.json")) {
        Write-Color "初始化 Vite + React + TypeScript 项目..." -ForegroundColor Yellow
        npm create vite@latest . -- --template react-ts
    }

    Write-Color "安装 npm 依赖..." -ForegroundColor Yellow
    npm install -q

    Set-Location ".."
    Write-Color "✅ 前端环境设置完成" -ForegroundColor Green
    Write-Host ""
}

# 创建 Docker 配置
function Create-Docker-Config {
    if (-not $NoDocker -and -not (Test-Path "docker-compose.yml")) {
        Write-Color "创建 docker-compose.yml 文件..." -ForegroundColor Yellow

        $dockerConfig = @"
version: "3.8"

services:
  backend:
    build: ./backend
    container_name: metisai-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/metisai.db
    volumes:
      - ./data:/app/data
    depends_on:
      - frontend

  frontend:
    build: ./frontend
    container_name: metisai-frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
"@
        $dockerConfig | Out-File -FilePath "docker-compose.yml" -Encoding utf8

        Write-Color "✅ Docker 配置创建完成" -ForegroundColor Green
        Write-Host ""
    }
}

# 启动服务器
function Start-Servers {
    Write-Color "启动开发服务器..." -ForegroundColor Yellow

    Write-Color "启动后端服务..." -ForegroundColor Yellow
    if (Test-Path "backend\venv\Scripts\activate.ps1") {
        $backendJob = Start-Job -ScriptBlock {
            param($Path)
            Set-Location $Path
            & ".\venv\Scripts\Activate.ps1"
            python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
        } -ArgumentList $PWD.Path\backend

        Write-Color "✅ 后端服务器正在启动..." -ForegroundColor Green
    }

    Write-Color "启动前端服务..." -ForegroundColor Yellow
    $frontendJob = Start-Job -ScriptBlock {
        param($Path)
        Set-Location $Path
        npm run dev
    } -ArgumentList $PWD.Path\frontend

    Write-Color "✅ 前端服务器正在启动..." -ForegroundColor Green
    Write-Host ""
}

# 主执行函数
function Main {
    if (-not (Check-Requirements)) {
        return $false
    }

    Setup-Directories

    if (-not (Setup-Backend)) {
        return $false
    }

    if (-not (Setup-Frontend)) {
        return $false
    }

    Create-Docker-Config

    Write-Color "=== 初始化完成！ ===" -ForegroundColor Green
    Write-Host ""

    Write-Color "下一步操作：" -ForegroundColor Yellow
    Write-Host "1. 查看 task.json 选择任务"
    Write-Host "2. 按照工作流程实施开发"
    Write-Host "3. 完成后更新 progress.txt"
    Write-Host ""

    Write-Color "服务器启动信息：" -ForegroundColor Yellow
    Write-Host "后端: http://localhost:8000"
    Write-Host "前端: http://localhost:5173"
    Write-Host ""

    Start-Servers

    return $true
}

# 清理函数
function Cleanup {
    Write-Color "清理任务..." -ForegroundColor Yellow
    Get-Job | Stop-Job
    Get-Job | Remove-Job
}

# 主程序入口
try {
    if (-not (Main)) {
        Write-Color "❌ 初始化过程中出错" -ForegroundColor Red
        $host.SetShouldExit(1)
    }
}
catch {
    Write-Color "❌ 初始化失败: $($_.Exception.Message)" -ForegroundColor Red
    $host.SetShouldExit(1)
}
finally {
    Cleanup
}