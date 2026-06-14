$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

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

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:11434/api/tags" -UseBasicParsing -TimeoutSec 5
    Write-Host "OK: Ollama API is available"
} catch {
    Write-Host "ERROR: Ollama API is not available"
}
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
Write-Host "Checking AnythingLLM..."

try {
    $anythingResponse = Invoke-WebRequest -Uri "http://localhost:3001" -UseBasicParsing -TimeoutSec 5
    Write-Host "OK: AnythingLLM is available at http://localhost:3001"
} catch {
    Write-Host "ERROR: AnythingLLM is not available at http://localhost:3001"
}
Write-Host ""
Write-Host "Checking LM Studio (OpenAI-compatible API on port 1234)..."

try {
    $lmModels = Invoke-RestMethod -Uri "http://127.0.0.1:1234/v1/models" -TimeoutSec 5 -Method Get
    Write-Host "OK: LM Studio API is available at http://127.0.0.1:1234/v1"
    if ($lmModels.data) {
        Write-Host "Models exposed by the server (id -> use in AnythingLLM):"
        foreach ($m in $lmModels.data) {
            Write-Host "  - $($m.id)"
        }
    } else {
        Write-Host "(No model list in response; server still answered.)"
    }
} catch {
    Write-Host "SKIP: LM Studio API not on http://127.0.0.1:1234/v1 (start app, load a model, enable Local Server)"
}
Write-Host ""
Write-Host "Docker -> host LLM (AnythingLLM in a container):"
Write-Host "  Base URL example: http://host.docker.internal:1234/v1"
Write-Host "  (localhost inside the container is NOT your Windows host.)"
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