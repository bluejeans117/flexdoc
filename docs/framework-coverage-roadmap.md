# Framework coverage roadmap: FlexDoc 2.2.5 → 2.3.0

FlexDoc keeps one canonical browser renderer and thin language/framework hosts. Product release numbers track the overall FlexDoc line; ecosystem packages continue to use independent semantic versions where appropriate.

## Release ladder

| FlexDoc release | Coverage slice | Primary deliverables |
| --- | --- | --- |
| **2.2.5** | .NET | ASP.NET Core adapter, example, CI/package validation, NuGet-ready package — implemented in #29 |
| **2.2.6** | JVM foundation | framework-neutral Java host, Jakarta REST/JAX-RS transport, Spring Boot refactor, Quarkus and Micronaut runtime coverage, and Guice/Governator-style neutral-host path — in progress in #31 |
| **2.2.7** | Python breadth | add WSGI support plus first-class Flask and Django integrations while retaining ASGI/FastAPI |
| **2.2.8** | PHP | generic PHP host plus Laravel integration; Symfony compatibility/integration on the shared core |
| **2.2.9** | Ruby | Rack adapter plus Rails integration; keep Sinatra/other Rack applications compatible |
| **2.3.0** | Coverage completion | Rust Actix Web, Kotlin Ktor, Go Fiber, Elixir Plug/Phoenix, Hono integration/example, plus Go Gin/Chi/Echo and other lightweight framework examples/documentation |

## 2.2.6 JVM design

The Java family is coordinated at source version `0.4.0`:

- `com.prauga.flexdoc:flexdoc-jvm` — Java 17+ framework-neutral host; owns the host HTML, cache policy, fingerprinting, and canonical renderer assets.
- `com.prauga.flexdoc:flexdoc-jaxrs` — Jakarta REST/JAX-RS response transport over `flexdoc-jvm`.
- `com.prauga.flexdoc:flexdoc-spring-boot-starter` — existing Spring Boot integration refactored to delegate renderer hosting to `flexdoc-jvm`.

The coverage proof in #31 includes a Spring regression build, a Quarkus REST runtime test, a Micronaut runtime test, and a Guice/JDK HTTP smoke test. Governator-style services use the Guice path: bind `FlexDocHost` in the existing object graph and translate `FlexDocHttpResponse` through the service's HTTP stack.

## Architecture rule

Do not create a renderer implementation per framework. Each ecosystem should expose the smallest native host abstraction possible and reuse the canonical standalone renderer.

Prefer one framework-neutral package per language/runtime, then thin helpers:

- **.NET:** ASP.NET Core endpoint routing is the native host boundary.
- **JVM:** `flexdoc-jvm` is the native host boundary. Spring Boot and Jakarta REST are transports; Quarkus consumes the Jakarta path; Micronaut and Guice/Governator-style services map the neutral response through their native HTTP stack. Ktor remains a 2.3.0 Kotlin proof path.
- **Python:** one package supporting ASGI and WSGI, with FastAPI/Flask/Django helpers.
- **PHP:** generic PHP package, then Laravel/Symfony integration sugar.
- **Ruby:** Rack first, Rails helper second.
- **Go:** keep `net/http` as the main adapter; add Fiber only because its `fasthttp` stack is outside `net/http`; other routers should use examples rather than new modules.
- **Rust:** keep renderer hosting shared conceptually across Axum and Actix rather than diverging behavior.
- **Elixir:** Plug is the reusable boundary; Phoenix consumes the Plug integration.

## Definition of done for 2.3.0

By 2.3.0 the documented backend matrix should include, at minimum:

- JavaScript/TypeScript: Express, Fastify, NestJS, Hono
- C#/.NET: ASP.NET Core
- JVM: Spring Boot, Jakarta/JAX-RS, Quarkus, Micronaut, Ktor-compatible path, Guice/Governator-style applications through the neutral host layer
- Python: FastAPI/Starlette/ASGI, Flask/WSGI, Django
- PHP: Laravel, Symfony
- Ruby: Rack, Rails
- Go: `net/http`, Gin, Chi, Echo, Fiber
- Rust: Axum, Actix Web
- Elixir: Plug, Phoenix

Every first-class integration must have package/build validation and at least one runnable or smoke-tested example. Frameworks that already compose cleanly with a neutral host abstraction should prefer examples over package fragmentation.
