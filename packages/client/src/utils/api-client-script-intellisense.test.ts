import {
  API_CLIENT_SCRIPT_COMPLETION_PATHS,
  apiClientScriptMemberCompletions,
  apiClientScriptVariableKeyCompletions,
} from './api-client-script-intellisense';
import { runApiClientScript } from './api-client-scripting';

const expressionForPath: Record<string, string> = {
  flex: 'flex',
  'flex.request': 'flex.request',
  'flex.request.headers': 'flex.request.headers',
  'flex.request.body': 'flex.request.body',
  'flex.response': 'flex.response',
  'flex.response.headers': 'flex.response.headers',
  'flex.environment': 'flex.environment',
  'flex.collection': 'flex.collection',
  'flex.variables': 'flex.variables',
  'flex.expect.to': 'flex.expect(1).to',
  'flex.expect.to.have': 'flex.expect({ value: 1 }).to.have',
  'flex.expect.to.be': 'flex.expect(1).to.be',
  console: 'console',
};

function runtimeSurfaceScript(): string {
  return Object.entries(API_CLIENT_SCRIPT_COMPLETION_PATHS)
    .map(([path, members]) => {
      const expression = expressionForPath[path];
      if (!expression) throw new Error(`Missing runtime expression for ${path}`);
      return members.map((member) => `if (!(${JSON.stringify(member.label)} in ${expression})) throw new Error(${JSON.stringify(`Missing ${path}.${member.label}`)});`).join('\n');
    })
    .join('\n');
}

describe('api-client-script-intellisense', () => {
  it('keeps response and test helpers out of pre-request completion', () => {
    const preRequest = apiClientScriptMemberCompletions('flex', 'pre-request').map((item) => item.label);
    const tests = apiClientScriptMemberCompletions('flex', 'tests').map((item) => item.label);

    expect(preRequest).toEqual(expect.arrayContaining(['request', 'environment', 'collection', 'variables', 'expect']));
    expect(preRequest).not.toContain('response');
    expect(preRequest).not.toContain('test');
    expect(tests).toEqual(expect.arrayContaining(['request', 'response', 'environment', 'collection', 'variables', 'expect', 'test']));
    expect(apiClientScriptMemberCompletions('flex.response', 'pre-request')).toEqual([]);
    expect(apiClientScriptMemberCompletions('flex.response', 'tests').map((item) => item.label)).toEqual(expect.arrayContaining(['code', 'status', 'responseTime', 'headers', 'text', 'json']));
  });

  it('describes request, header, variable, and assertion members with signatures', () => {
    expect(apiClientScriptMemberCompletions('flex.request.headers', 'pre-request')).toEqual(expect.arrayContaining([
      expect.objectContaining({ label: 'get', signature: 'get(name: string): string | undefined' }),
      expect.objectContaining({ label: 'set', signature: 'set(name: string, value: unknown): void' }),
      expect.objectContaining({ label: 'remove', signature: 'remove(name: string): void' }),
    ]));
    expect(apiClientScriptMemberCompletions('flex.environment', 'pre-request').map((item) => item.label)).toEqual(['get', 'has', 'set', 'unset', 'replaceIn']);
    expect(apiClientScriptMemberCompletions('flex.expect.to', 'tests').map((item) => item.label)).toEqual(['equal', 'eql', 'include', 'match', 'have', 'be']);
    expect(apiClientScriptMemberCompletions('flex.expect.to.be', 'tests').map((item) => item.label)).toEqual(['above', 'below', 'oneOf', 'ok', 'true', 'false']);
  });

  it('suggests known variable keys by scope and prefix without duplicates', () => {
    const keys = {
      environment: ['baseUrl', 'token', 'token'],
      collection: ['baseUrl', 'petId'],
      variables: ['baseUrl', 'petId', 'token'],
    };
    expect(apiClientScriptVariableKeyCompletions('environment', 'to', keys).map((item) => item.label)).toEqual(['token']);
    expect(apiClientScriptVariableKeyCompletions('collection', '', keys).map((item) => item.label)).toEqual(['baseUrl', 'petId']);
    expect(apiClientScriptVariableKeyCompletions('variables', 'p', keys)[0]).toMatchObject({ label: 'petId', kind: 'variable' });
  });

  it('keeps the completion catalogue aligned with the actual scripting runtime', async () => {
    const result = await runApiClientScript({
      script: runtimeSurfaceScript(),
      phase: 'tests',
      draft: { method: 'GET', url: 'https://api.example.test', headers: [], query: [] },
      variables: { effective: 'value' },
      collectionVariables: { collection: 'value' },
      environmentVariables: { environment: 'value' },
      response: {
        status: 200,
        statusText: 'OK',
        headers: [['content-type', 'application/json']],
        body: '{"ok":true}',
        responseTime: 12,
      },
    });

    expect(result.error).toBeUndefined();
  });
});
