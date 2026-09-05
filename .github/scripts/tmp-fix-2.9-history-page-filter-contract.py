from pathlib import Path

page_path = Path('packages/client/src/components/ApiClientHistoryPage.tsx')
text = page_path.read_text()

old = "type OutcomeFilter = 'all' | 'success' | 'failed' | 'tests';\n"
new = "export type ApiClientHistoryOutcomeFilter = 'all' | 'success' | 'failed' | 'tests';\n\nexport interface ApiClientHistoryFilters {\n  query: string;\n  method: string;\n  outcome: ApiClientHistoryOutcomeFilter;\n}\n"
if old not in text:
    raise SystemExit('history outcome type marker not found')
text = text.replace(old, new, 1)

old = "function hasFailure(entry: ApiClientHistoryEntry): boolean {\n  return !!entry.error\n    || !!entry.scriptError\n    || (entry.status !== undefined && entry.status >= 400)\n    || !!entry.scriptTests?.some((test) => !test.passed);\n}\n"
new = old + "\nexport function filterApiClientHistoryEntries(workspace: ApiClientWorkspaceState, filters: ApiClientHistoryFilters): ApiClientHistoryEntry[] {\n  const needle = filters.query.trim().toLowerCase();\n  return workspace.history.filter((entry) => {\n    const collection = entry.collectionId ? workspace.collections.find((candidate) => candidate.id === entry.collectionId)?.name || '' : '';\n    const folder = entry.folderId ? workspace.folders.find((candidate) => candidate.id === entry.folderId)?.name || '' : '';\n    const matchesSearch = !needle || [entry.executedMethod, entry.resolvedUrl, entry.status, entry.statusText, collection, folder]\n      .filter((value) => value !== undefined)\n      .some((value) => String(value).toLowerCase().includes(needle));\n    const matchesMethod = filters.method === 'all' || entry.executedMethod.toUpperCase() === filters.method;\n    const failed = hasFailure(entry);\n    const matchesOutcome = filters.outcome === 'all'\n      || (filters.outcome === 'success' && !failed)\n      || (filters.outcome === 'failed' && failed)\n      || (filters.outcome === 'tests' && !!entry.scriptTests?.length);\n    return matchesSearch && matchesMethod && matchesOutcome;\n  });\n}\n"
if old not in text:
    raise SystemExit('history failure helper marker not found')
text = text.replace(old, new, 1)

text = text.replace("const [outcome, setOutcome] = useState<OutcomeFilter>('all');", "const [outcome, setOutcome] = useState<ApiClientHistoryOutcomeFilter>('all');", 1)

old = "  const filtered = useMemo(() => {\n    const needle = query.trim().toLowerCase();\n    return workspace.history.filter((entry) => {\n      const collection = entry.collectionId ? workspace.collections.find((candidate) => candidate.id === entry.collectionId)?.name || '' : '';\n      const folder = entry.folderId ? workspace.folders.find((candidate) => candidate.id === entry.folderId)?.name || '' : '';\n      const matchesSearch = !needle || [entry.executedMethod, entry.resolvedUrl, entry.status, entry.statusText, collection, folder]\n        .filter((value) => value !== undefined)\n        .some((value) => String(value).toLowerCase().includes(needle));\n      const matchesMethod = method === 'all' || entry.executedMethod.toUpperCase() === method;\n      const failed = hasFailure(entry);\n      const matchesOutcome = outcome === 'all'\n        || (outcome === 'success' && !failed)\n        || (outcome === 'failed' && failed)\n        || (outcome === 'tests' && !!entry.scriptTests?.length);\n      return matchesSearch && matchesMethod && matchesOutcome;\n    });\n  }, [method, outcome, query, workspace.collections, workspace.folders, workspace.history]);"
new = "  const filtered = useMemo(\n    () => filterApiClientHistoryEntries(workspace, { query, method, outcome }),\n    [method, outcome, query, workspace],\n  );"
if old not in text:
    raise SystemExit('history filtered useMemo marker not found')
text = text.replace(old, new, 1)
text = text.replace("setOutcome(event.target.value as OutcomeFilter)", "setOutcome(event.target.value as ApiClientHistoryOutcomeFilter)", 1)
page_path.write_text(text)

Path('packages/client/src/components/ApiClientHistoryPage.test.tsx').write_text(r'''import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { ApiClientHistoryPage, filterApiClientHistoryEntries } from './ApiClientHistoryPage';
import { createDefaultApiClientWorkspace } from '../utils/api-client-workspace';
import type { ApiClientWorkspaceState } from '../utils/api-client-workspace';

function workspaceFixture(): ApiClientWorkspaceState {
  const workspace = createDefaultApiClientWorkspace();
  return {
    ...workspace,
    history: [
      {
        id: 'history-new',
        collectionId: workspace.collections[0].id,
        request: { method: 'GET', url: '{{baseUrl}}/pets' },
        scripts: { preRequest: '', tests: "flex.test('ok', () => flex.expect(flex.response.code).to.equal(200));" },
        executedMethod: 'GET',
        resolvedUrl: 'https://api.example.test/pets',
        status: 200,
        statusText: 'OK',
        responseTime: 23,
        responseHeaders: [['content-type', 'application/json']],
        responseBody: '{"pets":[]}',
        scriptTests: [{ name: 'ok', passed: true }],
        createdAt: '2026-09-05T10:00:00.000Z',
      },
      {
        id: 'history-old',
        request: { method: 'POST', url: 'https://api.example.test/login' },
        executedMethod: 'POST',
        resolvedUrl: 'https://api.example.test/login',
        status: 500,
        statusText: 'Server Error',
        responseBody: 'boom',
        createdAt: '2026-09-05T09:00:00.000Z',
      },
    ],
  };
}

describe('ApiClientHistoryPage', () => {
  it('shows captured response details and opens an entry back in the client', () => {
    const onLoadRequest = jest.fn();
    const onBack = jest.fn();
    render(<ApiClientHistoryPage workspace={workspaceFixture()} onWorkspaceChange={jest.fn()} onLoadRequest={onLoadRequest} onBack={onBack} theme='light' />);

    expect(screen.getByText('{"pets":[]}')).toBeInTheDocument();
    expect(screen.getByText('content-type')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Open in client/i }));
    expect(onLoadRequest).toHaveBeenCalledWith(
      expect.objectContaining({ method: 'GET', url: '{{baseUrl}}/pets' }),
      expect.objectContaining({ tests: expect.stringContaining("flex.test('ok'") }),
      expect.any(String),
      undefined,
    );
    expect(onBack).toHaveBeenCalled();
  });

  it('filters by search text, collection metadata, method, outcome, and tests', () => {
    const workspace = workspaceFixture();

    expect(filterApiClientHistoryEntries(workspace, { query: 'login', method: 'all', outcome: 'all' }).map((entry) => entry.id)).toEqual(['history-old']);
    expect(filterApiClientHistoryEntries(workspace, { query: 'My Collection', method: 'all', outcome: 'all' }).map((entry) => entry.id)).toEqual(['history-new']);
    expect(filterApiClientHistoryEntries(workspace, { query: '', method: 'GET', outcome: 'all' }).map((entry) => entry.id)).toEqual(['history-new']);
    expect(filterApiClientHistoryEntries(workspace, { query: '', method: 'all', outcome: 'failed' }).map((entry) => entry.id)).toEqual(['history-old']);
    expect(filterApiClientHistoryEntries(workspace, { query: '', method: 'all', outcome: 'success' }).map((entry) => entry.id)).toEqual(['history-new']);
    expect(filterApiClientHistoryEntries(workspace, { query: '', method: 'all', outcome: 'tests' }).map((entry) => entry.id)).toEqual(['history-new']);
  });
});
''')

Path('e2e/api-client-history.spec.cjs').write_text(r'''const { test, expect } = require('@playwright/test');

async function openApiClient(page) {
  await page.goto('/e2e/index.html#get-pets-id');
  await page.getByLabel('path id').fill('42');
  await page.getByRole('button', { name: 'Open in API Client' }).click();
  const apiClient = page.locator('section[aria-labelledby="api-client-heading"]');
  await expect(apiClient).toBeVisible();
  return apiClient;
}

test('API Client full history filters, inspects responses, and reopens requests', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'chromium-desktop', 'desktop history coverage');

  await page.route('https://history.example.test/**', async (route) => {
    const url = new URL(route.request().url());
    const failed = url.pathname.includes('/bad');
    await route.fulfill({
      status: failed ? 500 : 200,
      contentType: 'application/json',
      headers: { 'x-history': failed ? 'bad' : 'good' },
      body: JSON.stringify({ kind: failed ? 'bad' : 'good' }),
    });
  });

  let apiClient = await openApiClient(page);
  await apiClient.getByLabel('Request URL').fill('https://history.example.test/good');
  await apiClient.getByRole('button', { name: 'Send request' }).click();
  await expect(apiClient.getByText(/Response\s+200\s+OK/)).toBeVisible();

  await apiClient.getByLabel('HTTP method').selectOption('POST');
  await apiClient.getByLabel('Request URL').fill('https://history.example.test/bad');
  await apiClient.getByRole('button', { name: 'Send request' }).click();
  await expect(apiClient.getByText(/Response\s+500/)).toBeVisible();

  await page.getByRole('button', { name: 'Open full history · 2' }).click();
  const history = page.locator('section[aria-labelledby="api-client-history-page-heading"]');
  await expect(history).toBeVisible();
  await expect(history.getByText('Request history')).toBeVisible();

  const search = history.getByLabel('Search history');
  await search.fill('bad');
  await expect(search).toHaveValue('bad');
  await expect(history.getByText(/history\.example\.test\/bad/).first()).toBeVisible();
  await expect(history.getByText(/history\.example\.test\/good/)).toHaveCount(0);
  await expect(history.getByText('{"kind":"bad"}')).toBeVisible();

  await search.fill('');
  const outcome = history.getByLabel('History outcome filter');
  await outcome.selectOption('failed');
  await expect(outcome).toHaveValue('failed');
  await expect(history.getByText(/history\.example\.test\/bad/).first()).toBeVisible();
  await expect(history.getByText(/history\.example\.test\/good/)).toHaveCount(0);

  await outcome.selectOption('all');
  const method = history.getByLabel('History method filter');
  await method.selectOption('GET');
  await expect(method).toHaveValue('GET');
  await expect(history.getByText(/history\.example\.test\/good/).first()).toBeVisible();
  await expect(history.getByText(/history\.example\.test\/bad/)).toHaveCount(0);

  await method.selectOption('all');
  await search.fill('bad');
  await history.getByRole('button', { name: /Open in client/i }).click();
  apiClient = page.locator('section[aria-labelledby="api-client-heading"]');
  await expect(apiClient).toBeVisible();
  await expect(apiClient.getByLabel('HTTP method')).toHaveValue('POST');
  await expect(apiClient.getByLabel('Request URL')).toHaveValue('https://history.example.test/bad');

  await page.reload();
  apiClient = await openApiClient(page);
  await page.getByRole('button', { name: 'Open full history · 2' }).click();
  const reopenedHistory = page.locator('section[aria-labelledby="api-client-history-page-heading"]');
  await expect(reopenedHistory.getByText('{"kind":"bad"}')).toBeVisible();
});
''')
