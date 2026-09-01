import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ApiClientWorkspace } from './ApiClientWorkspace';

describe('ApiClientWorkspace', () => {
  it('saves and reloads requests inside a local collection', async () => {
    render(<ApiClientWorkspace
      persistenceKey={false}
      initialRequest={{ method: 'GET', url: 'https://api.example.test/pets' }}
    />);

    await waitFor(() => expect(screen.getByLabelText('Request URL')).toHaveValue('https://api.example.test/pets'));

    fireEvent.change(screen.getByLabelText('Saved request name'), { target: { value: 'List pets' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save request' }));

    expect(screen.getByRole('button', { name: 'Load saved request List pets' })).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Request URL'), { target: { value: 'https://api.example.test/owners' } });
    await waitFor(() => expect(screen.getByLabelText('Request URL')).toHaveValue('https://api.example.test/owners'));

    fireEvent.click(screen.getByRole('button', { name: 'Load saved request List pets' }));
    expect(screen.getByLabelText('Request URL')).toHaveValue('https://api.example.test/pets');
  });

  it('creates folders and saves requests into them', async () => {
    render(<ApiClientWorkspace
      persistenceKey={false}
      initialRequest={{ method: 'POST', url: 'https://api.example.test/pets' }}
    />);

    fireEvent.change(screen.getByLabelText('New folder name'), { target: { value: 'Pets' } });
    fireEvent.click(screen.getByRole('button', { name: 'Add folder' }));
    expect(screen.getByRole('button', { name: 'Delete folder Pets' })).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Saved request name'), { target: { value: 'Create pet' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save request' }));

    expect(screen.getByRole('button', { name: 'Load saved request Create pet' })).toBeInTheDocument();
    expect(screen.getByLabelText('Saved request folder')).toHaveDisplayValue('Pets');
  });
});
