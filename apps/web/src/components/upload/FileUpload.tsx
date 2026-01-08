import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  UploadCloud,
  FileText,
  FileType,
  X,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { clsx } from 'clsx';

interface FileUploadProps {
  fileType: 'resume' | 'jd';
  onFileSelect: (file: File | null) => void;
  acceptedFormats?: Record<string, string[]>;
  maxSize?: number; // bytes
  className?: string;
}

const DEFAULT_ACCEPTED_FORMATS = {
  'application/pdf': ['.pdf'],
  'text/plain': ['.txt'],
  'text/markdown': ['.md'],
};

const DEFAULT_MAX_SIZE = 10 * 1024 * 1024; // 10MB

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

const getFileIcon = (fileName: string) => {
  const extension = fileName.split('.').pop()?.toLowerCase();
  switch (extension) {
    case 'pdf':
      return <FileType className="h-10 w-10 text-red-400" />;
    case 'txt':
    case 'md':
      return <FileText className="h-10 w-10 text-blue-400" />;
    default:
      return <FileText className="h-10 w-10 text-slate-400" />;
  }
};

export const FileUpload: React.FC<FileUploadProps> = ({
  fileType,
  onFileSelect,
  acceptedFormats,
  maxSize = DEFAULT_MAX_SIZE,
  className,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      // Reset error
      setError(null);

      // Handle rejected files
      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0];
        if (rejection.errors[0]?.code === 'file-too-large') {
          setError(`파일 크기는 ${formatFileSize(maxSize)} 이하여야 합니다.`);
        } else if (rejection.errors[0]?.code === 'file-invalid-type') {
          setError('PDF, TXT, MD 파일만 업로드할 수 있습니다.');
        } else {
          setError('파일 업로드 중 오류가 발생했습니다.');
        }
        return;
      }

      // Handle accepted files
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        setSelectedFile(file);
        onFileSelect(file);
      }
    },
    [maxSize, onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } =
    useDropzone({
      onDrop,
      accept: acceptedFormats || DEFAULT_ACCEPTED_FORMATS,
      maxSize,
      maxFiles: 1,
      multiple: false,
    });

  const handleRemoveFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedFile(null);
    setError(null);
    onFileSelect(null);
  };

  const fileTypeLabel = fileType === 'resume' ? '이력서/경험' : '채용 공고(JD)';

  return (
    <div className={clsx('w-full', className)}>
      {/* Label - Enhanced Typography */}
      <label className="mb-4 block text-xl font-bold tracking-tight text-slate-200">
        {fileTypeLabel}
      </label>

      {/* Dropzone - Enhanced spacing and design */}
      <div
        {...getRootProps()}
        className={clsx(
          'group relative min-h-[280px] cursor-pointer rounded-xl border-2 border-dashed p-10 transition-all duration-200',
          // Base styles
          'bg-slate-900/30 backdrop-blur-sm',
          // State-based styles
          {
            // Default state
            'border-slate-800/50 hover:scale-[1.01] hover:border-slate-700 hover:bg-slate-900/40':
              !isDragActive && !isDragReject && !error && !selectedFile,
            // Drag active
            'scale-[1.01] border-blue-500/50 bg-blue-500/5':
              isDragActive && !isDragReject,
            // Drag reject or error
            'border-red-500/50 bg-red-500/5': isDragReject || error,
            // File selected (ready state)
            'border-emerald-500/30 bg-emerald-500/5': selectedFile && !error,
          }
        )}
      >
        <input {...getInputProps()} />

        {/* Content */}
        <div className="flex min-h-[200px] flex-col items-center justify-center space-y-6">
          {!selectedFile ? (
            <>
              {/* Upload Icon - Larger */}
              <div
                className={clsx(
                  'rounded-2xl p-6 transition-all duration-200',
                  {
                    'bg-slate-800/50': !isDragActive && !error,
                    'bg-blue-500/10 group-hover:bg-blue-500/20': isDragActive,
                    'bg-red-500/10': error,
                  }
                )}
              >
                {error ? (
                  <AlertCircle className="h-14 w-14 text-red-400" />
                ) : (
                  <UploadCloud
                    className={clsx('h-14 w-14 transition-colors', {
                      'text-slate-500 group-hover:text-slate-400':
                        !isDragActive,
                      'text-blue-400': isDragActive,
                    })}
                  />
                )}
              </div>

              {/* Text - Enhanced spacing */}
              <div className="text-center">
                <p className="text-base font-semibold text-slate-200">
                  {isDragActive
                    ? '파일을 여기에 놓으세요'
                    : '파일을 드래그하거나 클릭하여 업로드'}
                </p>
                <p className="mt-2 text-sm leading-relaxed text-slate-500">
                  PDF, TXT, MD · 최대 {formatFileSize(maxSize)}
                </p>
              </div>

              {/* Error Message */}
              {error && (
                <div className="rounded-xl bg-red-500/10 px-6 py-3 backdrop-blur-sm">
                  <p className="text-sm font-medium text-red-400">{error}</p>
                </div>
              )}
            </>
          ) : (
            <>
              {/* File Ready State */}
              <div className="flex w-full items-center justify-between rounded-xl bg-slate-800/50 p-6 backdrop-blur-sm">
                <div className="flex items-center space-x-5">
                  {/* File Icon */}
                  <div className="flex-shrink-0">
                    {getFileIcon(selectedFile.name)}
                  </div>

                  {/* File Info */}
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-base font-semibold text-slate-100">
                      {selectedFile.name}
                    </p>
                    <p className="mt-1 text-sm text-slate-500">
                      {formatFileSize(selectedFile.size)}
                    </p>
                  </div>

                  {/* Remove Button */}
                  <button
                    onClick={handleRemoveFile}
                    className="flex-shrink-0 rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-700 hover:text-slate-200"
                    type="button"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Ready Indicator */}
              <div className="flex items-center space-x-2 text-emerald-400">
                <CheckCircle2 className="h-5 w-5" />
                <span className="text-sm font-semibold">파일 준비됨</span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Helper Text */}
      {!selectedFile && !error && (
        <p className="mt-3 text-xs leading-relaxed text-slate-500">
          {fileType === 'resume'
            ? '이력서 또는 프로젝트 경험이 담긴 파일을 업로드하세요.'
            : '분석할 채용 공고 파일을 업로드하세요.'}
        </p>
      )}
    </div>
  );
};
