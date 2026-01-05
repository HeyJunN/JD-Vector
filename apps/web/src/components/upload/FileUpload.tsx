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
  acceptedFormats?: string[];
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
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

const getFileIcon = (fileName: string) => {
  const extension = fileName.split('.').pop()?.toLowerCase();
  switch (extension) {
    case 'pdf':
      return <FileType className="h-8 w-8 text-red-400" />;
    case 'txt':
    case 'md':
      return <FileText className="h-8 w-8 text-blue-400" />;
    default:
      return <FileText className="h-8 w-8 text-gray-400" />;
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
      {/* Label */}
      <label className="mb-2 block text-sm font-medium text-gray-300">
        {fileTypeLabel}
      </label>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={clsx(
          'relative cursor-pointer rounded-lg border-2 border-dashed p-8 transition-all duration-200',
          // Base styles
          'bg-gray-900/50 backdrop-blur-sm',
          // State-based styles
          {
            // Default state
            'border-gray-700 hover:border-gray-600 hover:bg-gray-900/70':
              !isDragActive && !isDragReject && !error && !selectedFile,
            // Drag active
            'border-blue-500 bg-blue-500/10': isDragActive && !isDragReject,
            // Drag reject or error
            'border-red-500 bg-red-500/10': isDragReject || error,
            // File selected (ready state)
            'border-green-500/50 bg-green-500/5': selectedFile && !error,
          }
        )}
      >
        <input {...getInputProps()} />

        {/* Content */}
        <div className="flex flex-col items-center justify-center space-y-4">
          {!selectedFile ? (
            <>
              {/* Upload Icon */}
              <div
                className={clsx(
                  'rounded-full p-4 transition-colors duration-200',
                  {
                    'bg-gray-800': !isDragActive && !error,
                    'bg-blue-500/20': isDragActive,
                    'bg-red-500/20': error,
                  }
                )}
              >
                {error ? (
                  <AlertCircle className="h-12 w-12 text-red-400" />
                ) : (
                  <UploadCloud
                    className={clsx('h-12 w-12 transition-colors', {
                      'text-gray-500': !isDragActive,
                      'text-blue-400': isDragActive,
                    })}
                  />
                )}
              </div>

              {/* Text */}
              <div className="text-center">
                <p className="text-base font-medium text-gray-200">
                  {isDragActive
                    ? '파일을 여기에 놓으세요'
                    : '파일을 드래그하거나 클릭하여 업로드'}
                </p>
                <p className="mt-1 text-sm text-gray-500">
                  PDF, TXT, MD (최대 {formatFileSize(maxSize)})
                </p>
              </div>

              {/* Error Message */}
              {error && (
                <div className="rounded-md bg-red-500/10 px-4 py-2">
                  <p className="text-sm text-red-400">{error}</p>
                </div>
              )}
            </>
          ) : (
            <>
              {/* File Ready State */}
              <div className="flex w-full items-center justify-between rounded-lg bg-gray-800/50 p-4">
                <div className="flex items-center space-x-4">
                  {/* File Icon */}
                  <div className="flex-shrink-0">
                    {getFileIcon(selectedFile.name)}
                  </div>

                  {/* File Info */}
                  <div className="flex-1 min-w-0">
                    <p className="truncate text-sm font-medium text-gray-100">
                      {selectedFile.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(selectedFile.size)}
                    </p>
                  </div>

                  {/* Remove Button */}
                  <button
                    onClick={handleRemoveFile}
                    className="flex-shrink-0 rounded-full p-1 text-gray-400 transition-colors hover:bg-gray-700 hover:text-gray-200"
                    type="button"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Ready Indicator */}
              <div className="flex items-center space-x-2 text-green-400">
                <CheckCircle2 className="h-5 w-5" />
                <span className="text-sm font-medium">파일 준비됨</span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Helper Text */}
      {!selectedFile && !error && (
        <p className="mt-2 text-xs text-gray-500">
          {fileType === 'resume'
            ? '이력서 또는 프로젝트 경험이 담긴 파일을 업로드하세요.'
            : '분석할 채용 공고 파일을 업로드하세요.'}
        </p>
      )}
    </div>
  );
};
