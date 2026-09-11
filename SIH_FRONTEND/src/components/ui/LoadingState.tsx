import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
}

const LoadingState: React.FC<LoadingStateProps> = ({ message = 'Loading...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 h-full min-h-[200px]">
      <Loader2 className="h-8 w-8 text-primary-600 animate-spin" />
      <p className="mt-4 text-sm text-slate-500 font-medium">{message}</p>
    </div>
  );
};

export default LoadingState;
