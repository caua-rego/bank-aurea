import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface AdminStats {
    total_users: number;
    total_reservs: string;
}

export interface UserDTO {
    id: number;
    username: string;
    email: string;
    is_admin: boolean;
    balance: string;
}

export interface AdminDashboardData {
    stats: AdminStats;
    users: UserDTO[];
}

@Injectable({
    providedIn: 'root',
})
export class AdminService {
    private http = inject(HttpClient);
    private apiUrl = 'http://127.0.0.1:5001/admin';

    getDashboard(): Observable<AdminDashboardData> {
        return this.http.get<AdminDashboardData>(`${this.apiUrl}/`, { withCredentials: true });
    }
}
