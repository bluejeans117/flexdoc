# Framework coverage roadmap: FlexDoc 2.2.5 → 2.3.0

FlexDoc keeps one canonical browser renderer and thin language/framework hosts. Product release numbers track the overall FlexDoc line; ecosystem packages continue to use independent semantic versions.

## Stacked implementation

| FlexDoc slice | Coverage | Stack PR |
| --- | --- | --- |
| **2.2.5** | ASP.NET Core | #29 (already merged) |
| **2.2.6** | framework-neutral JVM, Jakarta REST, Spring refactor, Quarkus, Micronaut, Guice/Governator path | #31 |
| **2.2.7** | Python WSGI, Flask, Django while retaining ASGI/FastAPI | #32 |
| **2.2.8** | generic PHP host, Laravel, Symfony | #33 |
| **2.2.9** | Ruby host, Rack, Rails | #34 |
| **2.3.0** | Hono, Gin/Chi/Echo/Fiber, Actix Web, Ktor, Plug/Phoenix and coverage closure | final stacked PR |

The open stack is implementation work, not a released version. Do not mark a slice shipped until its PR is explicitly approved, merged, and its relevant packages are published.

## Architecture rule

Do not create a renderer implementation per framework. Each ecosystem exposes the smallest useful host abstraction and reuses the canonical standalone renderer.

- **.NET:** ASP.NET Core endpoint routing is the native boundary.
- **JVM:** `flexdoc-jvm` owns renderer hosting. Spring and Jakarta REST are transports; Quarkus consumes Jakarta; Micronaut, Guice/Governator, and Ktor map the neutral response.
- **Python:** `FlexDocHost` owns renderer hosting; ASGI and WSGI are transports; FastAPI, Flask, and Django remain thin integrations.
- **PHP:** `FlexDocHost` owns renderer hosting; Laravel and Symfony translate/register native responses/routes.
- **Ruby:** `Prauga::FlexDoc::Host` owns renderer hosting; Rack is the transport and Rails mounts the same Rack app.
- **Go:** `net/http` remains the adapter. Gin, Chi, and Echo compose it directly; Fiber v3 now also adapts standard `net/http` handlers directly, so no Fiber dependency enters the FlexDoc Go module.
- **Rust:** Axum and Actix Web have separate transport crates but package byte-identical canonical renderer assets and equivalent host behavior.
- **Elixir:** Plug is the package/runtime boundary; Phoenix forwards to the same Plug.
- **Hono:** a dependency-free Hono-shaped helper is exposed from the existing Node backend package.

## 2.3.0 definition of done

The stack must provide documented and CI/compile/smoke-tested paths for:

- [x] JavaScript/TypeScript: Express, Fastify, NestJS, Hono
- [x] C#/.NET: ASP.NET Core
- [x] JVM: Spring Boot, Jakarta/JAX-RS, Quarkus, Micronaut, Ktor, Guice/Governator-style applications
- [x] Python: FastAPI/Starlette/ASGI, Flask/WSGI, Django
- [x] PHP: Laravel, Symfony
- [x] Ruby: Rack, Rails
- [x] Go: `net/http`, Gin, Chi, Echo, Fiber
- [x] Rust: Axum, Actix Web
- [x] Elixir: Plug, Phoenix

The checkboxes describe what is implemented in the **stacked branches**, not what is already merged/released. Final release readiness additionally requires all stacked PR checks green, explicit merge approval, coordinated package publication, and the npm 2.3.0 release-preparation bump.
