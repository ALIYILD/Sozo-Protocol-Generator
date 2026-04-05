import clsx from 'clsx';
import type { ProtocolStatus } from '../../types';

interface BadgeProps {
  status: ProtocolStatus | string;
  className?: string;
}

const statusStyles: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
  pending_review: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300',
  approved: 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300',
  rejected: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300',
  archived: 'bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400',
  high: 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300',
  moderate: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300',
  low: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300',
  very_low: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300',
};

const statusLabels: Record<string, string> = {
  draft: 'Draft',
  pending_review: 'Pending Review',
  approved: 'Approved',
  rejected: 'Rejected',
  archived: 'Archived',
  high: 'High',
  moderate: 'Moderate',
  low: 'Low',
  very_low: 'Very Low',
};

export default function Badge({ status, className }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        statusStyles[status] ?? 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
        className,
      )}
    >
      {statusLabels[status] ?? status}
    </span>
  );
}
