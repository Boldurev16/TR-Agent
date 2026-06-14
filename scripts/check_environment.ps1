$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

# Заглушки endpoint — задайте реальные URL локально или в config/ (не коммитить секреты).
$Endpoints = @{
    LangChainCoreRuntime = "<LANGCHAIN_CORE_RUNTIME_URL>"
    OllamaApi            = "<OLLAMA_API_URL>"
    LlmProviderApi       = "<LLM_PROVIDER_API_URL>"
}

function Write-EndpointCheck {
    param(
        [string]$Name,
        [string]$Url
    )

    if ($Url -match '^<.+>$') {
        Write-Host "SKIP: $Name — endpoint not configured (stub: $Url)"
        return
    }

    try {
        $null = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
        Write-Host "OK: $Name is available"
    } catch {
        Write-Host "ERROR: $Name is not available"
    }
}

Write-Host "TR Agent environment check"
Write-Host "Project folder:"
Write-Host $ProjectRoot

Write-Host ""
Write-Host "Checking Ollama..."

$ollamaCommand = Get-Command ollama -ErrorAction SilentlyContinue

if ($ollamaCommand) {
    Write-Host "OK: Ollama command found"
    ollama --version
    Write-Host "Installed Ollama models:"
    ollama list
} else {
    Write-Host "ERROR: Ollama command not found"
}

Write-Host ""
Write-Host "Checking Ollama API..."
Write-EndpointCheck -Name "Ollama API" -Url $Endpoints.OllamaApi

Write-Host ""
Write-Host "Checking Docker..."

$dockerCommand = Get-Command docker -ErrorAction SilentlyContinue

if ($dockerCommand) {
    Write-Host "OK: Docker command found"

    docker info --format "Docker server version: {{.ServerVersion}}" 2>$null

    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: Docker daemon is running"
    } else {
        Write-Host "ERROR: Docker Desktop is not running"
    }
} else {
    Write-Host "ERROR: Docker command not found"
}

Write-Host ""
Write-Host "Checking LangChain Core Agent Runtime..."
Write-EndpointCheck -Name "LangChain Core Agent Runtime" -Url $Endpoints.LangChainCoreRuntime

Write-Host ""
Write-Host "Checking LLM Provider (OpenAI-compatible API)..."
try {
    if ($Endpoints.LlmProviderApi -match '^<.+>$') {
        Write-Host "SKIP: LLM Provider — endpoint not configured (stub: $($Endpoints.LlmProviderApi))"
    } else {
        $modelsUrl = $Endpoints.LlmProviderApi.TrimEnd('/') + "/models"
        $lmModels = Invoke-RestMethod -Uri $modelsUrl -TimeoutSec 5 -Method Get
        Write-Host "OK: LLM Provider API is available"
        if ($lmModels.data) {
            Write-Host "Models exposed by the server (id -> use in LangChain Core UI):"
            foreach ($m in $lmModels.data) {
                Write-Host "  - $($m.id)"
            }
        } else {
            Write-Host "(No model list in response; server still answered.)"
        }
    }
} catch {
    Write-Host "ERROR: LLM Provider API is not available"
}

Write-Host ""
Write-Host "LangChain Core Runtime -> LLM Provider:"
Write-Host "  Configure Base URL stub: $($Endpoints.LlmProviderApi)"
Write-Host "  (Runtime in Docker must reach the host LLM Provider, not container loopback.)"

Write-Host ""
Write-Host "Checking system resources..."

$os = Get-CimInstance Win32_OperatingSystem
$totalRamGb = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$freeRamGb = [math]::Round($os.FreePhysicalMemory / 1MB, 2)

Write-Host "Total RAM GB: $totalRamGb"
Write-Host "Free RAM GB: $freeRamGb"

Write-Host ""
Write-Host "Disk space:"
Get-PSDrive -PSProvider FileSystem | Select-Object Name, Root, @{
    Name = "FreeGB"
    Expression = { [math]::Round($_.Free / 1GB, 2) }
}, @{
    Name = "UsedGB"
    Expression = { [math]::Round($_.Used / 1GB, 2) }
} | Format-Table -AutoSize

Write-Host ""
Write-Host "GPU:"
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion | Format-Table -AutoSize

Write-Host ""
Write-Host "Checking project folders..."

$requiredFolders = @(
    "scripts",
    "config",
    "docs-inbox",
    "docs-batches",
    "cache",
    "logs",
    "notes"
)

foreach ($folder in $requiredFolders) {
    if (Test-Path $folder) {
        Write-Host "OK: $folder"
    } else {
        Write-Host "ERROR: Missing folder $folder"
    }
}
