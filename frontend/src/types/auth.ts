export type AuthUser = {
  id: string;
  name?: string | null;
  email: string;
  phoneNum?: string | null;
  role?: string | null;
  isVerified?: boolean | null;
};

export type LoginCredentials = {
  email: string;
  password: string;
};

export type RegisterCredentials = {
  name: string;
  email: string;
  phoneNum: string;
  password: string;
};
