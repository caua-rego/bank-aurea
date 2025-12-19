import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Transaction {
  id: number;
  amount: string;
  type: string;
  timestamp: string;
  source: number | string;
  target: number | string;
}

export interface DashboardData {
  account: {
    number: string;
    balance: string;
  };
  card: {
    number: string;
    holder: string;
    expiry: string;
    cvv: string;
  };
  transactions: Transaction[];
}

@Injectable({
  providedIn: 'root',
})
export class TransactionService {
  private http = inject(HttpClient);
  private apiUrl = 'http://127.0.0.1:5001/main';

  getDashboard(): Observable<DashboardData> {
    return this.http.get<DashboardData>(`${this.apiUrl}/dashboard`, { withCredentials: true });
  }

  transfer(targetAccount: string, amount: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/transfer`, { target_account: targetAccount, amount }, { withCredentials: true });
  }

  deposit(amount: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/deposit`, { amount }, { withCredentials: true });
  }

  withdraw(amount: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/withdraw`, { amount }, { withCredentials: true });
  }
}
