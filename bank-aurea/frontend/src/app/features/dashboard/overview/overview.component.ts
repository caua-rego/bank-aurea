import { Component, inject, signal } from '@angular/core';
import { CommonModule, CurrencyPipe, DatePipe, TitleCasePipe, UpperCasePipe } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { TransactionService, DashboardData } from '../../../core/services/transaction.service';
import { AuthService } from '../../../core/services/auth.service';
import { CardService, Card } from '../../../core/services/card.service';

@Component({
    selector: 'app-overview',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule, CurrencyPipe, DatePipe, TitleCasePipe, UpperCasePipe, RouterModule],
    template: `
    <header class="top-header">
        <h1>Overview</h1>
        <div class="date-display">{{ today | date:'fullDate' }}</div>
    </header>

    <div class="content-grid">
        <!-- LEFT COLUMN: CARD & ACTIONS -->
        <div class="left-col">
            <div class="account-info liquid-panel">
                <div class="label">Your Account</div>
                <div class="account-number">{{ data()?.account?.number }}</div>
                <div class="account-id">ID: {{ data()?.account?.id ?? '—' }}</div>
                <button class="btn-copy" (click)="copyAccountDetails()">Copy Details</button>
            </div>

            <!-- CREDIT CARD OR PLACEHOLDER -->
            <div class="credit-card-container">
                @if (data()?.card) {
                    <div class="credit-card" 
                         [ngClass]="(data()?.card?.tier || 'free')"
                         (click)="openActionModal(data()?.card)">
                        <div class="card-chip"></div>
                        <div class="card-logo">AURÉA <span class="card-type">{{ (data()?.card?.tier || 'free') | uppercase }}</span></div>
                        <div class="card-number">{{ data()?.card?.number || '•••• •••• •••• ••••' }}</div>
                        <div class="card-details">
                            <div class="group">
                                <span class="label">Holder</span>
                                <span class="value">{{ data()?.card?.holder || 'MEMBER' }}</span>
                            </div>
                            <div class="group">
                                <span class="label">Expires</span>
                                <span class="value">{{ data()?.card?.expiry || '00/00' }}</span>
                            </div>
                        </div>
                    </div>
                } @else {
                    <div class="credit-card placeholder" routerLink="/dashboard/cards">
                        <div class="content">
                            <span class="plus">+</span>
                            <span class="text">Activate Your Card</span>
                        </div>
                    </div>
                }
            </div>

            <!-- QUICK ACTIONS -->
            <div class="quick-actions liquid-panel">
                <h3>Quick Actions</h3>
                <div class="action-buttons">
                    <button (click)="setAction('deposit')" [class.active]="activeAction() === 'deposit'">
                        <span class="icon">↓</span> Deposit
                    </button>
                    <button (click)="setAction('withdraw')" [class.active]="activeAction() === 'withdraw'">
                        <span class="icon">↑</span> Withdraw
                    </button>
                    <button (click)="setAction('transfer')" [class.active]="activeAction() === 'transfer'">
                        <span class="icon">→</span> Transfer
                    </button>
                </div>

                <!-- DYNAMIC ACTION FORM -->
                @if (activeAction()) {
                <div class="action-form page-fade-in">
                    <h4>{{ activeAction() | titlecase }} Funds</h4>
                    
                    @if (activeAction() === 'transfer') {
                        <form [formGroup]="transferForm" (ngSubmit)="onTransfer()">
                            <input type="text" formControlName="target_account" placeholder="Recipient Account #">
                            <input type="number" formControlName="amount" placeholder="Amount">
                            <button type="submit" class="btn-action">Send Transfer</button>
                        </form>
                    } @else {
                        <form [formGroup]="amountForm" (ngSubmit)="activeAction() === 'deposit' ? onDeposit() : onWithdraw()">
                            <input type="number" formControlName="amount" placeholder="Amount">
                            <button type="submit" class="btn-action">
                                Confirm {{ activeAction() | titlecase }}
                            </button>
                        </form>
                    }
                </div>
                }
                
                @if (message) {
                    <div class="status-toast">{{ message }}</div>
                }
            </div>
        </div>

        <!-- RIGHT COLUMN: STATS & TRANSACTIONS -->
        <div class="right-col">
            <!-- BALANCE CARD -->
            <div class="balance-card liquid-panel">
                <span class="label">Total Balance</span>
                <div class="amount">{{ data()?.account?.balance ?? 0 | currency:'USD' }}</div>
                <div class="trend positive">
                    <span>+2.4%</span> this month
                </div>
            </div>

            <!-- TRANSACTIONS LIST -->
            <div class="transactions-panel liquid-panel">
                <div class="panel-header">
                    <h3>Recent Activity</h3>
                    <button class="view-all">View All</button>
                </div>

                <div class="tx-list">
                    @for (tx of data()?.transactions; track tx.id) {
                    <div class="tx-item">
                        <div class="tx-icon" [class.in]="tx.type === 'deposit'" [class.out]="tx.type !== 'deposit'">
                            {{ tx.type === 'deposit' ? '↓' : '↑' }}
                        </div>
                        <div class="tx-info">
                            <span class="tx-type">{{ tx.type | titlecase }}</span>
                            <span class="tx-date">ID #{{ tx.id }} · {{ tx.timestamp | date:'MMM d, h:mm a' }}</span>
                        </div>
                        <div class="tx-amount" [class.pos]="tx.type === 'deposit'">
                            {{ tx.type === 'deposit' ? '+' : '-' }}{{ tx.amount | currency:'USD' }}
                        </div>
                    </div>
                    } @empty {
                        <div class="empty-state">No recent activity</div>
                    }
                </div>
            </div>
        </div>
    </div>

    <!-- ACTION MODAL (DELETE/VIEW) -->
    @if (selectedCardForAction()) {
        <div class="modal-overlay page-fade-in" (click)="closeActionModal()">
            <div class="modal-content" (click)="$event.stopPropagation()">
                
                @if (showSensitiveData()) {
                    <!-- SENSITIVE DATA VIEW -->
                    <h3>Card Details</h3>
                    <div class="sensitive-info">
                        <div class="row">
                            <label>Number:</label>
                            <span class="val monospace">{{ selectedCardForAction()!.number }}</span>
                        </div>
                        <div class="row">
                            <label>CVV:</label>
                            <span class="val">{{ selectedCardForAction()!.cvv || '***' }}</span>
                        </div>
                        <div class="row">
                            <label>Expiry:</label>
                            <span class="val">{{ selectedCardForAction()!.expiry }}</span>
                        </div>
                        <div class="row">
                            <label>Tier:</label>
                            <span class="val">{{ selectedCardForAction()!.tier | uppercase }}</span>
                        </div>
                    </div>
                    <button class="btn-secondary" (click)="closeActionModal()">Close</button>
                } @else {
                    <!-- ACTION MENU -->
                    <h3>Manage Card</h3>
                    <div class="card-preview-mini">
                        ending in {{ selectedCardForAction()!.number | slice:-4 }}
                    </div>
                    
                    <div class="options vertical">
                        <div class="option" (click)="revealDetails()">
                            <span class="emoji">👁️</span>
                            <span class="lbl-main">View Details</span>
                        </div>
                        <div class="option danger" (click)="deleteExposedCard()">
                            <span class="emoji">🗑️</span>
                            <span class="lbl-main">Delete Card</span>
                        </div>
                    </div>
                }
            </div>
        </div>
    }

    <!-- LOADING OVERLAY -->
    @if (loading()) {
        <div class="loading-overlay page-fade-in">
            <div class="spinner"></div>
            <div class="loading-text">Processing...</div>
        </div>
    }
    `,
    styleUrls: ['../dashboard.component.scss']
})
export class OverviewComponent {
    private transactionService = inject(TransactionService);
    private authService = inject(AuthService);
    private cardService = inject(CardService);
    private fb = inject(FormBuilder);
    private route = inject(ActivatedRoute);

    today = new Date();
    data = signal<DashboardData | null>(null);

    // Action State
    activeAction = signal<'deposit' | 'withdraw' | 'transfer' | null>(null);
    loading = signal(false);
    message = '';

    // Card Action State
    selectedCardForAction = signal<any | null>(null); // Using any temporarily to avoid strict type mismatch if DashboardData.card != Card
    showSensitiveData = signal(false);

    amountForm = this.fb.group({ amount: ['', [Validators.required, Validators.min(0.01)]] });
    transferForm = this.fb.group({
        target_account: ['', Validators.required],
        amount: ['', [Validators.required, Validators.min(0.01)]]
    });

    constructor() {
        this.loadData();
        this.route.queryParams.subscribe(params => {
            if (params['action']) {
                this.setAction(params['action']);
            }
        });
    }

    loadData() {
        this.transactionService.getDashboard().subscribe({
            next: (res) => this.data.set(res),
            error: (err) => console.error(err)
        });
    }

    setAction(action: 'deposit' | 'withdraw' | 'transfer') {
        if (this.activeAction() === action) {
            this.activeAction.set(null);
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

    // --- CARD ACTIONS ---
    openActionModal(card: any) {
        if (!card || !card.id) return;
        this.selectedCardForAction.set(card);
        this.showSensitiveData.set(false);
        this.message = '';
    }

    closeActionModal() {
        this.selectedCardForAction.set(null);
        this.showSensitiveData.set(false);
    }

    revealDetails() {
        const card = this.selectedCardForAction();
        if (!card || !card.id) return;

        this.loading.set(true);
        this.cardService.getCardDetails(card.id).subscribe({
            next: (fullCard) => {
                this.selectedCardForAction.set(fullCard);
                this.showSensitiveData.set(true);
                this.loading.set(false);
            },
            error: (err) => {
                console.error(err);
                this.loading.set(false);
                this.message = 'Failed to load card details';
            }
        });
    }

    deleteExposedCard() {
        const card = this.selectedCardForAction();
        if (!card || !card.id) return;

        if (!confirm('Are you sure you want to delete this card? This action cannot be undone.')) return;

        this.loading.set(true);
        this.cardService.deleteCard(card.id).subscribe({
            next: () => {
                this.loading.set(false);
                this.closeActionModal();
                this.loadData(); // Refresh dashboard data
                this.message = 'Card deleted successfully';
            },
            error: (err) => {
                console.error(err);
                this.loading.set(false);
                this.message = 'Failed to delete card';
                this.closeActionModal();
            }
        });
    }

    copyAccountDetails() {
        const number = this.data()?.account?.number;
        const id = this.data()?.account?.id;
        if (!number) return;
        const text = `Account Number: ${number}${id ? `\nAccount ID: ${id}` : ''}`;
        navigator.clipboard?.writeText(text).catch(() => {});
        this.message = 'Account details copied';
        setTimeout(() => this.message = '', 1500);
    }
}
