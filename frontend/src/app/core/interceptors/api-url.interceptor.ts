import { HttpInterceptorFn } from '@angular/common/http';
import { environment } from '../../../environments/environment';

/**
 * Prepends the API base URL to outgoing requests that start with '/'.
 */
export const apiUrlInterceptor: HttpInterceptorFn = (req, next) => {
  const url = req.url;
  if (url.startsWith('/')) {
    const base = environment.apiUrl.replace(/\/$/, '');
    req = req.clone({ url: `${base}${url}` });
  }
  return next(req);
};
