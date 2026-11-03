export type ApiResponse<T> = {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
  meta?: {
    requestId: string;
    timestamp: string;
    source: "mock" | "central-platform" | "external";
  };
};

export type ApiPagination = {
  page: number;
  pageSize: number;
  total: number;
};

export type ApiListResponse<T> = ApiResponse<T[]> & {
  pagination?: ApiPagination;
};
