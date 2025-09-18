// バックエンドのAPIレスポンスに合わせた型定義

export type User = {
  id: number;
  name: string;
  email: string;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
};

export type UserCreate = {
  name: string;
  email: string;
  password: string;
};

export type UsersResponse = {
  users: User[];
  total: number;
};

export type Group = {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
};

export type GroupCreate = {
  name: string;
  description?: string;
};

export type GroupUpdate = {
  name?: string;
  description?: string;
};

export type GroupsResponse = {
  groups: Group[];
  total: number;
};

// ユーザーのヘルパー関数
export const UserHelpers = {
  /**
   * ユーザーが削除されているかどうかを確認
   */
  isDeleted: (user: User): boolean => {
    return user.deleted_at !== null;
  },

  /**
   * ユーザーがアクティブかどうかを確認
   */
  isActive: (user: User): boolean => {
    return user.deleted_at === null;
  },

  /**
   * 削除日時を日本語フォーマットで取得
   */
  getDeletedAtFormatted: (user: User): string | null => {
    if (!user.deleted_at) return null;
    return new Date(user.deleted_at).toLocaleString("ja-JP");
  },

  /**
   * 作成日時を日本語フォーマットで取得
   */
  getCreatedAtFormatted: (user: User): string => {
    return new Date(user.created_at).toLocaleString("ja-JP");
  },

  /**
   * 更新日時を日本語フォーマットで取得
   */
  getUpdatedAtFormatted: (user: User): string => {
    return new Date(user.updated_at).toLocaleString("ja-JP");
  },
};

// グループのヘルパー関数
export const GroupHelpers = {
  /**
   * グループが削除されているかどうかを確認
   */
  isDeleted: (group: Group): boolean => {
    return group.deleted_at !== null;
  },

  /**
   * グループがアクティブかどうかを確認
   */
  isActive: (group: Group): boolean => {
    return group.deleted_at === null;
  },

  /**
   * 削除日時を日本語フォーマットで取得
   */
  getDeletedAtFormatted: (group: Group): string | null => {
    if (!group.deleted_at) return null;
    return new Date(group.deleted_at).toLocaleString("ja-JP");
  },

  /**
   * 作成日時を日本語フォーマットで取得
   */
  getCreatedAtFormatted: (group: Group): string => {
    return new Date(group.created_at).toLocaleString("ja-JP");
  },

  /**
   * 更新日時を日本語フォーマットで取得
   */
  getUpdatedAtFormatted: (group: Group): string => {
    return new Date(group.updated_at).toLocaleString("ja-JP");
  },
};
