import React, { useState, useRef, useEffect } from 'react';
import { 
  Download, Trash2, RefreshCw, 
  CheckCircle, XCircle, Clock, Loader2, 
  FolderOpen, Music, Film, Play, X, FileText
} from 'lucide-react';
import { Button } from '../ui/Button';
import { 
  useActiveTasks, 
  useAllTasks, 
  useDownloadedFiles, 
  useRemoveTask, 
  useClearCompletedTasks,
  useDeleteFile 
} from '../../hooks/useDownloads';
import { downloadsApi } from '../../lib/downloadsApi';
import type { DownloadTask, DownloadedFile, SubtitleContent } from '../../lib/downloadsApi';

// 状态图标映射
const statusIcons: Record<string, React.ReactNode> = {
  pending: <Clock className="h-4 w-4 text-yellow-500" />,
  downloading: <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />,
  merging: <Loader2 className="h-4 w-4 text-purple-500 animate-spin" />,
  completed: <CheckCircle className="h-4 w-4 text-green-500" />,
  error: <XCircle className="h-4 w-4 text-red-500" />,
  cancelled: <XCircle className="h-4 w-4 text-gray-500" />,
};

const statusLabels: Record<string, string> = {
  pending: '等待中',
  downloading: '下载中',
  merging: '合并中',
  completed: '已完成',
  error: '失败',
  cancelled: '已取消',
};

// 进度条组件
const ProgressBar: React.FC<{ percent: number; status: string }> = ({ percent, status }) => {
  const colorClass = {
    pending: 'bg-yellow-500',
    downloading: 'bg-blue-500',
    merging: 'bg-purple-500',
    completed: 'bg-green-500',
    error: 'bg-red-500',
    cancelled: 'bg-gray-500',
  }[status] || 'bg-blue-500';

  return (
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div
        className={`h-2 rounded-full transition-all duration-300 ${colorClass}`}
        style={{ width: `${Math.min(100, percent)}%` }}
      />
    </div>
  );
};

// 单个任务卡片
const TaskCard: React.FC<{ task: DownloadTask; onRemove: () => void }> = ({ task, onRemove }) => {
  // 根据阶段计算显示的进度
  const getDisplayProgress = () => {
    if (task.status === 'completed') return 100;
    if (task.status === 'merging') {
      // 合并阶段：直接使用 merge_progress (0-100%)
      return task.merge_progress || 0;
    }
    // 下载阶段显示0-100%
    return task.progress_percent || 0;
  };

  const displayProgress = getDisplayProgress();
  
  // 获取阶段描述
  const getStageDescription = () => {
    switch (task.stage) {
      case 'fetching_info': return '获取视频信息';
      case 'fetching_links': return '获取下载链接';
      case 'downloading': return '下载中';
      case 'merging': return '合并中';
      case 'downloading_cover': return '下载封面';
      case 'completed': return '已完成';
      default: return task.stage;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-4 space-y-3">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-gray-900 truncate" title={task.title}>
            {task.title || task.bvid}
          </h3>
          <p className="text-sm text-gray-500">{task.bvid}</p>
        </div>
        <div className="flex items-center space-x-2 ml-2">
          {statusIcons[task.status]}
          <span className="text-sm text-gray-600">{statusLabels[task.status]}</span>
        </div>
      </div>

      {/* 进度条 */}
      <div className="space-y-1">
        <ProgressBar percent={displayProgress} status={task.status} />
        <div className="flex justify-between text-xs text-gray-400">
          <span>{getStageDescription()}</span>
          <span>{displayProgress.toFixed(1)}%</span>
        </div>
      </div>
      
      {/* 合并进度详情 */}
      {task.status === 'merging' && task.total_duration > 0 && (
        <div className="text-xs text-purple-600 bg-purple-50 px-2 py-1 rounded">
          音频总时长: {task.total_duration_formatted}
        </div>
      )}

      {/* 进度详情 */}
      <div className="flex items-center justify-between text-sm">
        <div className="text-gray-600 flex items-center">
          {task.status === 'merging' && (
            <span className="inline-flex items-center">
              <Loader2 className="h-3 w-3 mr-1 animate-spin text-purple-500" />
            </span>
          )}
          {task.stage_message}
        </div>
        <div className="flex items-center space-x-4 text-gray-500">
          {task.status === 'downloading' && task.speed > 0 && (
            <>
              <span className="text-blue-600 font-medium">{task.speed_formatted}</span>
              {task.eta > 0 && <span>剩余 {task.eta_formatted}</span>}
            </>
          )}
          {task.total_pages > 0 && task.status === 'downloading' && (
            <span className="bg-gray-100 px-2 py-0.5 rounded">
              {task.current_page}/{task.total_pages} P
            </span>
          )}
        </div>
      </div>

      {/* 下载统计 */}
      {task.status === 'downloading' && task.total_bytes > 0 && (
        <div className="text-xs text-gray-400">
          已下载: {formatBytes(task.current_bytes)} / {formatBytes(task.total_bytes)}
        </div>
      )}

      {/* 错误信息 */}
      {task.error_message && (
        <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
          {task.error_message}
        </div>
      )}

      {/* 完成信息 */}
      {task.status === 'completed' && task.download_path && (
        <div className="text-sm text-green-600 bg-green-50 p-2 rounded flex items-center">
          <CheckCircle className="h-4 w-4 mr-2" />
          下载完成
        </div>
      )}

      {/* 操作按钮 */}
      {(task.status === 'completed' || task.status === 'error' || task.status === 'cancelled') && (
        <div className="flex justify-end">
          <Button size="sm" variant="outline" onClick={onRemove}>
            <Trash2 className="h-4 w-4 mr-1" />
            移除
          </Button>
        </div>
      )}
    </div>
  );
};

// 格式化字节数
function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} GB`;
}

// 字幕查看弹窗
const SubtitleViewer: React.FC<{
  file: DownloadedFile;
  onClose: () => void;
}> = ({ file, onClose }) => {
  const [subtitle, setSubtitle] = useState<SubtitleContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadSubtitle = async () => {
      if (!file.has_subtitle) {
        setError('该文件没有字幕');
        setLoading(false);
        return;
      }

      try {
        const subtitleFilename = file.name.replace(/\.(mp3|mp4|m4a)$/, '.txt');
        const subtitleData = await downloadsApi.getSubtitle(subtitleFilename);
        setSubtitle(subtitleData);
      } catch (err) {
        setError('加载字幕失败');
        console.error('Failed to load subtitle:', err);
      } finally {
        setLoading(false);
      }
    };

    loadSubtitle();
  }, [file]);

  // ESC 关闭
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  const handleDownload = () => {
    if (subtitle) {
      const subtitleFilename = file.name.replace(/\.(mp3|mp4|m4a)$/, '.txt');
      const url = downloadsApi.getSubtitleDownloadUrl(subtitleFilename);
      window.open(url, '_blank');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75 p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-blue-600" />
            <h2 className="text-lg font-medium text-gray-900">AI字幕</h2>
          </div>
          <div className="flex items-center gap-2">
            {subtitle && (
              <Button size="sm" variant="outline" onClick={handleDownload}>
                <Download className="h-4 w-4 mr-1" />
                下载字幕
              </Button>
            )}
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          <div className="p-4 border-b bg-gray-50">
            <h3 className="font-medium text-gray-900 truncate" title={file.title || file.name}>
              {file.title || file.name}
            </h3>
            <p className="text-sm text-gray-500">{file.bvid}</p>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
                <span className="ml-2 text-gray-600">加载字幕中...</span>
              </div>
            ) : error ? (
              <div className="text-center py-8">
                <div className="text-red-600 mb-2">{error}</div>
                <p className="text-gray-500 text-sm">该视频可能没有AI生成的字幕内容</p>
              </div>
            ) : subtitle ? (
              <div className="prose max-w-none">
                <pre className="whitespace-pre-wrap text-sm leading-relaxed text-gray-800 font-sans">
                  {subtitle.content}
                </pre>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
};

// 媒体播放器弹窗
const MediaPlayer: React.FC<{ 
  file: DownloadedFile; 
  onClose: () => void 
}> = ({ file, onClose }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const streamUrl = downloadsApi.getStreamUrl(file.name);
  const isVideo = file.type === 'mp4' || file.type === 'webm';
  const coverFilename = file.name.replace(/\.(mp3|mp4|m4a)$/, '.jpg');
  const coverUrl = file.cover_path ? downloadsApi.getCoverUrl(coverFilename) : null;

  // ESC 关闭
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75">
      {/* 关闭按钮 */}
      <button
        onClick={onClose}
        className="absolute top-4 right-4 text-white hover:text-gray-300 z-10"
      >
        <X className="h-8 w-8" />
      </button>

      <div className="w-full max-w-4xl mx-4">
        {/* 标题 */}
        <h2 className="text-white text-lg font-medium mb-4 truncate">
          {file.title || file.name}
        </h2>

        {/* 播放器 */}
        {isVideo ? (
          <video
            ref={videoRef}
            src={streamUrl}
            controls
            autoPlay
            className="w-full rounded-lg shadow-2xl"
            poster={coverUrl || undefined}
          />
        ) : (
          <div className="bg-gray-900 rounded-lg p-8">
            {/* 音频封面 */}
            {coverUrl && (
              <div className="w-64 h-64 mx-auto mb-6 rounded-lg overflow-hidden shadow-lg">
                <img src={coverUrl} alt={file.title || file.name} className="w-full h-full object-cover" />
              </div>
            )}
            <audio
              ref={audioRef}
              src={streamUrl}
              controls
              autoPlay
              className="w-full"
            />
          </div>
        )}

        {/* 文件信息 */}
        <div className="mt-4 flex items-center justify-between text-gray-400 text-sm">
          <div className="flex items-center gap-4">
            {file.bvid && <span>{file.bvid}</span>}
            <span>{file.size_formatted}</span>
            <span className="uppercase">{file.type}</span>
          </div>
          <a
            href={downloadsApi.getFileUrl(file.name)}
            download={file.name}
            className="text-blue-400 hover:text-blue-300 flex items-center"
          >
            <Download className="h-4 w-4 mr-1" />
            下载文件
          </a>
        </div>
      </div>
    </div>
  );
};

// 已下载文件列表项
const FileRow: React.FC<{ 
  file: DownloadedFile; 
  onDelete: () => void;
  onPlay: () => void;
  onViewSubtitle: () => void;
}> = ({ file, onDelete, onPlay, onViewSubtitle }) => {
  const fileIcon = file.type === 'mp3' ? (
    <Music className="h-5 w-5 text-blue-500" />
  ) : (
    <Film className="h-5 w-5 text-purple-500" />
  );

  // 从文件名提取封面文件名，使用 getCoverUrl 构建完整URL
  const coverFilename = file.name.replace(/\.(mp3|mp4|m4a)$/, '.jpg');
  const coverUrl = file.cover_path ? downloadsApi.getCoverUrl(coverFilename) : null;

  return (
    <div className="bg-white rounded-lg shadow p-4 flex items-center gap-4 hover:bg-gray-50 transition-colors">
      {/* 封面缩略图 - 可点击播放 */}
      <div 
        className="w-24 h-14 bg-gray-100 rounded overflow-hidden flex-shrink-0 relative cursor-pointer group"
        onClick={onPlay}
      >
        {coverUrl ? (
          <img
            src={coverUrl}
            alt={file.title || file.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            {fileIcon}
          </div>
        )}
        {/* 播放图标覆盖层 */}
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 flex items-center justify-center transition-all">
          <Play className="h-8 w-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
      </div>

      {/* 信息 */}
      <div className="flex-1 min-w-0">
        <h3 
          className="font-medium text-gray-900 truncate cursor-pointer hover:text-blue-600" 
          title={file.title || file.name}
          onClick={onPlay}
        >
          {file.title || file.name}
        </h3>
        <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
          {file.bvid && <span className="text-blue-600">{file.bvid}</span>}
          <span>{file.size_formatted}</span>
          <span className="uppercase">{file.type}</span>
          <span>{new Date(file.created_at * 1000).toLocaleString()}</span>
        </div>
      </div>

      {/* 操作按钮 */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <Button
          size="sm"
          variant="outline"
          onClick={onPlay}
        >
          <Play className="h-4 w-4 mr-1" />
          播放
        </Button>
        {file.has_subtitle && (
          <Button
            size="sm"
            variant="outline"
            onClick={onViewSubtitle}
            title="查看AI字幕"
          >
            <FileText className="h-4 w-4 mr-1" />
            字幕
          </Button>
        )}
        <a
          href={downloadsApi.getFileUrl(file.name)}
          download={file.name}
          className="inline-flex items-center px-3 py-1.5 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
        >
          <Download className="h-4 w-4 mr-1" />
          下载
        </a>
        <Button
          size="sm"
          variant="danger"
          onClick={onDelete}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};

export const DownloadManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'tasks' | 'files'>('tasks');
  const [playingFile, setPlayingFile] = useState<DownloadedFile | null>(null);
  const [viewingSubtitleFile, setViewingSubtitleFile] = useState<DownloadedFile | null>(null);
  
  const { data: activeTasks, refetch: refetchActive } = useActiveTasks();
  const { data: allTasks, isLoading: loadingAll, refetch: refetchAll } = useAllTasks();
  const { data: files, isLoading: loadingFiles, refetch: refetchFiles } = useDownloadedFiles();
  
  const removeTaskMutation = useRemoveTask();
  const clearCompletedMutation = useClearCompletedTasks();
  const deleteFileMutation = useDeleteFile();

  const handleRefresh = () => {
    refetchActive();
    refetchAll();
    refetchFiles();
  };

  const handleClearCompleted = async () => {
    if (confirm('确定要清除所有已完成的任务记录吗？')) {
      await clearCompletedMutation.mutateAsync();
    }
  };

  const handleDeleteFile = async (filename: string) => {
    if (confirm(`确定要删除文件 "${filename}" 吗？`)) {
      await deleteFileMutation.mutateAsync(filename);
    }
  };

  const activeCount = activeTasks?.tasks?.length || 0;
  const completedCount = (allTasks?.tasks?.filter(t => t.status === 'completed').length) || 0;
  const filesCount = files?.files?.length || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">下载管理</h1>
          <p className="text-gray-600">查看下载进度和已下载的文件</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4 mr-1" />
            刷新
          </Button>
          {activeTab === 'tasks' && completedCount > 0 && (
            <Button variant="outline" size="sm" onClick={handleClearCompleted}>
              清除已完成
            </Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('tasks')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'tasks'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            下载任务
            {activeCount > 0 && (
              <span className="ml-2 bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full text-xs">
                {activeCount}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('files')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'files'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            已下载文件
            {filesCount > 0 && (
              <span className="ml-2 bg-green-100 text-green-600 px-2 py-0.5 rounded-full text-xs">
                {filesCount}
              </span>
            )}
          </button>
        </nav>
      </div>

      {/* Content */}
      {activeTab === 'tasks' ? (
        <div className="space-y-4">
          {loadingAll ? (
            <div className="text-center py-8 text-gray-500">加载中...</div>
          ) : allTasks?.tasks && allTasks.tasks.length > 0 ? (
            allTasks.tasks.map((task) => (
              <TaskCard
                key={task.task_id}
                task={task}
                onRemove={() => removeTaskMutation.mutate(task.task_id)}
              />
            ))
          ) : (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <Download className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">暂无下载任务</p>
              <p className="text-sm text-gray-400 mt-1">在视频管理页面点击下载按钮开始下载</p>
            </div>
          )}
        </div>
      ) : (
        <div>
          {loadingFiles ? (
            <div className="text-center py-8 text-gray-500">加载中...</div>
          ) : files?.files && files.files.length > 0 ? (
            <div className="space-y-3">
              {files.files.map((file) => (
                <FileRow
                  key={file.name}
                  file={file}
                  onDelete={() => handleDeleteFile(file.name)}
                  onPlay={() => setPlayingFile(file)}
                  onViewSubtitle={() => setViewingSubtitleFile(file)}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <FolderOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">暂无已下载文件</p>
            </div>
          )}
        </div>
      )}

      {/* 媒体播放器弹窗 */}
      {playingFile && (
        <MediaPlayer
          file={playingFile}
          onClose={() => setPlayingFile(null)}
        />
      )}

      {/* 字幕查看弹窗 */}
      {viewingSubtitleFile && (
        <SubtitleViewer
          file={viewingSubtitleFile}
          onClose={() => setViewingSubtitleFile(null)}
        />
      )}
    </div>
  );
};
