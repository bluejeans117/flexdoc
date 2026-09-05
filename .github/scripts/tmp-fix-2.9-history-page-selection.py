from pathlib import Path

path = Path('packages/client/src/components/ApiClientHistoryPage.tsx')
text = path.read_text()
replacements = {
    "onChange={(event) => setQuery(event.target.value)}": "onChange={(event) => { setQuery(event.target.value); setSelectedId(undefined); }}",
    "onChange={(event) => setMethod(event.target.value)}": "onChange={(event) => { setMethod(event.target.value); setSelectedId(undefined); }}",
    "onChange={(event) => setOutcome(event.target.value as OutcomeFilter)}": "onChange={(event) => { setOutcome(event.target.value as OutcomeFilter); setSelectedId(undefined); }}",
}
for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f'history filter marker not found: {old}')
    text = text.replace(old, new, 1)
path.write_text(text)
