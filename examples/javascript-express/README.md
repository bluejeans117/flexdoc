# Express + FlexDoc

This example serves the shared OpenAPI 3.1 feature showcase with Express and `@prauga/flexdoc-backend`. The API includes representative JSON, form, upload, parameter, authentication-metadata, multi-server, Try It, custom-server, API Client handoff, and code-sample flows.

```bash
npm install
npm start
```

Open `http://localhost:3000/docs`.

The FlexDoc dependency is pinned to published `2.8.0` and resolves directly from npm. Repository CI also installs the backend package built from the current commit and boots `/docs` to verify source compatibility.
