# Week5 环境安装与测试命令（Windows / PowerShell）

在仓库根目录 `modern-software-dev-assignments` 执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install fastapi "uvicorn[standard]" sqlalchemy pydantic python-dotenv openai ollama pytest httpx black ruff pre-commit
```

运行测试（在 `week5` 目录）：

```powershell
$env:PATH = "g:\software\modern-software-dev-assignments\.venv\Scripts;" + $env:PATH
make test
```
