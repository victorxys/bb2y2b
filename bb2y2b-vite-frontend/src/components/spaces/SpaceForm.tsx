import React, { useState } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import type { Space, SpaceCreate } from '../../lib/api';

interface SpaceFormProps {
  space?: Space;
  onSubmit: (data: SpaceCreate) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export const SpaceForm: React.FC<SpaceFormProps> = ({
  space,
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState({
    space_id: space?.space_id || '',
    space_name: space?.space_name || '',
    video_keyword: space?.video_keyword || '',
    video_type: space?.video_type || '',
    is_active: space?.is_active ?? true,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    const newErrors: Record<string, string> = {};
    if (!formData.space_id.trim()) {
      newErrors.space_id = 'UP主空间ID不能为空';
    }
    if (!formData.space_name.trim()) {
      newErrors.space_name = 'UP主名称不能为空';
    }
    if (!formData.video_type.trim()) {
      newErrors.video_type = '视频类型不能为空';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});
    onSubmit(formData);
  };

  const handleChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="UP主空间ID"
        value={formData.space_id}
        onChange={(e) => handleChange('space_id', e.target.value)}
        error={errors.space_id}
        placeholder="请输入B站UP主的空间ID"
        disabled={!!space} // 编辑时不允许修改ID
      />

      <Input
        label="UP主名称"
        value={formData.space_name}
        onChange={(e) => handleChange('space_name', e.target.value)}
        error={errors.space_name}
        placeholder="请输入UP主名称"
      />

      <Input
        label="视频关键字"
        value={formData.video_keyword}
        onChange={(e) => handleChange('video_keyword', e.target.value)}
        error={errors.video_keyword}
        placeholder="用逗号分隔多个关键字，如：教程,攻略"
      />

      <Input
        label="视频类型"
        value={formData.video_type}
        onChange={(e) => handleChange('video_type', e.target.value)}
        error={errors.video_type}
        placeholder="如：游戏、科技、生活等"
      />

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="is_active"
          checked={formData.is_active}
          onChange={(e) => handleChange('is_active', e.target.checked)}
          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="is_active" className="text-sm font-medium text-gray-700">
          启用此空间
        </label>
      </div>

      <div className="flex justify-end space-x-3 pt-4">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isLoading}
        >
          取消
        </Button>
        <Button
          type="submit"
          disabled={isLoading}
        >
          {isLoading ? '保存中...' : (space ? '更新' : '创建')}
        </Button>
      </div>
    </form>
  );
};