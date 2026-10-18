export class AppError extends Error {
  readonly retryable: boolean;

  constructor(message: string, retryable = false) {
    super(message);
    this.name = 'AppError';
    this.retryable = retryable;
  }
}
