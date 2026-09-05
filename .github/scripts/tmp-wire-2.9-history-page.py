from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text()
    if old not in text:
        raise SystemExit(f'marker not found in {path}: {old[:80]!r}')
    file.write_text(text.replace(old, new, 1))


def replace_all_count(path: str, old: str, new: str, count: int) -> None:
    file = Path(path)
    text = file.read_text()
    if text.count(old) != count:
        raise SystemExit(f'expected {count} markers in {path}, found {text.count(old)}')
    file.write_text(text.replace(old, new))


# Persist response details as part of the canonical execution result.
execution_path = 'packages/client/src/utils/api-client-execution.ts'
replace_once(
    execution_path,
    "  responseTime?: number;\n  error?: string;",
    "  responseTime?: number;\n  responseHeaders?: Array<[string, string]>;\n  responseBody?: string;\n  error?: string;",
)
replace_once(
    execution_path,
    "      responseTime,\n      ...(scriptTests.length ? { scriptTests } : {}),",
    "      responseTime,\n      responseHeaders: responseHeaders.map(([key, value]) => [key, value]),\n      responseBody: body,\n      ...(scriptTests.length ? { scriptTests } : {}),",
)

# Extend persisted history additively while keeping the v6 workspace readable.
workspace_path = 'packages/client/src/utils/api-client-workspace.ts'
replace_all_count(
    workspace_path,
    "  responseTime?: number;\n  error?: string;",
    "  responseTime?: number;\n  responseHeaders?: Array<[string, string]>;\n  responseBody?: string;\n  responseBodyTruncated?: boolean;\n  error?: string;",
    2,
)
replace_once(
    workspace_path,
    "const HISTORY_LIMIT = 100;",
    "const HISTORY_LIMIT = 100;\nconst HISTORY_RESPONSE_BODY_LIMIT = 256 * 1024;",
)
replace_once(
    workspace_path,
    "function normalizeScriptTestResult(value: unknown): ApiClientScriptTestResult | null {",
    "function isResponseHeader(value: unknown): value is [string, string] {\n  return Array.isArray(value)\n    && value.length === 2\n    && typeof value[0] === 'string'\n    && typeof value[1] === 'string';\n}\n\nfunction normalizeScriptTestResult(value: unknown): ApiClientScriptTestResult | null {",
)
replace_once(
    workspace_path,
    "    || !isOptionalFiniteNumber(value, 'responseTime')\n    || (value.error !== undefined && typeof value.error !== 'string')",
    "    || !isOptionalFiniteNumber(value, 'responseTime')\n    || (value.responseHeaders !== undefined && (!Array.isArray(value.responseHeaders) || !value.responseHeaders.every(isResponseHeader)))\n    || (value.responseBody !== undefined && typeof value.responseBody !== 'string')\n    || (value.responseBodyTruncated !== undefined && typeof value.responseBodyTruncated !== 'boolean')\n    || (value.error !== undefined && typeof value.error !== 'string')",
)
replace_once(
    workspace_path,
    "    responseTime: value.responseTime as number | undefined,\n    error: value.error as string | undefined,",
    "    responseTime: value.responseTime as number | undefined,\n    responseHeaders: Array.isArray(value.responseHeaders) ? value.responseHeaders.map(([key, headerValue]) => [key, headerValue] as [string, string]) : undefined,\n    responseBody: typeof value.responseBody === 'string' ? value.responseBody : undefined,\n    responseBodyTruncated: value.responseBodyTruncated === true ? true : undefined,\n    error: value.error as string | undefined,",
)
replace_once(
    workspace_path,
    "export function addApiClientHistoryEntry(workspace: ApiClientWorkspaceState, input: ApiClientHistoryInput): ApiClientWorkspaceState {\n  const entry: ApiClientHistoryEntry = {",
    "export function addApiClientHistoryEntry(workspace: ApiClientWorkspaceState, input: ApiClientHistoryInput): ApiClientWorkspaceState {\n  const responseBody = input.responseBody === undefined ? undefined : input.responseBody.slice(0, HISTORY_RESPONSE_BODY_LIMIT);\n  const responseBodyTruncated = input.responseBodyTruncated === true || (input.responseBody?.length || 0) > HISTORY_RESPONSE_BODY_LIMIT;\n  const entry: ApiClientHistoryEntry = {",
)
replace_once(
    workspace_path,
    "    responseTime: input.responseTime,\n    error: input.error,",
    "    responseTime: input.responseTime,\n    ...(input.responseHeaders?.length ? { responseHeaders: input.responseHeaders.map(([key, value]) => [key, value] as [string, string]) } : {}),\n    ...(responseBody !== undefined ? { responseBody, ...(responseBodyTruncated ? { responseBodyTruncated: true } : {}) } : {}),\n    error: input.error,",
)

# Compact sidebar history becomes a recent-history launcher rather than the full experience.
Path('packages/client/src/components/ApiClientHistory.tsx').write_text(r'''import React from 'react';
import { Clock3, Trash2 } from 'lucide-react';
import { cloneApiClientScripts } from '../utils/api-client-scripting';
import type { ApiClientRequestScripts } from '../utils/api-client-scripting';
import { cloneRequestDraft } from '../utils/api-client-workspace';
import type { ApiClientWorkspaceState } from '../utils/api-client-workspace';
import type { HttpRequestDraft } from '../utils/http-client';

interface Props {
  workspace: ApiClientWorkspaceState;
  onWorkspaceChange: React.Dispatch<React.SetStateAction<ApiClientWorkspaceState>>;
  onLoadRequest: (request: HttpRequestDraft, scripts?: ApiClientRequestScripts, collectionId?: string, folderId?: string) => void;
  onViewAll?: () => void;
  theme: 'light' | 'dark';
}

function displayTime(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

export const ApiClientHistory: React.FC<Props> = ({ workspace, onWorkspaceChange, onLoadRequest, onViewAll, theme }) => {
  const mutedClass = theme === 'dark' ? 'text-gray-400' : 'text-gray-500';

  const loadHistory = (id: string) => {
    const entry = workspace.history.find((candidate) => candidate.id === id);
    if (!entry) return;
    onLoadRequest(
      cloneRequestDraft(entry.request),
      entry.scripts ? cloneApiClientScripts(entry.scripts) : undefined,
      entry.collectionId,
      entry.folderId,
    );
  };

  const removeHistory = (id: string) => {
    onWorkspaceChange((current) => ({ ...current, history: current.history.filter((entry) => entry.id !== id) }));
  };

  return <section className='space-y-3' aria-labelledby='api-client-history-heading'>
    <div className='flex items-center justify-between gap-2'>
      <div className='flex items-center gap-2'>
        <Clock3 className='h-4 w-4' />
        <h3 id='api-client-history-heading' className='font-semibold'>Recent history</h3>
      </div>
      {workspace.history.length > 0 && onViewAll && <button type='button' className={`text-xs underline underline-offset-2 ${mutedClass}`} onClick={onViewAll}>View all</button>}
    </div>

    <div className='space-y-1'>
      {workspace.history.slice(0, 5).map((entry) => {
        const result = entry.status !== undefined
          ? `${entry.status}${entry.statusText ? ` ${entry.statusText}` : ''}`
          : entry.error ? 'Error' : 'Sent';
        const timing = entry.responseTime !== undefined ? ` · ${entry.responseTime} ms` : '';
        const passedTests = entry.scriptTests?.filter((test) => test.passed).length || 0;
        const testSummary = entry.scriptTests?.length ? `${passedTests}/${entry.scriptTests.length} tests passed` : entry.scriptError ? 'Script error' : undefined;
        return <div key={entry.id} className='group flex items-start gap-1 rounded-md'>
          <button
            type='button'
            className='min-w-0 flex-1 rounded-md px-2 py-2 text-left hover:bg-blue-500/10'
            aria-label={`Load history request ${entry.executedMethod.toUpperCase()} ${entry.resolvedUrl}`}
            onClick={() => loadHistory(entry.id)}
          >
            <div className='flex items-center gap-2 text-xs'>
              <span className='font-mono font-semibold text-blue-600'>{entry.executedMethod.toUpperCase()}</span>
              <span className={entry.error ? 'text-red-600' : mutedClass}>{result}{timing}</span>
            </div>
            <div className='truncate font-mono text-xs' title={entry.resolvedUrl}>{entry.resolvedUrl}</div>
            {testSummary && <div className={`mt-1 text-[11px] ${entry.scriptError ? 'text-red-600' : mutedClass}`}>{testSummary}</div>}
            <div className={`mt-1 text-[11px] ${mutedClass}`}>{displayTime(entry.createdAt)}</div>
          </button>
          <button type='button' className='rounded-md p-2 opacity-70 hover:opacity-100' aria-label={`Delete history request ${entry.executedMethod.toUpperCase()} ${entry.resolvedUrl}`} onClick={() => removeHistory(entry.id)}>
            <Trash2 className='h-4 w-4' />
          </button>
        </div>;
      })}
      {workspace.history.length === 0 && <p className={`px-2 text-xs ${mutedClass}`}>Sent requests appear here for quick replay.</p>}
    </div>

    {workspace.history.length > 0 && onViewAll && <button type='button' className='w-full rounded-md border px-3 py-2 text-xs font-medium hover:bg-blue-500/10' onClick={onViewAll}>Open full history · {workspace.history.length}</button>}
  </section>;
};
''')

# Full history page with filtering, master/detail inspection and replay.
Path('packages/client/src/components/ApiClientHistoryPage.tsx').write_text(r'''import React, { useMemo, useState } from 'react';
import { ArrowLeft, Clock3, RotateCcw, Search, Trash2 } from 'lucide-react';
import { cloneApiClientScripts } from '../utils/api-client-scripting';
import type { ApiClientRequestScripts } from '../utils/api-client-scripting';
import { cloneRequestDraft } from '../utils/api-client-workspace';
import type { ApiClientHistoryEntry, ApiClientWorkspaceState } from '../utils/api-client-workspace';
import type { HttpKeyValue, HttpRequestDraft } from '../utils/http-client';

export interface ApiClientHistoryPageProps {
  workspace: ApiClientWorkspaceState;
  onWorkspaceChange: React.Dispatch<React.SetStateAction<ApiClientWorkspaceState>>;
  onLoadRequest: (request: HttpRequestDraft, scripts?: ApiClientRequestScripts, collectionId?: string, folderId?: string) => void;
  onBack: () => void;
  theme: 'light' | 'dark';
}

type OutcomeFilter = 'all' | 'success' | 'failed' | 'tests';

function displayTime(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function hasFailure(entry: ApiClientHistoryEntry): boolean {
  return !!entry.error
    || !!entry.scriptError
    || (entry.status !== undefined && entry.status >= 400)
    || !!entry.scriptTests?.some((test) => !test.passed);
}

function resultLabel(entry: ApiClientHistoryEntry): string {
  if (entry.error) return 'Request failed';
  if (entry.status !== undefined) return `${entry.status}${entry.statusText ? ` ${entry.statusText}` : ''}`;
  return 'Sent';
}

function enabledPairs(values: HttpKeyValue[] | undefined): HttpKeyValue[] {
  return (values || []).filter((value) => value.enabled !== false && (value.key.trim() || value.value.trim()));
}

function PairDetails({ title, values, mutedClass }: { title: string; values: HttpKeyValue[] | undefined; mutedClass: string }) {
  const visible = enabledPairs(values);
  if (visible.length === 0) return null;
  return <section className='space-y-2'>
    <h4 className='text-xs font-semibold uppercase tracking-wide'>{title}</h4>
    <div className='overflow-hidden rounded-md border'>
      {visible.map((entry, index) => <div key={`${entry.key}:${index}`} className='grid grid-cols-[minmax(8rem,0.35fr)_minmax(0,1fr)] gap-3 border-b px-3 py-2 text-xs last:border-b-0'>
        <span className='break-all font-mono font-medium'>{entry.key || '—'}</span>
        <span className={`break-all font-mono ${mutedClass}`}>{entry.value}</span>
      </div>)}
    </div>
  </section>;
}

export const ApiClientHistoryPage: React.FC<ApiClientHistoryPageProps> = ({ workspace, onWorkspaceChange, onLoadRequest, onBack, theme }) => {
  const [query, setQuery] = useState('');
  const [method, setMethod] = useState('all');
  const [outcome, setOutcome] = useState<OutcomeFilter>('all');
  const [selectedId, setSelectedId] = useState<string | undefined>(workspace.history[0]?.id);
  const inputClass = theme === 'dark' ? 'border-gray-700 bg-gray-900 text-gray-100' : 'border-gray-300 bg-white text-gray-900';
  const panelClass = theme === 'dark' ? 'border-gray-700 bg-gray-800/60 text-gray-100' : 'border-gray-200 bg-gray-50 text-gray-900';
  const mutedClass = theme === 'dark' ? 'text-gray-400' : 'text-gray-500';
  const codeClass = theme === 'dark' ? 'border-gray-700 bg-gray-950 text-gray-100' : 'border-gray-200 bg-white text-gray-900';

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return workspace.history.filter((entry) => {
      const collection = entry.collectionId ? workspace.collections.find((candidate) => candidate.id === entry.collectionId)?.name || '' : '';
      const folder = entry.folderId ? workspace.folders.find((candidate) => candidate.id === entry.folderId)?.name || '' : '';
      const matchesSearch = !needle || [entry.executedMethod, entry.resolvedUrl, entry.status, entry.statusText, collection, folder]
        .filter((value) => value !== undefined)
        .some((value) => String(value).toLowerCase().includes(needle));
      const matchesMethod = method === 'all' || entry.executedMethod.toUpperCase() === method;
      const failed = hasFailure(entry);
      const matchesOutcome = outcome === 'all'
        || (outcome === 'success' && !failed)
        || (outcome === 'failed' && failed)
        || (outcome === 'tests' && !!entry.scriptTests?.length);
      return matchesSearch && matchesMethod && matchesOutcome;
    });
  }, [method, outcome, query, workspace.collections, workspace.folders, workspace.history]);

  const selected = filtered.find((entry) => entry.id === selectedId) || filtered[0];
  const collection = selected?.collectionId ? workspace.collections.find((candidate) => candidate.id === selected.collectionId) : undefined;
  const folder = selected?.folderId ? workspace.folders.find((candidate) => candidate.id === selected.folderId) : undefined;

  const openInClient = (entry: ApiClientHistoryEntry) => {
    onLoadRequest(
      cloneRequestDraft(entry.request),
      entry.scripts ? cloneApiClientScripts(entry.scripts) : undefined,
      entry.collectionId,
      entry.folderId,
    );
    onBack();
  };

  const removeHistory = (id: string) => {
    onWorkspaceChange((current) => ({ ...current, history: current.history.filter((entry) => entry.id !== id) }));
    if (selectedId === id) setSelectedId(undefined);
  };

  const clearHistory = () => {
    onWorkspaceChange((current) => ({ ...current, history: [] }));
    setSelectedId(undefined);
  };

  const responseHeaders = selected?.responseHeaders || [];
  const passedTests = selected?.scriptTests?.filter((test) => test.passed).length || 0;

  return <section className={`rounded-xl border p-4 md:p-5 ${panelClass}`} aria-labelledby='api-client-history-page-heading'>
    <div className='space-y-4'>
      <header className='flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between'>
        <div className='flex items-center gap-3'>
          <button type='button' className='inline-flex min-h-10 items-center gap-2 rounded-md border px-3 py-2 text-sm' onClick={onBack}><ArrowLeft className='h-4 w-4' /> Client</button>
          <div>
            <div className='flex items-center gap-2'><Clock3 className='h-5 w-5' /><h2 id='api-client-history-page-heading' className='text-lg font-semibold'>Request history</h2></div>
            <p className={`text-xs ${mutedClass}`}>{workspace.history.length} persisted request{workspace.history.length === 1 ? '' : 's'} · newest first</p>
          </div>
        </div>
        {workspace.history.length > 0 && <button type='button' className='inline-flex min-h-10 items-center gap-2 self-start rounded-md border px-3 py-2 text-sm text-red-600' onClick={clearHistory}><Trash2 className='h-4 w-4' /> Clear history</button>}
      </header>

      <div className='grid gap-2 md:grid-cols-[minmax(0,1fr)_10rem_10rem]'>
        <label className='relative'>
          <span className='sr-only'>Search history</span>
          <Search className={`pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 ${mutedClass}`} />
          <input aria-label='Search history' className={`w-full rounded-md border py-2 pl-9 pr-3 text-sm ${inputClass}`} value={query} onChange={(event) => setQuery(event.target.value)} placeholder='Search URL, status, collection…' />
        </label>
        <select aria-label='History method filter' className={`rounded-md border px-3 py-2 text-sm ${inputClass}`} value={method} onChange={(event) => setMethod(event.target.value)}>
          <option value='all'>All methods</option>
          {['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'].map((value) => <option key={value} value={value}>{value}</option>)}
        </select>
        <select aria-label='History outcome filter' className={`rounded-md border px-3 py-2 text-sm ${inputClass}`} value={outcome} onChange={(event) => setOutcome(event.target.value as OutcomeFilter)}>
          <option value='all'>All outcomes</option>
          <option value='success'>Successful</option>
          <option value='failed'>Failed</option>
          <option value='tests'>With tests</option>
        </select>
      </div>

      <div className='grid min-h-[32rem] gap-4 lg:grid-cols-[minmax(18rem,0.85fr)_minmax(0,1.35fr)]'>
        <div className='max-h-[48rem] space-y-1 overflow-auto rounded-lg border p-2'>
          {filtered.map((entry) => {
            const active = selected?.id === entry.id;
            const failed = hasFailure(entry);
            const origin = entry.collectionId ? workspace.collections.find((candidate) => candidate.id === entry.collectionId)?.name : undefined;
            return <button
              key={entry.id}
              type='button'
              className={`w-full rounded-md border px-3 py-3 text-left transition ${active ? 'border-blue-500 bg-blue-500/10' : 'border-transparent hover:bg-blue-500/5'}`}
              onClick={() => setSelectedId(entry.id)}
            >
              <div className='flex items-center justify-between gap-3 text-xs'>
                <span className='font-mono font-semibold text-blue-600'>{entry.executedMethod.toUpperCase()}</span>
                <span className={failed ? 'text-red-600' : mutedClass}>{resultLabel(entry)}{entry.responseTime !== undefined ? ` · ${entry.responseTime} ms` : ''}</span>
              </div>
              <div className='mt-1 truncate font-mono text-xs' title={entry.resolvedUrl}>{entry.resolvedUrl}</div>
              <div className={`mt-1 flex items-center justify-between gap-2 text-[11px] ${mutedClass}`}><span className='truncate'>{origin || 'Unsaved request'}</span><span>{displayTime(entry.createdAt)}</span></div>
            </button>;
          })}
          {filtered.length === 0 && <div className={`px-3 py-8 text-center text-sm ${mutedClass}`}>{workspace.history.length === 0 ? 'Send a request to start building history.' : 'No history entries match these filters.'}</div>}
        </div>

        <div className='min-w-0 rounded-lg border p-4'>
          {!selected && <div className={`flex min-h-[20rem] items-center justify-center text-sm ${mutedClass}`}>Select a history entry to inspect it.</div>}
          {selected && <div className='space-y-5'>
            <div className='space-y-2 border-b pb-4'>
              <div className='flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between'>
                <div className='min-w-0'>
                  <div className='flex flex-wrap items-center gap-2 text-sm'><span className='font-mono font-bold text-blue-600'>{selected.executedMethod.toUpperCase()}</span><span className={hasFailure(selected) ? 'text-red-600' : mutedClass}>{resultLabel(selected)}</span>{selected.responseTime !== undefined && <span className={mutedClass}>{selected.responseTime} ms</span>}</div>
                  <div className='mt-1 break-all font-mono text-sm'>{selected.resolvedUrl}</div>
                  <div className={`mt-1 text-xs ${mutedClass}`}>{displayTime(selected.createdAt)}{collection ? ` · ${collection.name}` : ''}{folder ? ` / ${folder.name}` : ''}</div>
                </div>
                <div className='flex shrink-0 gap-2'>
                  <button type='button' className='inline-flex min-h-10 items-center gap-2 rounded-md border px-3 py-2 text-sm font-medium hover:bg-blue-500/10' onClick={() => openInClient(selected)}><RotateCcw className='h-4 w-4' /> Open in client</button>
                  <button type='button' aria-label='Delete selected history entry' className='inline-flex min-h-10 items-center rounded-md border px-3 py-2 text-red-600' onClick={() => removeHistory(selected.id)}><Trash2 className='h-4 w-4' /></button>
                </div>
              </div>
              {selected.error && <div className='rounded-md border border-red-300 bg-red-500/10 px-3 py-2 text-sm text-red-700'>{selected.error}</div>}
            </div>

            <section className='space-y-3'>
              <h3 className='font-semibold'>Request</h3>
              <div className='grid gap-3 text-xs sm:grid-cols-2'><div><span className={mutedClass}>Original URL</span><div className='mt-1 break-all font-mono'>{selected.request.url}</div></div><div><span className={mutedClass}>Content type</span><div className='mt-1 font-mono'>{selected.request.contentType || '—'}</div></div></div>
              <PairDetails title='Query parameters' values={selected.request.query} mutedClass={mutedClass} />
              <PairDetails title='Headers' values={selected.request.headers} mutedClass={mutedClass} />
              {selected.request.body && <div className='space-y-2'><h4 className='text-xs font-semibold uppercase tracking-wide'>Body</h4><pre className={`max-h-72 overflow-auto whitespace-pre-wrap break-words rounded-md border p-3 text-xs ${codeClass}`}>{selected.request.body}</pre></div>}
            </section>

            <section className='space-y-3 border-t pt-4'>
              <div className='flex items-center justify-between gap-2'><h3 className='font-semibold'>Response</h3>{selected.responseBodyTruncated && <span className='text-xs text-amber-600'>Body truncated in history</span>}</div>
              {responseHeaders.length > 0 && <div className='space-y-2'><h4 className='text-xs font-semibold uppercase tracking-wide'>Headers</h4><div className='overflow-hidden rounded-md border'>{responseHeaders.map(([key, value], index) => <div key={`${key}:${index}`} className='grid grid-cols-[minmax(8rem,0.35fr)_minmax(0,1fr)] gap-3 border-b px-3 py-2 text-xs last:border-b-0'><span className='break-all font-mono font-medium'>{key}</span><span className={`break-all font-mono ${mutedClass}`}>{value}</span></div>)}</div></div>}
              {selected.responseBody !== undefined ? <div className='space-y-2'><h4 className='text-xs font-semibold uppercase tracking-wide'>Body</h4><pre className={`max-h-96 overflow-auto whitespace-pre-wrap break-words rounded-md border p-3 text-xs ${codeClass}`}>{selected.responseBody || '(empty response body)'}</pre></div> : <p className={`text-sm ${mutedClass}`}>Response payload was not captured for this older history entry.</p>}
            </section>

            {(selected.scriptTests?.length || selected.scriptError || selected.scriptLogs?.length) && <section className='space-y-3 border-t pt-4'>
              <h3 className='font-semibold'>Tests & console</h3>
              {selected.scriptTests?.length ? <div className='space-y-1'><div className={`text-xs ${mutedClass}`}>{passedTests}/{selected.scriptTests.length} tests passed</div>{selected.scriptTests.map((test, index) => <div key={`${test.name}:${index}`} className={`rounded-md border px-3 py-2 text-sm ${test.passed ? '' : 'border-red-300 bg-red-500/10 text-red-700'}`}><span className='font-medium'>{test.passed ? '✓' : '✕'} {test.name}</span>{test.error && <div className='mt-1 text-xs'>{test.error}</div>}</div>)}</div> : null}
              {selected.scriptError && <div className='rounded-md border border-red-300 bg-red-500/10 px-3 py-2 text-sm text-red-700'>{selected.scriptError}</div>}
              {selected.scriptLogs?.length ? <pre className={`max-h-56 overflow-auto whitespace-pre-wrap rounded-md border p-3 text-xs ${codeClass}`}>{selected.scriptLogs.join('\n')}</pre> : null}
            </section>}

            {(selected.scripts?.preRequest.trim() || selected.scripts?.tests.trim()) && <section className='space-y-3 border-t pt-4'>
              <h3 className='font-semibold'>Scripts used</h3>
              {selected.scripts?.preRequest.trim() && <div className='space-y-2'><h4 className='text-xs font-semibold uppercase tracking-wide'>Pre-request</h4><pre className={`max-h-56 overflow-auto whitespace-pre-wrap rounded-md border p-3 text-xs ${codeClass}`}>{selected.scripts.preRequest}</pre></div>}
              {selected.scripts?.tests.trim() && <div className='space-y-2'><h4 className='text-xs font-semibold uppercase tracking-wide'>Tests</h4><pre className={`max-h-56 overflow-auto whitespace-pre-wrap rounded-md border p-3 text-xs ${codeClass}`}>{selected.scripts.tests}</pre></div>}
            </section>}
          </div>}
        </div>
      </div>
    </div>
  </section>;
};
''')

# Wire the full page into the standalone workspace while preserving recent history in the sidebar.
workspace_component = 'packages/client/src/components/ApiClientWorkspace.tsx'
replace_once(
    workspace_component,
    "import { ApiClientHistory } from './ApiClientHistory';\n",
    "import { ApiClientHistory } from './ApiClientHistory';\nimport { ApiClientHistoryPage } from './ApiClientHistoryPage';\n",
)
replace_once(
    workspace_component,
    "  const [editorRevision, setEditorRevision] = useState(0);\n  const [workspace, setWorkspace] = useState<ApiClientWorkspaceState>(initialWorkspace);",
    "  const [editorRevision, setEditorRevision] = useState(0);\n  const [activeView, setActiveView] = useState<'request' | 'history'>('request');\n  const [workspace, setWorkspace] = useState<ApiClientWorkspaceState>(initialWorkspace);",
)
replace_once(
    workspace_component,
    "  const loadSavedRequest = (request: HttpRequestDraft, scripts?: ApiClientRequestScripts, collectionId?: string, folderId?: string) => {\n    const validCollectionId",
    "  const loadSavedRequest = (request: HttpRequestDraft, scripts?: ApiClientRequestScripts, collectionId?: string, folderId?: string) => {\n    setActiveView('request');\n    const validCollectionId",
)
replace_once(
    workspace_component,
    "          onLoadRequest={loadSavedRequest}\n          theme={theme}\n        />",
    "          onLoadRequest={loadSavedRequest}\n          onViewAll={() => setActiveView('history')}\n          theme={theme}\n        />",
)
replace_once(
    workspace_component,
    "    <ApiClient\n      key={editorRevision}",
    "    {activeView === 'history' ? <ApiClientHistoryPage\n      workspace={workspace}\n      onWorkspaceChange={setWorkspace}\n      onLoadRequest={loadSavedRequest}\n      onBack={() => setActiveView('request')}\n      theme={theme}\n    /> : <ApiClient\n      key={editorRevision}",
)
replace_once(
    workspace_component,
    "      onRequestChange={handleRequestChange}\n    />\n  </div>;",
    "      onRequestChange={handleRequestChange}\n    />}\n  </div>;",
)

# Export the page for hosts that want to compose their own shell.
index_path = 'packages/client/src/index.ts'
replace_once(
    index_path,
    "export type { ApiClientScriptEditorProps } from './components/ApiClientScriptEditor';\n",
    "export type { ApiClientScriptEditorProps } from './components/ApiClientScriptEditor';\nexport { ApiClientHistoryPage } from './components/ApiClientHistoryPage';\nexport type { ApiClientHistoryPageProps } from './components/ApiClientHistoryPage';\n",
)

# Execution coverage verifies response details flow into the history-compatible result.
execution_test = 'packages/client/src/utils/api-client-execution.test.ts'
replace_once(
    execution_test,
    "      status: 200,\n      responseTime: 25,\n    });",
    "      status: 200,\n      responseTime: 25,\n      responseBody: '{\\\"id\\\":42}',\n    });\n    expect(outcome.result?.responseHeaders).toEqual(expect.arrayContaining([['content-type', 'application/json'], ['x-trace', 'server']]));",
)

# Focused persistence coverage for payload capping and normalization.
Path('packages/client/src/utils/api-client-history-details.test.ts').write_text(r'''import { addApiClientHistoryEntry, createDefaultApiClientWorkspace, normalizeApiClientWorkspace } from './api-client-workspace';

describe('api-client history response details', () => {
  it('persists response headers and body on history entries', () => {
    const workspace = addApiClientHistoryEntry(createDefaultApiClientWorkspace(), {
      request: { method: 'GET', url: 'https://api.example.test/pets' },
      executedMethod: 'GET',
      resolvedUrl: 'https://api.example.test/pets',
      status: 200,
      responseHeaders: [['content-type', 'application/json']],
      responseBody: '{"ok":true}',
    });

    expect(workspace.history[0]).toMatchObject({
      responseHeaders: [['content-type', 'application/json']],
      responseBody: '{"ok":true}',
    });
  });

  it('caps large response bodies and marks them as truncated', () => {
    const largeBody = 'x'.repeat((256 * 1024) + 17);
    const workspace = addApiClientHistoryEntry(createDefaultApiClientWorkspace(), {
      request: { method: 'GET', url: 'https://api.example.test/large' },
      executedMethod: 'GET',
      resolvedUrl: 'https://api.example.test/large',
      responseBody: largeBody,
    });

    expect(workspace.history[0].responseBody).toHaveLength(256 * 1024);
    expect(workspace.history[0].responseBodyTruncated).toBe(true);
  });

  it('normalizes response details from persisted v6 workspaces', () => {
    const base = createDefaultApiClientWorkspace();
    const normalized = normalizeApiClientWorkspace({
      ...base,
      history: [{
        id: 'history-1',
        request: { method: 'GET', url: 'https://api.example.test' },
        executedMethod: 'GET',
        resolvedUrl: 'https://api.example.test',
        responseHeaders: [['x-test', 'yes']],
        responseBody: 'hello',
        responseBodyTruncated: true,
        createdAt: '2026-09-05T10:00:00.000Z',
      }],
    });

    expect(normalized.history[0]).toMatchObject({
      responseHeaders: [['x-test', 'yes']],
      responseBody: 'hello',
      responseBodyTruncated: true,
    });
  });
});
''')

# UI coverage for searching, selecting and replaying entries from the full page.
Path('packages/client/src/components/ApiClientHistoryPage.test.tsx').write_text(r'''import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { ApiClientHistoryPage } from './ApiClientHistoryPage';
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
  it('filters history and shows captured response details', () => {
    render(<ApiClientHistoryPage workspace={workspaceFixture()} onWorkspaceChange={jest.fn()} onLoadRequest={jest.fn()} onBack={jest.fn()} theme='light' />);

    expect(screen.getByText('{"pets":[]}')).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Search history'), { target: { value: 'login' } });
    expect(screen.getByText('https://api.example.test/login')).toBeInTheDocument();
    expect(screen.queryByText('{"pets":[]}')).not.toBeInTheDocument();
  });

  it('opens a selected history entry back in the client', () => {
    const onLoadRequest = jest.fn();
    const onBack = jest.fn();
    render(<ApiClientHistoryPage workspace={workspaceFixture()} onWorkspaceChange={jest.fn()} onLoadRequest={onLoadRequest} onBack={onBack} theme='light' />);

    fireEvent.click(screen.getByRole('button', { name: /Open in client/i }));
    expect(onLoadRequest).toHaveBeenCalledWith(
      expect.objectContaining({ method: 'GET', url: '{{baseUrl}}/pets' }),
      expect.objectContaining({ tests: expect.stringContaining("flex.test('ok'") }),
      expect.any(String),
      undefined,
    );
    expect(onBack).toHaveBeenCalled();
  });

  it('filters failed requests independently of method', () => {
    render(<ApiClientHistoryPage workspace={workspaceFixture()} onWorkspaceChange={jest.fn()} onLoadRequest={jest.fn()} onBack={jest.fn()} theme='light' />);

    fireEvent.change(screen.getByLabelText('History outcome filter'), { target: { value: 'failed' } });
    expect(screen.getByText('https://api.example.test/login')).toBeInTheDocument();
    expect(screen.queryByText('https://api.example.test/pets')).not.toBeInTheDocument();
  });
});
''')
