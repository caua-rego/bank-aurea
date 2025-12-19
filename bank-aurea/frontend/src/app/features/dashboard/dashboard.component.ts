import { Component, inject, signal } from '@angular/core';
import { CommonModule, CurrencyPipe, DatePipe, TitleCasePipe, SlicePipe, UpperCasePipe } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { TransactionService, DashboardData } from '../../core/services/transaction.service';
import { AuthService } from '../../core/services/auth.service';
import { Router } from '@angular/router';
import { FooterComponent } from '../../core/components/footer/footer';
import { NavbarComponent } from '../../core/components/navbar/navbar';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, CurrencyPipe, DatePipe, TitleCasePipe, FooterComponent, NavbarComponent],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent {
  private transactionService = inject(TransactionService);
  private authService = inject(AuthService);
  private fb = inject(FormBuilder);

  // Data Signal
  data = signal<DashboardData | null>(null);
  user = this.authService.currentUser;

  // Action State
  activeAction = signal<'deposit' | 'withdraw' | 'transfer' | null>(null);
  message = '';
  loading = false; // Added loading state

  amountForm = this.fb.group({ amount: ['', [Validators.required, Validators.min(0.01)]] });
  transferForm = this.fb.group({
    target_account: ['', Validators.required],
    amount: ['', [Validators.required, Validators.min(0.01)]]
  });

  constructor() {
    this.loadData();
  }

  loadData() {
    this.transactionService.getDashboard().subscribe({
      next: (res) => this.data.set(res),
      error: (err) => console.error(err)
    });
  }

  setAction(action: 'deposit' | 'withdraw' | 'transfer') {
    if (this.activeAction() === action) {
      this.activeAction.set(null); // Toggle off
    } else {
      this.activeAction.set(action);
      this.message = '';
      this.amountForm.reset();
      this.transferForm.reset();
    }
  }

  onDeposit() {
    if (this.amountForm.invalid) return;
    this.transactionService.deposit(this.amountForm.value.amount!).subscribe({
      next: (res) => this.handleSuccess(res),
      error: (err) => this.message = err.error?.error || 'Failed'
    });
  }

  onWithdraw() {
    if (this.amountForm.invalid) return;
    this.transactionService.withdraw(this.amountForm.value.amount!).subscribe({
      next: (res) => this.handleSuccess(res),
      error: (err) => this.message = err.error?.error || 'Failed'
    });
  }

  onTransfer() {
    if (this.transferForm.invalid) return;
    const { target_account, amount } = this.transferForm.value;
    this.transactionService.transfer(target_account!, amount!).subscribe({
      next: (res) => this.handleSuccess(res),
      error: (err) => this.message = err.error?.error || 'Failed'
    });
  }

  handleSuccess(res: any) {
    this.message = res.message || 'Success';
    this.loadData();
    setTimeout(() => {
      this.message = '';
      this.activeAction.set(null);
    }, 2000);
  }

  logout() {
    this.authService.logout();
  }
}
