import { Injectable, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { tap, catchError, of, Observable } from 'rxjs';

export interface User {
  id?: number;
  username: string;
  email?: string;
  is_admin: boolean;
  profile_image?: string;
  preferences?: any;
  tier?: 'free' | 'gold' | 'titanium' | 'adamantium';
  is_titanium?: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  // Ensure we use 127.0.0.1 consistency or relative path if proxied. Sticking to 127.0.0.1:5001 is safer for cookies on localhost.
  private apiUrl = 'http://localhost:5001/auth';

  currentUser = signal<User | null>(null);

  constructor() {
    this.checkSession();
  }

  checkSession(): Observable<User | null> {
    return this.http.get<User>(`${this.apiUrl}/me`, { withCredentials: true }).pipe(
      tap({
        next: (user) => {
          // Ensure tier exists if missing from old backend (fallback)
          if (!user.tier) user.tier = 'free';
          this.currentUser.set(user);
        },
        error: () => this.currentUser.set(null)
      }),
      catchError(() => {
        this.currentUser.set(null);
        return of(null);
      })
    );
  }

  login(credentials: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/login`, credentials, { withCredentials: true }).pipe(
      tap((res: any) => {
        if (res.success && res.user) {
          const user = res.user;
          if (!user.tier) user.tier = 'free'; // Fallback
          this.currentUser.set(user);
          this.router.navigate(['/dashboard']);
        }
      })
    );
  }

  register(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, data, { withCredentials: true }).pipe(
      tap((res: any) => {
        // Auto login logic if backend returns user
        if (res.success && res.user) {
          const user = res.user;
          if (!user.tier) user.tier = 'free';
          this.currentUser.set(user);
          this.router.navigate(['/dashboard']);
        }
      })
    );
  }

  logout() {
    this.http.post(`${this.apiUrl}/logout`, {}, { withCredentials: true }).subscribe(() => {
      this.currentUser.set(null);
      this.router.navigate(['/login']);
    });
  }

  isLoggedIn() {
    return !!this.currentUser();
  }
}
