from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text()
    if old not in text:
        raise SystemExit(f'marker not found in {path}: {old[:80]!r}')
    file.write_text(text.replace(old, new, 1))


# Preserve provenance for history entries whose collection/folder was deleted.
replace_once(
    'packages/client/src/components/ApiClientHistoryPage.tsx',
    "            const origin = entry.collectionId ? workspace.collections.find((candidate) => candidate.id === entry.collectionId)?.name : undefined;",
    "            const origin = entry.collectionId ? workspace.collections.find((candidate) => candidate.id === entry.collectionId)?.name || 'Deleted collection' : undefined;",
)
replace_once(
    'packages/client/src/components/ApiClientHistoryPage.tsx',
    "                  <div className={`mt-1 text-xs ${mutedClass}`}>{displayTime(selected.createdAt)}{collection ? ` · ${collection.name}` : ''}{folder ? ` / ${folder.name}` : ''}</div>",
    "                  <div className={`mt-1 text-xs ${mutedClass}`}>{displayTime(selected.createdAt)}{selected.collectionId ? ` · ${collection?.name || 'Deleted collection'}` : ''}{selected.folderId ? ` / ${folder?.name || 'Deleted folder'}` : ''}</div>",
)
replace_once(
    'packages/client/src/utils/api-client-history.ts',
    "    const collection = entry.collectionId ? workspace.collections.find((candidate) => candidate.id === entry.collectionId)?.name || '' : '';\n    const folder = entry.folderId ? workspace.folders.find((candidate) => candidate.id === entry.folderId)?.name || '' : '';",
    "    const collection = entry.collectionId ? workspace.collections.find((candidate) => candidate.id === entry.collectionId)?.name || 'Deleted collection' : '';\n    const folder = entry.folderId ? workspace.folders.find((candidate) => candidate.id === entry.folderId)?.name || 'Deleted folder' : '';",
)
replace_once(
    'packages/client/src/components/ApiClientHistoryPage.test.tsx',
    "    expect(filterApiClientHistoryEntries(workspace, { query: '', method: 'all', outcome: 'tests' }).map((entry) => entry.id)).toEqual(['history-new']);\n  });",
    "    expect(filterApiClientHistoryEntries(workspace, { query: '', method: 'all', outcome: 'tests' }).map((entry) => entry.id)).toEqual(['history-new']);\n\n    const deletedCollectionWorkspace = { ...workspace, collections: [] };\n    expect(filterApiClientHistoryEntries(deletedCollectionWorkspace, { query: 'deleted collection', method: 'all', outcome: 'all' }).map((entry) => entry.id)).toEqual(['history-new']);\n  });",
)

# Legacy browser coverage now uses the full history page for provenance and actions.
collection_e2e = Path('e2e/api-client-collection-variables.spec.cjs')
text = collection_e2e.read_text()
old = """  await apiClient.getByRole('button', { name: 'Second', exact: true }).click();
  await apiClient.getByRole('button', { name: 'Delete collection My Collection', exact: true }).click();
  await expect(apiClient.getByText(/Deleted collection/).first()).toBeVisible();
  await apiClient.getByRole('button', { name: 'Load history request GET https://history-one.example.test/pets?locale=fr', exact: true }).first().click();
  await expect(apiClient.getByLabel('Collection variable 1 value')).toHaveValue('https://history-two.example.test');
"""
new = """  await apiClient.getByRole('button', { name: 'Second', exact: true }).click();
  await apiClient.getByRole('button', { name: 'Delete collection My Collection', exact: true }).click();
  await apiClient.getByRole('button', { name: /Open full history ·/ }).click();
  const history = page.locator('section[aria-labelledby=\"api-client-history-page-heading\"]');
  await expect(history).toBeVisible();
  await history.getByLabel('Search history').fill('history-one.example.test');
  await expect(history.getByText('Deleted collection').first()).toBeVisible();
  await history.getByRole('button', { name: /Open in client/i }).click();
  await expect(apiClient).toBeVisible();
  await expect(apiClient.getByLabel('Collection variable 1 value')).toHaveValue('https://history-two.example.test');
"""
if old not in text:
    raise SystemExit('collection replay E2E marker not found')
text = text.replace(old, new, 1)
old = """  await expect(apiClient.getByText(/Response\\s+200\\s+OK/)).toBeVisible();
  const historyEntry = apiClient.getByRole('button', {
    name: 'Load history request GET https://history-start.example.test/pets?locale=fr',
    exact: true,
  });
  await expect(historyEntry).toContainText('My Collection');
"""
new = """  await expect(apiClient.getByText(/Response\\s+200\\s+OK/)).toBeVisible();
  await apiClient.getByRole('button', { name: /Open full history ·/ }).click();
  const history = page.locator('section[aria-labelledby=\"api-client-history-page-heading\"]');
  await expect(history).toBeVisible();
  await expect(history.getByText('My Collection').first()).toBeVisible();
"""
if old not in text:
    raise SystemExit('collection send-start E2E marker not found')
collection_e2e.write_text(text.replace(old, new, 1))

scripting_e2e = Path('e2e/api-client-scripting.spec.cjs')
text = scripting_e2e.read_text()
old = """  await expect(reopenedClient.getByText('3/3 tests passed')).toBeVisible();

  await reopenedClient.getByRole('button', { name: 'Clear history' }).click();
  await expect(reopenedClient.getByRole('button', { name: 'Load history request GET https://script.example.test/pets/77?locale=fr' })).toHaveCount(0);
  await expect.poll(async () => (await readApiClientWorkspace(page))?.history?.length).toBe(0);
"""
new = """  await expect(reopenedClient.getByText('3/3 tests passed')).toBeVisible();

  await reopenedClient.getByRole('button', { name: /Open full history ·/ }).click();
  const history = page.locator('section[aria-labelledby=\"api-client-history-page-heading\"]');
  await expect(history).toBeVisible();
  await history.getByRole('button', { name: 'Clear history' }).click();
  await expect(history.getByText('0 persisted requests')).toBeVisible();
  await expect.poll(async () => (await readApiClientWorkspace(page))?.history?.length).toBe(0);
"""
if old not in text:
    raise SystemExit('scripting clear-history E2E marker not found')
scripting_e2e.write_text(text.replace(old, new, 1))
