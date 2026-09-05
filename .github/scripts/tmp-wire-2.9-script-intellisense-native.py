from pathlib import Path

editor_path = Path('packages/client/src/components/ApiClientScriptEditor.tsx')
editor_path.write_text(r'''import React, { useMemo, useRef, useState } from 'react';
import {
  apiClientScriptCompletionsAtPosition,
} from '../utils/api-client-script-intellisense';
import type {
  ApiClientScriptCompletionContext,
  ApiClientScriptCompletionItem,
  ApiClientScriptPhase,
  ApiClientScriptVariableKeys,
} from '../utils/api-client-script-intellisense';

export interface ApiClientScriptEditorProps {
  ariaLabel: string;
  value: string;
  onChange: (value: string) => void;
  phase: ApiClientScriptPhase;
  theme?: 'light' | 'dark';
  variableKeys?: ApiClientScriptVariableKeys;
}

export const ApiClientScriptEditor: React.FC<ApiClientScriptEditorProps> = ({
  ariaLabel,
  value,
  onChange,
  phase,
  theme = 'light',
  variableKeys = {},
}) => {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const [completion, setCompletion] = useState<ApiClientScriptCompletionContext | null>(null);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const listId = useMemo(() => `api-client-script-completions-${ariaLabel.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`, [ariaLabel]);
  const dark = theme === 'dark';

  const refreshCompletion = (source: string, position: number, explicit = false) => {
    const next = apiClientScriptCompletionsAtPosition(source, position, phase, variableKeys, explicit);
    setCompletion(next);
    setSelectedIndex(0);
  };

  const applyCompletion = (item: ApiClientScriptCompletionItem) => {
    if (!completion) return;
    const nextValue = `${value.slice(0, completion.from)}${item.label}${value.slice(completion.to)}`;
    const nextPosition = completion.from + item.label.length;
    onChange(nextValue);
    setCompletion(null);
    requestAnimationFrame(() => {
      const textarea = textareaRef.current;
      if (!textarea) return;
      textarea.focus();
      textarea.setSelectionRange(nextPosition, nextPosition);
    });
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    const textarea = event.currentTarget;
    if ((event.ctrlKey || event.metaKey) && event.code === 'Space') {
      event.preventDefault();
      refreshCompletion(value, textarea.selectionStart, true);
      return;
    }
    if (!completion || completion.items.length === 0) return;
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setSelectedIndex((current) => (current + 1) % completion.items.length);
      return;
    }
    if (event.key === 'ArrowUp') {
      event.preventDefault();
      setSelectedIndex((current) => (current - 1 + completion.items.length) % completion.items.length);
      return;
    }
    if (event.key === 'Enter' || event.key === 'Tab') {
      event.preventDefault();
      applyCompletion(completion.items[selectedIndex]);
      return;
    }
    if (event.key === 'Escape') {
      event.preventDefault();
      setCompletion(null);
    }
  };

  const selected = completion?.items[selectedIndex];
  const textareaClass = dark
    ? 'w-full min-h-40 max-h-96 resize-y rounded-md border border-gray-700 bg-gray-900 px-3 py-2 font-mono text-xs text-gray-100 outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400'
    : 'w-full min-h-40 max-h-96 resize-y rounded-md border border-gray-300 bg-white px-3 py-2 font-mono text-xs text-gray-900 outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600';
  const popupClass = dark
    ? 'absolute z-50 mt-1 w-full overflow-hidden rounded-md border border-gray-700 bg-gray-900 text-gray-100 shadow-xl'
    : 'absolute z-50 mt-1 w-full overflow-hidden rounded-md border border-gray-200 bg-white text-gray-900 shadow-xl';

  return <div className='relative'>
    <textarea
      ref={textareaRef}
      aria-label={ariaLabel}
      aria-autocomplete='list'
      aria-controls={completion ? listId : undefined}
      aria-expanded={!!completion}
      aria-activedescendant={completion ? `${listId}-${selectedIndex}` : undefined}
      className={textareaClass}
      data-api-client-script-phase={phase}
      data-testid={`${ariaLabel}-editor`}
      onBlur={() => setCompletion(null)}
      onChange={(event) => {
        const nextValue = event.target.value;
        const position = event.target.selectionStart;
        onChange(nextValue);
        refreshCompletion(nextValue, position);
      }}
      onKeyDown={handleKeyDown}
      spellCheck={false}
      value={value}
    />
    {completion && completion.items.length > 0 && <div className={popupClass}>
      <div id={listId} role='listbox' className='max-h-52 overflow-y-auto py-1'>
        {completion.items.map((item, index) => <button
          aria-selected={index === selectedIndex}
          className={`flex w-full items-baseline gap-2 px-3 py-1.5 text-left text-xs ${index === selectedIndex ? (dark ? 'bg-blue-700 text-white' : 'bg-blue-50 text-gray-900') : (dark ? 'hover:bg-gray-800' : 'hover:bg-gray-50')}`}
          id={`${listId}-${index}`}
          key={`${item.kind}-${item.label}`}
          onMouseDown={(event) => {
            event.preventDefault();
            applyCompletion(item);
          }}
          role='option'
          type='button'
        >
          <span className='font-mono font-semibold'>{item.label}</span>
          <span className={`truncate ${index === selectedIndex && dark ? 'text-blue-100' : (dark ? 'text-gray-400' : 'text-gray-500')}`}>{item.signature || item.kind}</span>
        </button>)}
      </div>
      {selected && <div className={`border-t px-3 py-2 text-[11px] ${dark ? 'border-gray-700 text-gray-300' : 'border-gray-200 text-gray-600'}`}>
        {selected.signature && <div className='mb-1 font-mono text-xs'>{selected.signature}</div>}
        <div>{selected.documentation}</div>
      </div>}
    </div>}
    <div className={`mt-1 text-[11px] ${dark ? 'text-gray-400' : 'text-gray-500'}`}>
      IntelliSense: type <code>flex.</code> or press Ctrl+Space. Use ↑/↓ and Enter or Tab to complete. Known variable names are suggested inside variable helpers.
    </div>
  </div>;
};
''')

intellisense_path = Path('packages/client/src/utils/api-client-script-intellisense.ts')
intellisense = intellisense_path.read_text()
intellisense = intellisense.replace(
    "export type ApiClientScriptCompletionKind = 'property' | 'method' | 'function' | 'variable';",
    "export type ApiClientScriptCompletionKind = 'property' | 'method' | 'function' | 'variable' | 'namespace';",
)
context_code = r'''

export interface ApiClientScriptCompletionContext {
  from: number;
  to: number;
  items: ApiClientScriptCompletionItem[];
}

const ROOT_SCRIPT_COMPLETIONS: ApiClientScriptCompletionItem[] = [
  { label: 'flex', kind: 'namespace', documentation: 'FlexDoc request, response, variables, assertions, and test scripting API.' },
  { label: 'console', kind: 'namespace', documentation: 'Captured script console with log, info, warn, and error methods.' },
];

function assertionCompletionContext(textBeforeCursor: string): { path: string; prefix: string } | null {
  const start = textBeforeCursor.lastIndexOf('flex.expect(');
  if (start < 0) return null;
  const tail = textBeforeCursor.slice(start);
  const paths: Array<[RegExp, string]> = [
    [/\.to\.have\.([A-Za-z_$][\w$]*)?$/, 'flex.expect.to.have'],
    [/\.to\.be\.([A-Za-z_$][\w$]*)?$/, 'flex.expect.to.be'],
    [/\.to\.([A-Za-z_$][\w$]*)?$/, 'flex.expect.to'],
  ];
  for (const [pattern, path] of paths) {
    const match = tail.match(pattern);
    if (match) return { path, prefix: match[1] || '' };
  }
  return null;
}

function variableCompletionContext(textBeforeCursor: string): { scope: keyof ApiClientScriptVariableKeys; prefix: string } | null {
  const match = textBeforeCursor.match(/flex\.(environment|collection|variables)\.(?:get|has|set|unset)\(\s*['"]([^'"]*)$/);
  if (!match) return null;
  return { scope: match[1] as keyof ApiClientScriptVariableKeys, prefix: match[2] || '' };
}

function memberCompletionContext(textBeforeCursor: string): { path: string; prefix: string } | null {
  const match = textBeforeCursor.match(/(?:^|[^\w$])((?:flex|console)(?:\.[A-Za-z_$][\w$]*)*)\.([A-Za-z_$][\w$]*)?$/);
  if (!match) return null;
  return { path: match[1], prefix: match[2] || '' };
}

export function apiClientScriptCompletionsAtPosition(
  source: string,
  position: number,
  phase: ApiClientScriptPhase,
  variableKeys: ApiClientScriptVariableKeys = {},
  explicit = false,
): ApiClientScriptCompletionContext | null {
  const safePosition = Math.max(0, Math.min(position, source.length));
  const before = source.slice(0, safePosition);

  const variable = variableCompletionContext(before);
  if (variable) {
    const items = apiClientScriptVariableKeyCompletions(variable.scope, variable.prefix, variableKeys);
    return items.length > 0 ? { from: safePosition - variable.prefix.length, to: safePosition, items } : null;
  }

  const assertion = assertionCompletionContext(before);
  if (assertion) {
    const items = apiClientScriptMemberCompletions(assertion.path, phase)
      .filter((item) => item.label.toLowerCase().startsWith(assertion.prefix.toLowerCase()));
    return items.length > 0 ? { from: safePosition - assertion.prefix.length, to: safePosition, items } : null;
  }

  const member = memberCompletionContext(before);
  if (member) {
    const items = apiClientScriptMemberCompletions(member.path, phase)
      .filter((item) => item.label.toLowerCase().startsWith(member.prefix.toLowerCase()));
    return items.length > 0 ? { from: safePosition - member.prefix.length, to: safePosition, items } : null;
  }

  const word = before.match(/([A-Za-z_$][\w$]*)$/)?.[1] || '';
  if (!explicit && !word) return null;
  const items = ROOT_SCRIPT_COMPLETIONS.filter((item) => !word || item.label.startsWith(word));
  if (!explicit && items.length === 0) return null;
  return items.length > 0 ? { from: safePosition - word.length, to: safePosition, items: items.map((item) => ({ ...item })) } : null;
}
'''
if 'export interface ApiClientScriptCompletionContext' not in intellisense:
    intellisense += context_code
intellisense_path.write_text(intellisense)

test_path = Path('packages/client/src/utils/api-client-script-intellisense.test.ts')
tests = test_path.read_text()
tests = tests.replace(
    "  apiClientScriptMemberCompletions,\n  apiClientScriptVariableKeyCompletions,",
    "  apiClientScriptCompletionsAtPosition,\n  apiClientScriptMemberCompletions,\n  apiClientScriptVariableKeyCompletions,",
)
context_tests = r'''

  it('resolves dot-triggered, assertion, and explicit completion contexts', () => {
    expect(apiClientScriptCompletionsAtPosition('flex.', 5, 'pre-request')?.items.map((item) => item.label)).toEqual(expect.arrayContaining(['request', 'environment', 'collection', 'variables', 'expect']));
    expect(apiClientScriptCompletionsAtPosition('flex.', 5, 'pre-request')?.items.map((item) => item.label)).not.toEqual(expect.arrayContaining(['response', 'test']));
    expect(apiClientScriptCompletionsAtPosition('flex.', 5, 'tests')?.items.map((item) => item.label)).toEqual(expect.arrayContaining(['response', 'test']));

    const member = apiClientScriptCompletionsAtPosition('flex.request.he', 15, 'pre-request');
    expect(member).toMatchObject({ from: 13, to: 15 });
    expect(member?.items.map((item) => item.label)).toEqual(['headers']);

    expect(apiClientScriptCompletionsAtPosition('flex.expect(value).to.be.', 25, 'tests')?.items.map((item) => item.label)).toEqual(expect.arrayContaining(['above', 'below', 'oneOf', 'ok', 'true', 'false']));
    expect(apiClientScriptCompletionsAtPosition('', 0, 'pre-request', {}, true)?.items.map((item) => item.label)).toEqual(['flex', 'console']);
  });

  it('resolves known variable names at the caret', () => {
    const source = "flex.environment.get('to";
    const completion = apiClientScriptCompletionsAtPosition(source, source.length, 'pre-request', {
      environment: ['token', 'tenant', 'baseUrl'],
    });
    expect(completion).toMatchObject({ from: source.length - 2, to: source.length });
    expect(completion?.items.map((item) => item.label)).toEqual(['token']);
  });
'''
if "resolves dot-triggered, assertion, and explicit completion contexts" not in tests:
    insert = tests.rfind('\n});')
    if insert < 0:
        raise SystemExit('intellisense test suite marker not found')
    tests = tests[:insert] + context_tests + tests[insert:]
test_path.write_text(tests)

index_path = Path('packages/client/src/index.ts')
index = index_path.read_text()
index = index.replace(
    "export { API_CLIENT_SCRIPT_COMPLETION_PATHS, apiClientScriptMemberCompletions, apiClientScriptVariableKeyCompletions } from './utils/api-client-script-intellisense';",
    "export { API_CLIENT_SCRIPT_COMPLETION_PATHS, apiClientScriptCompletionsAtPosition, apiClientScriptMemberCompletions, apiClientScriptVariableKeyCompletions } from './utils/api-client-script-intellisense';",
)
index = index.replace(
    "export type { ApiClientScriptCompletionItem, ApiClientScriptCompletionKind, ApiClientScriptPhase, ApiClientScriptVariableKeys } from './utils/api-client-script-intellisense';",
    "export type { ApiClientScriptCompletionContext, ApiClientScriptCompletionItem, ApiClientScriptCompletionKind, ApiClientScriptPhase, ApiClientScriptVariableKeys } from './utils/api-client-script-intellisense';",
)
index_path.write_text(index)
