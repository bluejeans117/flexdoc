import React, { useEffect, useRef } from 'react';
import {
  autocompletion,
  completionKeymap,
} from '@codemirror/autocomplete';
import type { Completion, CompletionContext, CompletionResult } from '@codemirror/autocomplete';
import {
  drawSelection,
  EditorView,
  highlightActiveLine,
  highlightActiveLineGutter,
  keymap,
  lineNumbers,
} from '@codemirror/view';
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

function assertionCompletion(textBeforeCursor: string): { path: string; prefix: string } | null {
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

function variableKeyCompletion(
  textBeforeCursor: string,
): { scope: keyof ApiClientScriptVariableKeys; prefix: string } | null {
  const match = textBeforeCursor.match(/flex\.(environment|collection|variables)\.(?:get|has|set|unset)\(\s*['"]([^'"]*)$/);
  if (!match) return null;
  return { scope: match[1] as keyof ApiClientScriptVariableKeys, prefix: match[2] || '' };
}

function memberCompletion(textBeforeCursor: string): { path: string; prefix: string } | null {
  const match = textBeforeCursor.match(/(?:^|[^\w$])((?:flex|console)(?:\.[A-Za-z_$][\w$]*)*)\.([A-Za-z_$][\w$]*)?$/);
  if (!match) return null;
  return { path: match[1], prefix: match[2] || '' };
}

function createCompletionSource(phase: ApiClientScriptPhase, variableKeys: ApiClientScriptVariableKeys) {
  return (context: CompletionContext): CompletionResult | null => {
    const textBeforeCursor = context.state.sliceDoc(0, context.pos);
    const variable = variableKeyCompletion(textBeforeCursor);
    if (variable) {
      const options = apiClientScriptVariableKeyCompletions(variable.scope, variable.prefix, variableKeys).map(toCompletion);
      return options.length > 0 ? { from: context.pos - variable.prefix.length, options, validFor: /^[\w.-]*$/ } : null;
    }

    const assertion = assertionCompletion(textBeforeCursor);
    if (assertion) {
      const options = apiClientScriptMemberCompletions(assertion.path, phase).map(toCompletion);
      return options.length > 0 ? { from: context.pos - assertion.prefix.length, options, validFor: /^\w*$/ } : null;
    }

    const member = memberCompletion(textBeforeCursor);
    if (member) {
      const options = apiClientScriptMemberCompletions(member.path, phase).map(toCompletion);
      return options.length > 0 ? { from: context.pos - member.prefix.length, options, validFor: /^\w*$/ } : null;
    }

    const word = context.matchBefore(/[A-Za-z_$][\w$]*/);
    if (!word) return null;
    if (!context.explicit && !'flex'.startsWith(word.text) && !'console'.startsWith(word.text)) return null;
    return {
      from: word.from,
      options: [
        { label: 'flex', type: 'namespace', detail: 'FlexDoc scripting API', info: 'Request, response, variables, assertions, and test helpers.' },
        { label: 'console', type: 'namespace', detail: 'Script console', info: 'Captured log, info, warn, and error output.' },
      ],
      validFor: /^\w*$/,
    };
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
        lineNumbers(),
        highlightActiveLineGutter(),
        drawSelection(),
        highlightActiveLine(),
        EditorView.lineWrapping,
        keymap.of(completionKeymap),
        autocompletion({ override: [completionSource], activateOnTyping: true, maxRenderedOptions: 30 }),
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
