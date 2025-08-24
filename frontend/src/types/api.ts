// バックエンドのAPIレスポンスに合わせた型定義

export type User = {
  id: number;
  name: string;
  email: string;
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
