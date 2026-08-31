# Prauga package migration

FlexDoc is moving from the original personal `bluejeans` package namespace to Prauga. New releases should use the Prauga identities below.

| Ecosystem | Previous identity | Prauga identity |
| --- | --- | --- |
| npm renderer/client | `@bluejeans/flexdoc-client` | `@prauga/flexdoc-client` |
| npm backend adapters | `@bluejeans/flexdoc-backend` | `@prauga/flexdoc-backend` |
| npm core | `@bluejeans/flexdoc-core` | `@prauga/flexdoc-core` |
| npm CLI | `@bluejeans/flexdoc-cli` | `@prauga/flexdoc-cli` |
| Maven | `io.github.bluejeans117.flexdoc:flexdoc-spring-boot-starter` | `com.prauga.flexdoc:flexdoc-spring-boot-starter` |
| PyPI | — | `prauga-flexdoc` |
| crates.io | — | `prauga-flexdoc-axum` |
| Go module | — | `github.com/prauga/flexdoc/adapters/go` |

## npm deprecation policy

The old npm packages are deprecated only after their matching `@prauga/*` replacements are publicly installable. They are not unpublished.

The repository includes a guarded helper:

```bash
npm run deprecate:bluejeans
npm run deprecate:bluejeans -- --apply
```

The first command is a dry run. `--apply` requires an authenticated npm owner session, verifies the replacement package exists, and then applies the migration message to every published version of the old package.

Equivalent explicit commands are:

```bash
npm deprecate '@bluejeans/flexdoc-client@*' 'This package has moved to @prauga/flexdoc-client. Please migrate to the @prauga scope; @bluejeans/flexdoc-client is no longer maintained.'
npm deprecate '@bluejeans/flexdoc-backend@*' 'This package has moved to @prauga/flexdoc-backend. Please migrate to the @prauga scope; @bluejeans/flexdoc-backend is no longer maintained.'
npm deprecate '@bluejeans/flexdoc-core@*' 'This package has moved to @prauga/flexdoc-core. Please migrate to the @prauga scope; @bluejeans/flexdoc-core is no longer maintained.'
npm deprecate '@bluejeans/flexdoc-cli@*' 'This package has moved to @prauga/flexdoc-cli. Please migrate to the @prauga scope; @bluejeans/flexdoc-cli is no longer maintained.'
```

There is no analogous Maven deprecation step in this migration. The new Prauga Maven coordinate is a new artifact line.

## Recommended release order

1. Move/confirm the source repository at `prauga/flexdoc` and update registry Trusted Publisher relationships to that repository.
2. Publish `@prauga/flexdoc-client@2.1.0` and `@prauga/flexdoc-backend@2.1.0` from `js/v2.1.0`.
3. Publish `@prauga/flexdoc-core@0.1.0` from `core/v0.1.0`.
4. Publish `@prauga/flexdoc-cli@0.1.0` from `cli/v0.1.0` after the client exists on npm.
5. Deprecate the published `@bluejeans/*` packages using the guarded helper.
6. Publish `prauga-flexdoc` from `python/v0.1.0`, `prauga-flexdoc-axum` from `rust/v0.1.0`, and the Go module using `adapters/go/v0.1.0`.
7. Verify the Maven Central namespace `com.prauga.flexdoc`, then publish `com.prauga.flexdoc:flexdoc-spring-boot-starter:0.2.0` from `java/v0.2.0`.

## Registry setup outside Git

Repository code cannot establish registry ownership on its own. Before the corresponding first release:

- npm: create/claim the `@prauga` packages and configure npm Trusted Publishers for the exact workflow filenames after the repository is under Prauga.
- PyPI: configure a Trusted Publisher for project `prauga-flexdoc` and workflow `publish-python.yml` (a pending publisher can bootstrap a new project).
- crates.io: bootstrap the crate if required, then configure its trusted publisher for `publish-rust.yml`.
- Maven Central: verify the `com.prauga.flexdoc` namespace and configure Central credentials/signing secrets.
- Go: no registry upload is required; the public submodule tag is the release.
