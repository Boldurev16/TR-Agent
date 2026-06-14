# Мемо: параллельный AnythingLLM без подписи Created with AnythingLLM

Дата: 2026-05-02

## Цель

Создать параллельный контейнер AnythingLLM, в котором агентские навыки генерации файлов PDF/XLSX
не добавляют подпись `Created with AnythingLLM`, не ломая текущий рабочий контейнер проекта.

## Текущий рабочий контейнер

- Container: `local-ai-workspace-anythingllm`
- ID: `5e9200982f6e4e7127bb564c87205f55733b1a6c82b8149c02bd2d802ca84e64`
- Image: `mintplexlabs/anythingllm:latest`
- Image digest/id: `sha256:6421755dbce82dbeed4fdda8113e54b7d88331be70f5921785a7bea81ccc8386`
- AnythingLLM version: `DEPLOYMENT_VERSION=1.12.1`
- Port: `http://localhost:3001`
- Status after work: `healthy`

## Новый параллельный контейнер

- Container: `local-ai-workspace-anythingllm-no-branding`
- Image: `anythingllm-no-branding:1.12.1-local`
- Base image: `mintplexlabs/anythingllm@sha256:6421755dbce82dbeed4fdda8113e54b7d88331be70f5921785a7bea81ccc8386`
- AnythingLLM version: `DEPLOYMENT_VERSION=1.12.1`
- Port: `http://localhost:3002`
- Status after work: `healthy`

## Что изменено

Код генерации PDF/XLSX не удалялся целиком. Чтобы не нарушить зависимости и экспорты, в функции
`applyBranding` добавлен ранний `return`.

Измененные места внутри кастомного образа:

- `/app/server/utils/agents/aibitat/plugins/create-files/pdf/utils.js`
- `/app/server/utils/agents/aibitat/plugins/create-files/xlsx/utils.js`

Проверено:

- `applyBranding` в PDF начинается с `return`.
- `applyBranding` в XLSX начинается с `return`.
- `pdf-lib` доступен.
- `exceljs` доступен.
- `create-pdf-file.js` загружается.
- `create-excel-file.js` загружается.

## Данные и mounts

Новый контейнер не использует рабочий volume старого контейнера напрямую.

- Старый volume: `local-ai-workspace_anythingllm-storage`
- Новый cloned volume: `local-ai-workspace_anythingllm-storage-no-branding`
- Старые bind mounts:
  - `C:\AI Agent\Local_qwen-coder\local-ai-workspace\workspace\uploads`
  - `C:\AI Agent\Local_qwen-coder\local-ai-workspace\workspace\artifacts`
- Новые bind mounts:
  - `C:\AI Agent\Local_qwen-coder\local-ai-workspace\workspace-no-branding\uploads`
  - `C:\AI Agent\Local_qwen-coder\local-ai-workspace\workspace-no-branding\artifacts`

## Backup

Backup создан до запуска нового контейнера:

`C:\AI Agent\Local_qwen-coder\local-ai-workspace\backups\anythingllm-no-branding-2026-05-02_10-52-40`

Содержит:

- `container-inspect.json`
- `image-inspect.json`
- `volume-inspect.json`
- `anythingllm-storage.tgz`
- `workspace-bind-mounts.zip`
- `BACKUP_LOCATION.txt`

## Быстрый безопасный откат

Самый безопасный откат: просто продолжить пользоваться старым контейнером на `http://localhost:3001`.
Он не был изменен.

Чтобы остановить новый контейнер:

```powershell
docker stop local-ai-workspace-anythingllm-no-branding
```

Чтобы удалить только новый контейнер:

```powershell
docker rm -f local-ai-workspace-anythingllm-no-branding
```

Чтобы дополнительно удалить новый образ и cloned volume после успешного отката:

```powershell
docker image rm anythingllm-no-branding:1.12.1-local
docker volume rm local-ai-workspace_anythingllm-storage-no-branding
```

Не удалять старый volume:

```text
local-ai-workspace_anythingllm-storage
```

## Полное восстановление старого storage из backup

Использовать только если старый рабочий volume когда-либо будет поврежден.
Сейчас это не требуется.

1. Остановить старый контейнер:

```powershell
docker stop local-ai-workspace-anythingllm
```

2. Восстановить storage из backup:

```powershell
docker run --rm `
  -v local-ai-workspace_anythingllm-storage:/target `
  -v "C:\AI Agent\Local_qwen-coder\local-ai-workspace\backups\anythingllm-no-branding-2026-05-02_10-52-40:/backup" `
  alpine sh -c "cd /target && tar xzf /backup/anythingllm-storage.tgz -C /target"
```

3. Запустить старый контейнер:

```powershell
docker start local-ai-workspace-anythingllm
```

## Что проверить вручную

Попросить пользователя проверить новый контейнер в UI:

- открыть `http://localhost:3002`;
- зайти в нужный workspace;
- сгенерировать PDF через agent skill;
- сгенерировать XLSX через agent skill;
- убедиться, что внутри файлов нет `Created with AnythingLLM`;
- убедиться, что старый контейнер на `http://localhost:3001` продолжает работать.

## Важное ограничение

Так как новый контейнер использует cloned volume, изменения в новом контейнере не синхронизируются
автоматически со старым. Это сделано намеренно ради безопасного параллельного тестирования.
