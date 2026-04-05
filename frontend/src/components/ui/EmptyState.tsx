import type { ComponentType } from 'react';
import clsx from 'clsx';
import Button from './Button';

interface EmptyStateProps {
  icon: ComponentType<{ className?: string }>;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export default function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={clsx(
        'rounded-lg border border-gray-200 bg-white shadow-sm px-6 py-12',
        className,
      )}
    >
      <div className="flex flex-col items-center text-center gap-3">
        <div className="rounded-full bg-sozo-surface p-4">
          <Icon className="h-10 w-10 text-gray-300" />
        </div>
        <div className="space-y-1">
          <p className="text-base font-semibold text-sozo-text">{title}</p>
          <p className="text-sm text-gray-500 max-w-xs mx-auto">{description}</p>
        </div>
        {action && (
          <Button
            variant="primary"
            size="sm"
            onClick={action.onClick}
            className="mt-1"
          >
            {action.label}
          </Button>
        )}
      </div>
    </div>
  );
}
