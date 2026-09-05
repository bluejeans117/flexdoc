from pathlib import Path

path = Path('packages/client/src/components/ApiClientHistoryPage.test.tsx')
text = path.read_text()

marker = "import { fireEvent, render, screen, waitFor } from '@testing-library/react';\n"
if marker not in text:
    raise SystemExit('testing-library import marker not found')
text = text.replace(marker, marker + "import userEvent from '@testing-library/user-event';\n", 1)

old = "  it('filters history and shows captured response details', async () => {\n    render(<ApiClientHistoryPage"
new = "  it('filters history and shows captured response details', async () => {\n    const user = userEvent.setup();\n    render(<ApiClientHistoryPage"
if old not in text:
    raise SystemExit('search test marker not found')
text = text.replace(old, new, 1)

old = "    fireEvent.change(screen.getByLabelText('Search history'), { target: { value: 'login' } });\n    await waitFor(() => expect(screen.queryByText('{\"pets\":[]}')).not.toBeInTheDocument());"
new = "    await user.type(screen.getByLabelText('Search history'), 'login');\n    expect(screen.getByLabelText('Search history')).toHaveValue('login');\n    await waitFor(() => expect(screen.queryByText('{\"pets\":[]}')).not.toBeInTheDocument());"
if old not in text:
    raise SystemExit('search interaction marker not found')
text = text.replace(old, new, 1)

old = "  it('filters failed requests independently of method', async () => {\n    render(<ApiClientHistoryPage"
new = "  it('filters failed requests independently of method', async () => {\n    const user = userEvent.setup();\n    render(<ApiClientHistoryPage"
if old not in text:
    raise SystemExit('outcome test marker not found')
text = text.replace(old, new, 1)

old = "    fireEvent.change(screen.getByLabelText('History outcome filter'), { target: { value: 'failed' } });\n    await waitFor(() => expect(screen.queryAllByText('https://api.example.test/pets')).toHaveLength(0));"
new = "    await user.selectOptions(screen.getByLabelText('History outcome filter'), 'failed');\n    expect(screen.getByLabelText('History outcome filter')).toHaveValue('failed');\n    await waitFor(() => expect(screen.queryAllByText('https://api.example.test/pets')).toHaveLength(0));"
if old not in text:
    raise SystemExit('outcome interaction marker not found')
text = text.replace(old, new, 1)

path.write_text(text)
