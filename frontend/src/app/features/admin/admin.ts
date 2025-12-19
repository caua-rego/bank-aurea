import { Component, inject, signal } from '@angular/core';
import { CommonModule, CurrencyPipe } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { AdminService, AdminDashboardData, UserDTO } from '../../core/services/admin.service';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule, CurrencyPipe, ReactiveFormsModule],
  templateUrl: './admin.html',
  styleUrls: ['./admin.scss']
})
export class AdminComponent {
  private adminService = inject(AdminService);
  private fb = inject(FormBuilder);

  data = signal<AdminDashboardData | null>(null);
  editingUser = signal<UserDTO | null>(null);
  message = signal('');

  editForm = this.fb.group({
    username: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    balance: ['', Validators.required],
    is_admin: [false]
  });

  constructor() {
    this.load();
  }

  load() {
    this.adminService.getDashboard().subscribe({
      next: (res) => this.data.set(res),
      error: (err) => console.error('Admin Load Failed', err)
    });
  }

  openEdit(user: UserDTO) {
    this.editingUser.set(user);
    this.editForm.patchValue({
      username: user.username,
      email: user.email,
      balance: user.balance,
      is_admin: user.is_admin
    });
    this.message.set('');
  }

  closeEdit() {
    this.editingUser.set(null);
    this.message.set('');
  }

  saveEdit() {
    const user = this.editingUser();
    if (!user || this.editForm.invalid) return;

    this.adminService.updateUser(user.id, this.editForm.value).subscribe({
      next: (updated) => {
        this.message.set('User updated');
        this.closeEdit();
        this.load();
      },
      error: (err) => {
        console.error(err);
        this.message.set(err.error?.error || 'Failed to update');
      }
    });
  }
}
