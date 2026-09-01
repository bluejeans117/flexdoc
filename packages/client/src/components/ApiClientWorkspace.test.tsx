import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { ApiClientWorkspace } from './ApiClientWorkspace';

describe('ApiClientWorkspace', () => {
  it('saves and reloads requests inside a local collection', async () => {
    const user = userEvent.setup();
    render(<ApiClientWorkspace
      persistenceKey={false}
      initialRequest={{ method: 'GET', url: 'https://api.example.test/pets' }}
    />);

    await waitFor(() => expect(screen.getByLabelText('Request URL')).toHaveValue('https://api.example.test/pets'));

    await user.type(screen.getByLabelText('Saved request name'), 'List pets');
    await user.click(screen.getByRole('button', { name: 'Save request' }));

    expect(await screen.findByRole('button', { name: 'Load saved request List pets' })).toBeInTheDocument();

    const urlInput = screen.getByLabelText('Request URL');
    await user.clear(urlInput);
    await user.type(urlInput, 'https://api.example.test/owners');
    await waitFor(() => expect(screen.getByLabelText('Request URL')).toHaveValue('https://api.example.test/owners'));

    await user.click(screen.getByRole('button', { name: 'Load saved request List pets' }));
    await waitFor(() => expect(screen.getByLabelText('Request URL')).toHaveValue('https://api.example.test/pets'));
  });

  it('creates folders and saves requests into them', async () => {
    const user = userEvent.setup();
    render(<ApiClientWorkspace
      persistenceKey={false}
      initialRequest={{ method: 'POST', url: 'https://api.example.test/pets' }}
    />);

    await user.type(screen.getByLabelText('New folder name'), 'Pets');
    await user.click(screen.getByRole('button', { name: 'Add folder' }));
    expect(await screen.findByRole('button', { name: 'Delete folder Pets' })).toBeInTheDocument();

    await user.type(screen.getByLabelText('Saved request name'), 'Create pet');
    await user.click(screen.getByRole('button', { name: 'Save request' }));

    expect(await screen.findByRole('button', { name: 'Load saved request Create pet' })).toBeInTheDocument();
    expect(screen.getByLabelText('Saved request folder')).toHaveDisplayValue('Pets');
  });
});
