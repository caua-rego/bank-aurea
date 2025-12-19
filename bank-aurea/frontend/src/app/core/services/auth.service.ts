import { Injectable, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { tap, catchError, of, Observable } from 'rxjs';

export interface User {
  username: string;
  is_admin: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private apiUrl = 'http://127.0.0.1:5001/auth';

  currentUser = signal<User | null>(null);

  constructor() {
    // Check session on load (optional, or call /me)
    this.checkSession();
  }

  checkSession() {
    return this.http.get<User>(`${this.apiUrl}/me`, { withCredentials: true }).subscribe({
      next: (user) => this.currentUser.set(user),
      error: () => this.currentUser.set(null)
    });
  }

  login(credentials: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/login`, credentials, { withCredentials: true }).pipe(
      tap((res: any) => {
        if (res.success) {
          this.currentUser.set({ username: res.user, is_admin: res.is_admin });
          this.router.navigate(['/dashboard']);
        }
      })
    );
  }

  register(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, data, { withCredentials: true });
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
