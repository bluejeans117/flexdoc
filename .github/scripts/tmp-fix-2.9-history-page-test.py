from pathlib import Path

path = Path('packages/client/src/utils/api-client-execution.test.ts')
text = path.read_text()
old = "      responseBody: '{\\\"id\\\":42}',\n"
new = "      responseBody: '{\"id\":42}',\n"
if old not in text:
    raise SystemExit('history execution expectation marker not found')
path.write_text(text.replace(old, new, 1))
