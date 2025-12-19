import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Simple check. For async (waiting for /me), we might need an observable or resolving
  // For this demo, we assume session check is fast or handled via login flow.
  if (authService.isLoggedIn()) {
    return true;
  }

  // If not explicitly logged in, maybe we are attempting?
  // Ideally we wait for checkSession() response. 
  // Let's redirect to login for now.
  return router.createUrlTree(['/login']);
};
