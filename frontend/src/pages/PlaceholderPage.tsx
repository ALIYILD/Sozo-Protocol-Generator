import { useLocation } from 'react-router-dom';
import Card from '../components/ui/Card';

export default function PlaceholderPage() {
  const location = useLocation();

  return (
    <div className="flex items-center justify-center pt-20">
      <Card className="max-w-md text-center">
        <h2 className="text-xl font-semibold text-sozo-text">Coming Soon</h2>
        <p className="mt-2 text-sm text-gray-500">
          The page at <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs">{location.pathname}</code> is under development.
        </p>
        <p className="mt-4 text-xs text-gray-400">V2 milestone</p>
      </Card>
    </div>
  );
}
