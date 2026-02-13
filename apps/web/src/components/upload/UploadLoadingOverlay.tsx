import { Loader2 } from 'lucide-react';

interface UploadLoadingOverlayProps {
  isVisible: boolean;
  message?: string;
}

export const UploadLoadingOverlay: React.FC<UploadLoadingOverlayProps> = ({
  isVisible,
  message,
}) => {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/90 backdrop-blur-sm">
      <div className="flex flex-col items-center space-y-6 rounded-2xl border border-slate-800 bg-slate-900/80 p-12 shadow-2xl backdrop-blur-md">
        {/* Spinner Animation */}
        <div className="relative">
          <Loader2 className="h-16 w-16 animate-spin text-blue-500" />
          <div className="absolute inset-0 -z-10 animate-pulse rounded-full bg-blue-500/20 blur-xl" />
        </div>

        {/* Progress Text */}
        <div className="text-center">
          <p className="text-xl font-semibold text-slate-100">
            {message || '처리 중...'}
          </p>
          <p className="mt-2 text-sm text-slate-400">
            잠시만 기다려주세요. 대용량 파일은 수십 초가 걸릴 수 있습니다.
          </p>
        </div>

        {/* Animated Progress Indicator */}
        <div className="flex space-x-2">
          <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.3s]" />
          <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.15s]" />
          <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500" />
        </div>
      </div>
    </div>
  );
};

export default UploadLoadingOverlay;
