from pathlib import Path

page_path = Path('packages/client/src/components/ApiClientHistoryPage.tsx')
text = page_path.read_text()

workspace_import = "import type { ApiClientHistoryEntry, ApiClientWorkspaceState } from '../utils/api-client-workspace';\n"
filter_import = "import { filterApiClientHistoryEntries } from '../utils/api-client-history';\nimport type { ApiClientHistoryOutcomeFilter } from '../utils/api-client-history';\n"
if workspace_import not in text:
    raise SystemExit('workspace import marker not found')
text = text.replace(workspace_import, workspace_import + filter_import, 1)

contract = "export type ApiClientHistoryOutcomeFilter = 'all' | 'success' | 'failed' | 'tests';\n\nexport interface ApiClientHistoryFilters {\n  query: string;\n  method: string;\n  outcome: ApiClientHistoryOutcomeFilter;\n}\n\n"
if contract not in text:
    raise SystemExit('history filter type contract not found')
text = text.replace(contract, '', 1)

filter_function = "export function filterApiClientHistoryEntries(workspace: ApiClientWorkspaceState, filters: ApiClientHistoryFilters): ApiClientHistoryEntry[] {\n  const needle = filters.query.trim().toLowerCase();\n  return workspace.history.filter((entry) => {\n    const collection = entry.collectionId ? workspace.collections.find((candidate) => candidate.id === entry.collectionId)?.name || '' : '';\n    const folder = entry.folderId ? workspace.folders.find((candidate) => candidate.id === entry.folderId)?.name || '' : '';\n    const matchesSearch = !needle || [entry.executedMethod, entry.resolvedUrl, entry.status, entry.statusText, collection, folder]\n      .filter((value) => value !== undefined)\n      .some((value) => String(value).toLowerCase().includes(needle));\n    const matchesMethod = filters.method === 'all' || entry.executedMethod.toUpperCase() === filters.method;\n    const failed = hasFailure(entry);\n    const matchesOutcome = filters.outcome === 'all'\n      || (filters.outcome === 'success' && !failed)\n      || (filters.outcome === 'failed' && failed)\n      || (filters.outcome === 'tests' && !!entry.scriptTests?.length);\n    return matchesSearch && matchesMethod && matchesOutcome;\n  });\n}\n\n"
if filter_function not in text:
    raise SystemExit('history filter function not found')
text = text.replace(filter_function, '', 1)
page_path.write_text(text)

Path('packages/client/src/utils/api-client-history.ts').write_text(r'''import type { ApiClientHistoryEntry, ApiClientWorkspaceState } from './api-client-workspace';

export type ApiClientHistoryOutcomeFilter = 'all' | 'success' | 'failed' | 'tests';

export interface ApiClientHistoryFilters {
  query: string;
  method: string;
  outcome: ApiClientHistoryOutcomeFilter;
}

function hasFailure(entry: ApiClientHistoryEntry): boolean {
  return !!entry.error
    || !!entry.scriptError
    || (entry.status !== undefined && entry.status >= 400)
    || !!entry.scriptTests?.some((test) => !test.passed);
}

export function filterApiClientHistoryEntries(
  workspace: ApiClientWorkspaceState,
  filters: ApiClientHistoryFilters,
): ApiClientHistoryEntry[] {
  const needle = filters.query.trim().toLowerCase();
  return workspace.history.filter((entry) => {
    const collection = entry.collectionId
      ? workspace.collections.find((candidate) => candidate.id === entry.collectionId)?.name || ''
      : '';
    const folder = entry.folderId
      ? workspace.folders.find((candidate) => candidate.id === entry.folderId)?.name || ''
      : '';
    const matchesSearch = !needle || [entry.executedMethod, entry.resolvedUrl, entry.status, entry.statusText, collection, folder]
      .filter((value) => value !== undefined)
      .some((value) => String(value).toLowerCase().includes(needle));
    const matchesMethod = filters.method === 'all' || entry.executedMethod.toUpperCase() === filters.method;
    const failed = hasFailure(entry);
    const matchesOutcome = filters.outcome === 'all'
      || (filters.outcome === 'success' && !failed)
      || (filters.outcome === 'failed' && failed)
      || (filters.outcome === 'tests' && !!entry.scriptTests?.length);
    return matchesSearch && matchesMethod && matchesOutcome;
  });
}
''')

test_path = Path('packages/client/src/components/ApiClientHistoryPage.test.tsx')
test = test_path.read_text()
old = "import { ApiClientHistoryPage, filterApiClientHistoryEntries } from './ApiClientHistoryPage';\n"
new = "import { ApiClientHistoryPage } from './ApiClientHistoryPage';\nimport { filterApiClientHistoryEntries } from '../utils/api-client-history';\n"
if old not in test:
    raise SystemExit('history test filter import marker not found')
test_path.write_text(test.replace(old, new, 1))
