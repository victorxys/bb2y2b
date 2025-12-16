import React, { useState, useEffect } from 'react';
import { Download, Trash2, ExternalLink, RefreshCw, Loader2, FileText } from 'lucide-react';
import { Button } from '../ui/Button';
import { useVideos, useDeleteVideo, useStartDownload } from '../../hooks/useVideos';
import type { Video } from '../../lib/videosApi';

const statusMap: Record<string, { label: string; color: string }> = {
  pending: { label: '待下载', color: 'bg-yellow-100 text-yellow-800' },
  downloading: { label: '下载中', color: 'bg-blue-100 text-blue-800 animate-pulse' },
  downloaded: { label: '已下载', color: 'bg-green-100 text-green-800' },
  uploading: { label: '上传中', color: 'bg-purple-100 text-purple-800' },
  uploaded: { label: '已上传', color: 'bg-green-100 text-green-800' },
  error: { label: '错误', color: 'bg-red-100 text-red-800' },
};

// 视频列表行组件
const VideoRow: React.FC<{
  video: Video;
  onDownload: () => void;
  onDelete: () => void;
  isDownloading: boolean;
  isDeleting: boolean;
}> = ({ video, onDownload, onDelete, isDownloading, isDeleting }) => {
  const status = statusMap[video.status] || { label: video.status, color: 'bg-gray-100 text-gray-800' };

  return (
    <div className="bg-white rounded-lg shadow px-4 py-3 flex items-center gap-4 hover:bg-gray-50 transition-colors">
      {/* 标题和BV号 */}
      <div className="flex-1 min-w-0">
        <h3 className="font-medium text-gray-900 truncate" title={video.title}>
          {video.title}
        </h3>
        <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
          <a
            href={video.bilibili_url || `https://www.bilibili.com/video/${video.bvid}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 flex items-center"
          >
            {video.bvid}
            <ExternalLink className="h-3 w-3 ml-1" />
          </a>
          {video.duration && <span>{video.duration}</span>}
          <span>{video.video_type}</span>
          {video.start_p && video.end_p && (
            <span>P{video.start_p}-{video.end_p}</span>
          )}
        </div>
      </div>

      {/* 状态 */}
      <div className="flex-shrink-0">
        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${status.color}`}>
          {video.status === 'downloading' && <Loader2 className="h-3 w-3 mr-1 animate-spin" />}
          {status.label}
        </span>
      </div>

      {/* 字幕状态 */}
      <div className="flex-shrink-0 w-16 text-center">
        {video.subtitle_path ? (
          <span className="text-green-600 text-xs flex items-center justify-center">
            <FileText className="h-3 w-3 mr-1" />
            有字幕
          </span>
        ) : (
          <span className="text-gray-400 text-xs">无字幕</span>
        )}
      </div>

      {/* 操作按钮 */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <Button
          size="sm"
          variant="outline"
          onClick={onDownload}
          disabled={isDownloading || video.status === 'downloading'}
          title={video.status === 'downloaded' ? '重新下载' : '开始下载'}
        >
          {(video.status === 'downloading' || isDownloading) ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Download className="h-4 w-4" />
          )}
        </Button>
        <Button
          size="sm"
          variant="danger"
          onClick={onDelete}
          disabled={isDeleting || video.status === 'downloading'}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};

export const VideosList: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<string>('');
  const { data: videos, isLoading, error, refetch } = useVideos(
    statusFilter ? { status: statusFilter } : undefined
  );
  const deleteMutation = useDeleteVideo();
  const downloadMutation = useStartDownload();
  const [downloadingIds, setDownloadingIds] = useState<Set<string>>(new Set());

  // 自动刷新：当有视频正在下载时，每5秒刷新一次
  useEffect(() => {
    const hasDownloading = videos?.some(v => v.status === 'downloading');
    if (hasDownloading) {
      const interval = setInterval(() => {
        refetch();
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [videos, refetch]);

  const handleDelete = async (video: Video) => {
    if (confirm(`确定要删除视频 "${video.title}" 吗？`)) {
      try {
        await deleteMutation.mutateAsync(video.bvid);
      } catch (error) {
        console.error('删除失败:', error);
      }
    }
  };

  const handleDownload = async (video: Video) => {
    try {
      setDownloadingIds(prev => new Set(prev).add(video.bvid));
      const result = await downloadMutation.mutateAsync(video.bvid);
      alert(`下载任务已启动!\n任务ID: ${result.task_id}\n视频: ${video.title}\n\n下载将在后台进行，页面会自动刷新状态`);
      refetch();
    } catch (error) {
      console.error('下载失败:', error);
      alert('下载启动失败，请重试');
    } finally {
      setDownloadingIds(prev => {
        const next = new Set(prev);
        next.delete(video.bvid);
        return next;
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">
          加载失败: {error instanceof Error ? error.message : '未知错误'}
        </div>
      </div>
    );
  }

  const downloadingCount = videos?.filter(v => v.status === 'downloading').length || 0;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">视频管理</h1>
          <p className="text-gray-600">管理扫描到的B站视频，进行下载和上传操作</p>
        </div>
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
            刷新
          </Button>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">全部状态</option>
            <option value="pending">待下载</option>
            <option value="downloading">下载中</option>
            <option value="downloaded">已下载</option>
            <option value="uploaded">已上传</option>
            <option value="error">错误</option>
          </select>
          <span className="text-sm text-gray-500">
            共 {videos?.length || 0} 个视频
            {downloadingCount > 0 && (
              <span className="ml-2 text-blue-600">({downloadingCount} 个下载中)</span>
            )}
          </span>
        </div>
      </div>

      {/* 列表头 */}
      <div className="bg-gray-100 rounded-lg px-4 py-2 flex items-center gap-4 text-sm font-medium text-gray-600">
        <div className="flex-1">标题 / BV号</div>
        <div className="flex-shrink-0 w-20 text-center">状态</div>
        <div className="flex-shrink-0 w-16 text-center">字幕</div>
        <div className="flex-shrink-0 w-24 text-center">操作</div>
      </div>

      {/* Videos List */}
      <div className="space-y-2">
        {videos?.map((video) => (
          <VideoRow
            key={video.id}
            video={video}
            onDownload={() => handleDownload(video)}
            onDelete={() => handleDelete(video)}
            isDownloading={downloadingIds.has(video.bvid)}
            isDeleting={deleteMutation.isPending}
          />
        ))}
      </div>

      {(!videos || videos.length === 0) && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <div className="text-gray-500">
            暂无视频，请先在UP主空间管理中扫描视频
          </div>
        </div>
      )}
    </div>
  );
};
