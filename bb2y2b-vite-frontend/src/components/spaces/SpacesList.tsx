import React, { useState } from 'react';
import { Plus, Edit, Trash2, Play } from 'lucide-react';
import { Button } from '../ui/Button';
import { Modal } from '../ui/Modal';
import { SpaceForm } from './SpaceForm';
import { useSpaces, useCreateSpace, useUpdateSpace, useDeleteSpace, useScanSpace } from '../../hooks/useSpaces';
import type { Space, SpaceCreate, SpaceUpdate } from '../../lib/api';

export const SpacesList: React.FC = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingSpace, setEditingSpace] = useState<Space | null>(null);
  const [deletingSpace, setDeletingSpace] = useState<Space | null>(null);

  const { data: spaces, isLoading, error } = useSpaces();
  const createMutation = useCreateSpace();
  const updateMutation = useUpdateSpace();
  const deleteMutation = useDeleteSpace();
  const scanMutation = useScanSpace();

  const handleCreateSpace = async (data: SpaceCreate) => {
    try {
      await createMutation.mutateAsync(data);
      setIsCreateModalOpen(false);
    } catch (error) {
      console.error('创建空间失败:', error);
    }
  };

  const handleUpdateSpace = async (data: SpaceUpdate) => {
    if (!editingSpace) return;
    
    try {
      await updateMutation.mutateAsync({
        spaceId: editingSpace.space_id,
        data,
      });
      setEditingSpace(null);
    } catch (error) {
      console.error('更新空间失败:', error);
    }
  };

  const handleDeleteSpace = async () => {
    if (!deletingSpace) return;
    
    try {
      await deleteMutation.mutateAsync(deletingSpace.space_id);
      setDeletingSpace(null);
    } catch (error) {
      console.error('删除空间失败:', error);
    }
  };

  const handleScanSpace = async (spaceId: string) => {
    try {
      const result = await scanMutation.mutateAsync(spaceId);
      alert(`扫描完成!\n发现视频: ${result.total_found || 0}\n新增: ${result.new_videos || 0}\n更新: ${result.updated_videos || 0}`);
    } catch (error) {
      console.error('扫描空间失败:', error);
      alert('扫描失败，请检查网络连接');
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">UP主空间管理</h1>
          <p className="text-gray-600">管理B站UP主空间，配置视频下载规则</p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          添加空间
        </Button>
      </div>

      {/* Spaces Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                UP主信息
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                视频配置
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                状态
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                最后扫描
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {spaces?.map((space) => (
              <tr key={space.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {space.space_name}
                    </div>
                    <div className="text-sm text-gray-500">
                      ID: {space.space_id}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div>
                    <div className="text-sm text-gray-900">
                      类型: {space.video_type}
                    </div>
                    {space.video_keyword && (
                      <div className="text-sm text-gray-500">
                        关键字: {space.video_keyword}
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      space.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {space.is_active ? '启用' : '禁用'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {space.last_scan_time
                    ? new Date(space.last_scan_time).toLocaleString('zh-CN')
                    : '从未扫描'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex items-center justify-end space-x-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleScanSpace(space.space_id)}
                      disabled={scanMutation.isPending}
                    >
                      <Play className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setEditingSpace(space)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="danger"
                      onClick={() => setDeletingSpace(space)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {(!spaces || spaces.length === 0) && (
          <div className="text-center py-12">
            <div className="text-gray-500">
              暂无UP主空间配置，点击"添加空间"开始配置
            </div>
          </div>
        )}
      </div>

      {/* Create Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="添加UP主空间"
      >
        <SpaceForm
          onSubmit={handleCreateSpace}
          onCancel={() => setIsCreateModalOpen(false)}
          isLoading={createMutation.isPending}
        />
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={!!editingSpace}
        onClose={() => setEditingSpace(null)}
        title="编辑UP主空间"
      >
        {editingSpace && (
          <SpaceForm
            space={editingSpace}
            onSubmit={(data) => handleUpdateSpace(data as SpaceUpdate)}
            onCancel={() => setEditingSpace(null)}
            isLoading={updateMutation.isPending}
          />
        )}
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!deletingSpace}
        onClose={() => setDeletingSpace(null)}
        title="确认删除"
        size="sm"
      >
        {deletingSpace && (
          <div className="space-y-4">
            <p className="text-gray-600">
              确定要删除UP主空间 "{deletingSpace.space_name}" 吗？此操作不可撤销。
            </p>
            <div className="flex justify-end space-x-3">
              <Button
                variant="outline"
                onClick={() => setDeletingSpace(null)}
                disabled={deleteMutation.isPending}
              >
                取消
              </Button>
              <Button
                variant="danger"
                onClick={handleDeleteSpace}
                disabled={deleteMutation.isPending}
              >
                {deleteMutation.isPending ? '删除中...' : '确认删除'}
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};