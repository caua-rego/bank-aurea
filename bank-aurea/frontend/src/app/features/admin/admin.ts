import { Component, inject, signal } from '@angular/core';
import { CommonModule, CurrencyPipe } from '@angular/common';
import { AdminService, AdminDashboardData } from '../../core/services/admin.service';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule, CurrencyPipe],
  templateUrl: './admin.html',
  styleUrls: ['./admin.scss']
})
export class AdminComponent {
  private adminService = inject(AdminService);

  data = signal<AdminDashboardData | null>(null);

  constructor() {
    this.adminService.getDashboard().subscribe({
      next: (res) => this.data.set(res),
      error: (err) => console.error('Admin Load Failed', err)
    });
  }
}
