from pathlib import Path

path = Path('packages/client/src/components/ApiClientHistoryPage.test.tsx')
text = path.read_text()
text = text.replace(
    "import { fireEvent, render, screen } from '@testing-library/react';",
    "import { fireEvent, render, screen, waitFor } from '@testing-library/react';",
    1,
)
text = text.replace(
    "  it('filters history and shows captured response details', () => {",
    "  it('filters history and shows captured response details', async () => {",
    1,
)
text = text.replace(
    "    expect(screen.getByText('https://api.example.test/login')).toBeInTheDocument();\n    expect(screen.queryByText('{\"pets\":[]}')).not.toBeInTheDocument();",
    "    await waitFor(() => expect(screen.queryByText('{\"pets\":[]}')).not.toBeInTheDocument());\n    expect(screen.getAllByText('https://api.example.test/login').length).toBeGreaterThan(0);",
    1,
)
text = text.replace(
    "  it('filters failed requests independently of method', () => {",
    "  it('filters failed requests independently of method', async () => {",
    1,
)
text = text.replace(
    "    expect(screen.getByText('https://api.example.test/login')).toBeInTheDocument();\n    expect(screen.queryByText('https://api.example.test/pets')).not.toBeInTheDocument();",
    "    await waitFor(() => expect(screen.queryAllByText('https://api.example.test/pets')).toHaveLength(0));\n    expect(screen.getAllByText('https://api.example.test/login').length).toBeGreaterThan(0);",
    1,
)
path.write_text(text)
