import { ApiClientWorkspace } from '@prauga/flexdoc-client';

export function App() {
  return (
    <main className="shell">
      <header className="hero">
        <div>
          <p className="eyebrow">FlexDoc</p>
          <h1>API Client</h1>
          <p>
            A standalone API development workspace powered by the same canonical request engine as FlexDoc Try It.
            Collections, folders, saved requests, named environments and request scripts persist locally in this browser.
          </p>
          <p>
            Create an environment with <code>baseUrl</code> set to <code>https://jsonplaceholder.typicode.com</code>,
            then send the templated request below. The pre-request script supplies <code>postId</code> and the test script
            validates the response.
          </p>
        </div>
      </header>

      <ApiClientWorkspace
        persistenceKey="flexdoc-api-client-example"
        initialRequest={{
          method: 'GET',
          url: '{{baseUrl}}/posts/{{postId}}',
          query: [],
          headers: [{ key: 'Accept', value: 'application/json', enabled: true }],
          auth: { type: 'none' },
        }}
        initialScripts={{
          preRequest: "pm.variables.set('postId', '1');\nconsole.log('requesting post', pm.variables.get('postId'));",
          tests: "pm.test('status is 200', () => pm.expect(pm.response.code).to.equal(200));\npm.test('post id is 1', () => pm.expect(pm.response.json()).to.have.property('id', 1));",
        }}
      />
    </main>
  );
}
