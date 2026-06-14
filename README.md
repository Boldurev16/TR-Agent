# TR Agent

Локальная система исследования документов и бизнес-данных: файловый конвейер PDF/Excel + RAG через **AnythingLLM** и локальные LLM (**Ollama** / **LM Studio**).

**Документация:** [docs/PRD.md](docs/PRD.md)

---

## Архитектура проекта

```mermaid
flowchart TB
    subgraph USER["Пользователь"]
        UI["AnythingLLM Web UI :3001"]
    end

    subgraph HOST["Windows Host"]
        LM["LM Studio :1234/v1<br/>или Ollama :11434"]
        SCRIPTS["Python / PowerShell<br/>scripts/"]
    end

    subgraph DOCKER["Docker"]
        ALLM["AnythingLLM<br/>RAG + Agent Framework"]
        VDB[("Vector DB<br/>эмбеддинги")]
    end

    subgraph DATA["Файловый слой (локально)"]
        INBOX["docs-inbox/<br/>PDF, Excel, CSV"]
        BATCHES["docs-batches/<br/>batch-0001…"]
        KB["excel-batches/<br/>партии Excel"]
        CACHE["cache/<br/>*.txt + *.meta.json"]
        LOGS["logs/"]
    end

    subgraph CONFIG["config/ (локально)"]
        ENV["llm-presets.env"]
        MF["Modelfile"]
        YAML["agents reference.yaml"]
    end

    UI --> ALLM
    ALLM -->|"host.docker.internal"| LM
    ALLM --> VDB
    ALLM -->|"Upload документов"| BATCHES

    SCRIPTS --> INBOX
    SCRIPTS --> BATCHES
    SCRIPTS --> KB
    SCRIPTS --> CACHE
    SCRIPTS --> LOGS

    INBOX -->|"make_pdf_batches.py"| BATCHES
    INBOX -->|"split_radar_by_quadrant.py"| KB
    INBOX -->|"extract_pdf_to_cache.py"| CACHE

    ENV -.-> ALLM
    MF -.-> LM
    YAML -.-> ALLM
```

### Конвейеры данных

```mermaid
flowchart LR
    subgraph PDF["PDF"]
        P1["docs-inbox/"] --> P2["make_pdf_batches.py"]
        P2 --> P3["docs-batches/"]
        P3 --> P4["AnythingLLM RAG"]
        P1 --> P5["extract_pdf_to_cache.py"]
        P5 --> P6["cache/"]
    end

    subgraph Excel["Excel — база знаний"]
        E1["docs-inbox/*.xlsx"] --> E2["split_radar_by_quadrant.py"]
        E2 --> E3["excel-batches/"]
        E3 --> E4["RAG / анализ"]
    end
```

---

## Быстрый старт

```powershell
cd "C:\AI Agent\TR Agent"

# Диагностика окружения
.\scripts\check_environment.ps1

# PDF → батчи по 100
python .\scripts\make_pdf_batches.py

# PDF → текст в cache
python .\scripts\extract_pdf_to_cache.py --all --skip-existing

# Excel → партии базы знаний
python .\scripts\split_radar_by_quadrant.py
```

---

## Структура репозитория

| Путь | Назначение | Git |
|------|------------|-----|
| `docs/` | PRD и документация | ✅ |
| `scripts/` | Утилиты подготовки данных | ✅ |
| `docs-inbox/` | Исходные PDF, Excel, CSV | ❌ |
| `docs-batches/` | PDF-партии | ❌ |
| `cache/`, `logs/`, `config/`, `notes/` | Рабочие данные и настройки | ❌ |
