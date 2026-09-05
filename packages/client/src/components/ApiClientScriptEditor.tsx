import React, { useEffect, useRef } from 'react';
import { basicSetup, EditorView } from 'codemirror';
import type { Completion, CompletionContext, CompletionResult } from '@codemirror/autocomplete';
import { completionPath, javascript, javascriptLanguage } from '@codemirror/lang-javascript';
import {
  apiClientScriptMemberCompletions,
  apiClientScriptVariableKeyCompletions,
} from '../utils/api-client-script-intellisense';
import type {
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

function completionType(item: ApiClientScriptCompletionItem): Completion['type'] {
  if (item.kind === 'method' || item.kind === 'function') return 'function';
  if (item.kind === 'variable') return 'variable';
  return 'property';
}

function toCompletion(item: ApiClientScriptCompletionItem): Completion {
  return {
    label: item.label,
    type: completionType(item),
    detail: item.signature,
    info: item.documentation,
    boost: item.kind === 'variable' ? 20 : 10,
  };
}

function assertionCompletion(textBeforeCursor: string, phase: ApiClientScriptPhase): { path: string; prefix: string } | null {
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
  return phase === 'tests' || phase === 'pre-request' ? null : null;
}

function variableKeyCompletion(
  textBeforeCursor: string,
  keys: ApiClientScriptVariableKeys,
): { scope: keyof ApiClientScriptVariableKeys; prefix: string } | null {
  const match = textBeforeCursor.match(/flex\.(environment|collection|variables)\.(?:get|has|set|unset)\(\s*['"]([^'"]*)$/);
  if (!match) return null;
  return { scope: match[1] as keyof ApiClientScriptVariableKeys, prefix: match[2] || '' };
}

function createCompletionSource(phase: ApiClientScriptPhase, variableKeys: ApiClientScriptVariableKeys) {
  return (context: CompletionContext): CompletionResult | null => {
    const textBeforeCursor = context.state.sliceDoc(0, context.pos);
    const variable = variableKeyCompletion(textBeforeCursor, variableKeys);
    if (variable) {
      const options = apiClientScriptVariableKeyCompletions(variable.scope, variable.prefix, variableKeys).map(toCompletion);
      return options.length > 0 ? { from: context.pos - variable.prefix.length, options, validFor: /^[\w.-]*$/ } : null;
    }

    const assertion = assertionCompletion(textBeforeCursor, phase);
    if (assertion) {
      const options = apiClientScriptMemberCompletions(assertion.path, phase).map(toCompletion);
      return { from: context.pos - assertion.prefix.length, options, validFor: /^\w*$/ };
    }

    const path = completionPath(context);
    if (!path) return null;
    if (path.path.length === 0) {
      if (!context.explicit && !'flex'.startsWith(path.name) && !'console'.startsWith(path.name)) return null;
      return {
        from: context.pos - path.name.length,
        options: [
          { label: 'flex', type: 'namespace', detail: 'FlexDoc scripting API', info: 'Request, response, variables, assertions, and test helpers.' },
          { label: 'console', type: 'namespace', detail: 'Script console', info: 'Captured log, info, warn, and error output.' },
        ],
        validFor: /^\w*$/,
      };
    }

    const memberPath = path.path.join('.');
    const options = apiClientScriptMemberCompletions(memberPath, phase).map(toCompletion);
    if (options.length === 0) return null;
    return { from: context.pos - path.name.length, options, validFor: /^\w*$/ };
  };
}

export const ApiClientScriptEditor: React.FC<ApiClientScriptEditorProps> = ({
  ariaLabel,
  value,
  onChange,
  phase,
  theme = 'light',
  variableKeys = {},
}) => {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const viewRef = useRef<EditorView | null>(null);
  const onChangeRef = useRef(onChange);
  const variableSignature = JSON.stringify(variableKeys);

  useEffect(() => { onChangeRef.current = onChange; }, [onChange]);

  useEffect(() => {
    if (!hostRef.current) return undefined;
    const dark = theme === 'dark';
    const completionSource = createCompletionSource(phase, variableKeys);
    const editorTheme = EditorView.theme({
      '&': {
        border: `1px solid ${dark ? '#374151' : '#d1d5db'}`,
        borderRadius: '0.375rem',
        backgroundColor: dark ? '#111827' : '#ffffff',
        color: dark ? '#f3f4f6' : '#111827',
        fontSize: '12px',
      },
      '&.cm-focused': { outline: `2px solid ${dark ? '#60a5fa' : '#2563eb'}`, outlineOffset: '-1px' },
      '.cm-scroller': { minHeight: '10rem', maxHeight: '24rem', overflow: 'auto', fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace' },
      '.cm-content': { minHeight: '10rem', padding: '8px 0' },
      '.cm-gutters': { backgroundColor: dark ? '#111827' : '#f9fafb', color: dark ? '#9ca3af' : '#6b7280', borderRightColor: dark ? '#374151' : '#e5e7eb' },
      '.cm-activeLine, .cm-activeLineGutter': { backgroundColor: dark ? 'rgba(55, 65, 81, 0.4)' : 'rgba(243, 244, 246, 0.8)' },
      '.cm-tooltip': { zIndex: '50', borderColor: dark ? '#4b5563' : '#d1d5db', backgroundColor: dark ? '#1f2937' : '#ffffff', color: dark ? '#f3f4f6' : '#111827' },
      '.cm-tooltip-autocomplete > ul > li[aria-selected]': { backgroundColor: dark ? '#1d4ed8' : '#dbeafe', color: dark ? '#ffffff' : '#111827' },
    }, { dark });

    const view = new EditorView({
      parent: hostRef.current,
      doc: value,
      extensions: [
        basicSetup,
        javascript(),
        javascriptLanguage.data.of({ autocomplete: completionSource }),
        EditorView.contentAttributes.of({ 'aria-label': ariaLabel, spellcheck: 'false', 'data-api-client-script-phase': phase }),
        EditorView.updateListener.of((update) => {
          if (update.docChanged) onChangeRef.current(update.state.doc.toString());
        }),
        editorTheme,
      ],
    });
    viewRef.current = view;
    return () => {
      view.destroy();
      if (viewRef.current === view) viewRef.current = null;
    };
  // variableSignature intentionally recreates the completion source only when known keys change.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ariaLabel, phase, theme, variableSignature]);

  useEffect(() => {
    const view = viewRef.current;
    if (!view) return;
    const current = view.state.doc.toString();
    if (current === value) return;
    view.dispatch({ changes: { from: 0, to: current.length, insert: value } });
  }, [value]);

  return <div>
    <div ref={hostRef} data-testid={`${ariaLabel}-editor`} />
    <div className={`mt-1 text-[11px] ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
      IntelliSense: type <code>flex.</code> or press Ctrl+Space. Known variable names are suggested inside variable helpers.
    </div>
  </div>;
};
