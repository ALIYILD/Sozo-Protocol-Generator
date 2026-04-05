import { useState, type FormEvent } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useAuth } from '../hooks/useAuth';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

interface BackendError {
  response?: {
    data?: {
      detail?:
        | string
        | {
            password_issues?: string[];
          };
    };
  };
}

function extractErrorMessage(err: unknown): string {
  const e = err as BackendError;
  const detail = e?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (detail && typeof detail === 'object' && Array.isArray(detail.password_issues)) {
    return detail.password_issues.join(' · ');
  }
  if (err instanceof Error) return err.message;
  return 'Password change failed. Please try again.';
}

export default function ProfilePage() {
  const { user, changePassword } = useAuth();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const mutation = useMutation({
    mutationFn: (vars: { current_password: string; new_password: string }) =>
      changePassword(vars),
    onSuccess: () => {
      setSuccess('Password updated successfully.');
      setError('');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    },
    onError: (err: unknown) => {
      setError(extractErrorMessage(err));
      setSuccess('');
    },
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (newPassword !== confirmPassword) {
      setError('New passwords do not match.');
      return;
    }
    if (newPassword === currentPassword) {
      setError('New password must be different from current password.');
      return;
    }
    if (newPassword.length < 12) {
      setError('New password must be at least 12 characters.');
      return;
    }

    mutation.mutate({
      current_password: currentPassword,
      new_password: newPassword,
    });
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6 p-6">
      <h1 className="text-2xl font-bold text-sozo-text dark:text-white">Profile</h1>

      <Card title="Account">
        {user ? (
          <dl className="grid grid-cols-3 gap-y-3 text-sm">
            <dt className="font-medium text-gray-500 dark:text-gray-400">Name</dt>
            <dd className="col-span-2 text-sozo-text dark:text-gray-100">{user.name}</dd>

            <dt className="font-medium text-gray-500 dark:text-gray-400">Email</dt>
            <dd className="col-span-2 text-sozo-text dark:text-gray-100">{user.email}</dd>

            <dt className="font-medium text-gray-500 dark:text-gray-400">Role</dt>
            <dd className="col-span-2 text-sozo-text dark:text-gray-100 capitalize">
              {user.role}
            </dd>
          </dl>
        ) : (
          <p className="text-sm text-gray-500">Not signed in.</p>
        )}
      </Card>

      <Card title="Change password">
        {success && (
          <div className="mb-4 rounded-md bg-green-50 p-3 text-sm text-green-700">
            {success}
          </div>
        )}
        {error && (
          <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="current_password"
              className="block text-sm font-medium text-gray-700 dark:text-gray-200"
            >
              Current password
            </label>
            <input
              id="current_password"
              type="password"
              required
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
            />
          </div>

          <div>
            <label
              htmlFor="new_password"
              className="block text-sm font-medium text-gray-700 dark:text-gray-200"
            >
              New password
            </label>
            <input
              id="new_password"
              type="password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
              placeholder="At least 12 characters"
            />
            <p className="mt-1 text-xs text-gray-400">
              Min 12 characters, with upper, lower, digit, and special character.
            </p>
          </div>

          <div>
            <label
              htmlFor="confirm_password"
              className="block text-sm font-medium text-gray-700 dark:text-gray-200"
            >
              Confirm new password
            </label>
            <input
              id="confirm_password"
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
            />
          </div>

          <Button type="submit" isLoading={mutation.isPending}>
            Update password
          </Button>
        </form>
      </Card>
    </div>
  );
}
