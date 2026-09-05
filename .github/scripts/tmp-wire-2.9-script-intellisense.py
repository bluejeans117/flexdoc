from pathlib import Path

api_path = Path('packages/client/src/components/ApiClient.tsx')
api = api_path.read_text()
import_marker = "import { OAuthEditor } from './ApiClientAuthEditor';\n"
if "ApiClientScriptEditor" not in api:
    if import_marker not in api:
        raise SystemExit('ApiClient import marker not found')
    api = api.replace(import_marker, import_marker + "import { ApiClientScriptEditor } from './ApiClientScriptEditor';\n", 1)

section = api.index("<section className='space-y-3 border-t pt-4' aria-labelledby='api-client-scripts-heading'>")
start = api.index("        <div className='grid gap-3 xl:grid-cols-2'>", section)
end_marker = "        </div>\n      </section>"
end = api.index(end_marker, start)
smart_grid = """        <div className='grid gap-3 xl:grid-cols-2'>
          <label className='text-sm font-medium'>Pre-request script
            <div className='mt-1'>
              <ApiClientScriptEditor
                ariaLabel='Pre-request script'
                phase='pre-request'
                theme={theme}
                value={scripts.preRequest}
                onChange={(value) => setScripts((current) => ({ ...current, preRequest: value }))}
                variableKeys={{
                  environment: Object.keys(environmentVariables),
                  collection: Object.keys(collectionVariables),
                  variables: Object.keys(variables),
                }}
              />
            </div>
          </label>
          <label className='text-sm font-medium'>Tests
            <div className='mt-1'>
              <ApiClientScriptEditor
                ariaLabel='Tests script'
                phase='tests'
                theme={theme}
                value={scripts.tests}
                onChange={(value) => setScripts((current) => ({ ...current, tests: value }))}
                variableKeys={{
                  environment: Object.keys(environmentVariables),
                  collection: Object.keys(collectionVariables),
                  variables: Object.keys(variables),
                }}
              />
            </div>
          </label>
"""
api = api[:start] + smart_grid + api[end:]
api_path.write_text(api)

index_path = Path('packages/client/src/index.ts')
index = index_path.read_text()
component_marker = "export type { ApiClientExecutionResult, ApiClientProps } from './components/ApiClient';\n"
component_exports = "export { ApiClientScriptEditor } from './components/ApiClientScriptEditor';\nexport type { ApiClientScriptEditorProps } from './components/ApiClientScriptEditor';\n"
if component_exports not in index:
    if component_marker not in index:
        raise SystemExit('index component export marker not found')
    index = index.replace(component_marker, component_marker + component_exports, 1)

scripting_marker = "export { cloneApiClientScripts, EMPTY_API_CLIENT_SCRIPTS, runApiClientScript } from './utils/api-client-scripting';\n"
intellisense_exports = "export { API_CLIENT_SCRIPT_COMPLETION_PATHS, apiClientScriptMemberCompletions, apiClientScriptVariableKeyCompletions } from './utils/api-client-script-intellisense';\nexport type { ApiClientScriptCompletionItem, ApiClientScriptCompletionKind, ApiClientScriptPhase, ApiClientScriptVariableKeys } from './utils/api-client-script-intellisense';\n"
if intellisense_exports not in index:
    if scripting_marker not in index:
        raise SystemExit('index scripting export marker not found')
    index = index.replace(scripting_marker, scripting_marker + intellisense_exports, 1)
index_path.write_text(index)
