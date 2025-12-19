import { Component, inject, signal } from '@angular/core';
import { CommonModule, UpperCasePipe } from '@angular/common';
import { CardService, Card } from '../../core/services/card.service';

@Component({
    selector: 'app-cards',
    standalone: true,
    imports: [CommonModule, UpperCasePipe],
    template: `
    <div class="cards-page page-fade-in">
        <h2 class="page-title">My Cards</h2>
        
        <!-- ERROR MESSAGE -->
        @if (errorMessage()) {
            <div class="error-banner page-fade-in">
                {{ errorMessage() }}
            </div>
        }

        <div class="cards-grid">
            @for (card of cards(); track card.id) {
                <div class="credit-card" [ngClass]="card.tier" (click)="openActionModal(card)">
                    <div class="card-chip"></div>
                    <div class="card-logo">AURÉA <span class="card-type">{{ card.tier | uppercase }}</span></div>
                    <div class="card-number">{{ card.number }}</div>
                    <div class="card-details">
                        <span class="value">{{ card.holder_name }}</span>
                        <span class="value">{{ card.expiry }}</span>
                    </div>
                    @if (card.card_type === 'physical') {
                        <div class="phys-tag">PHYSICAL</div>
                    }
                </div>
            }

            <!-- ADD NEW CARD -->
            <div class="add-card" (click)="openCreateFlow()">
                <div class="plus">+</div>
                <span>New Card</span>
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

        <!-- TYPE SELECTOR MODAL -->
        @if (showTypeSelector()) {
            <div class="modal-overlay page-fade-in" (click)="closeCreateFlow()">
                <div class="modal-content" (click)="$event.stopPropagation()">
                    <h3>Select Card Type</h3>
                    <div class="options">
                        <div class="option" (click)="confirmCreate('virtual')">
                            <span class="emoji">📱</span>
                            <span class="lbl-main">Virtual</span>
                            <span class="lbl-sub">Instant use online</span>
                        </div>
                        <div class="option" (click)="confirmCreate('physical')">
                            <span class="emoji">💳</span>
                            <span class="lbl-main">Physical</span>
                            <span class="lbl-sub">Metal card mailed to you</span>
                        </div>
                    </div>
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
    </div>
  `,
    styles: [`
    .cards-page { padding: 40px; color: white; }
    .page-title { font-size: 2rem; margin-bottom: 40px; }
    .cards-grid { display: flex; gap: 30px; flex-wrap: wrap; }

    .error-banner {
        background: rgba(220, 53, 69, 0.2);
        border: 1px solid #dc3545;
        color: #ff6b6b;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .credit-card {
        width: 340px;
        height: 215px;
        background: linear-gradient(135deg, #2c2c2e 0%, #000000 100%);
        border-radius: 20px;
        padding: 30px;
        box-sizing: border-box;
        position: relative;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        transition: transform 0.3s;
        cursor: pointer;

        &:hover { transform: translateY(-5px); }
        // ... (Styles same as previous, simplified for brevity but will be injected)
        // I will assume the previous styles for .credit-card are kept or I need to re-include them all?
        // REPLACE CONTENT replaces lines, so I must include all styles if I replace the whole Component block.
        // Wait, I am replacing from @Component... so yes.
        
        // RE-INCLUDING STYLES TO BE SAFE
        .card-chip {
            width: 45px;
            height: 32px;
            background: linear-gradient(135deg, #d4a017 0%, #f1c40f 100%);
            border-radius: 6px;
            margin-bottom: 40px;
        }
        .card-logo {
            position: absolute;
            top: 30px;
            right: 30px;
            font-weight: 700;
            color: white;
            letter-spacing: 1px;
            .card-type { font-weight: 300; color: rgba(255,255,255,0.7); font-size: 0.8rem; margin-left: 5px; }
        }
        .card-number {
            font-family: monospace;
            font-size: 1.5rem;
            color: white;
            letter-spacing: 2px;
            margin-bottom: 30px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }
        .card-details {
            display: flex;
            justify-content: space-between;
            text-transform: uppercase;
            font-size: 0.9rem;
            letter-spacing: 1px;
        }

        &.gold {
            background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%);
            border: none;
            color: black;
            .card-logo, .card-number, .card-details { color: #3d2b00; }
            .card-type { color: rgba(0,0,0,0.6); }
            .card-chip { background: linear-gradient(135deg, #fff 0%, #eee 100%); }
        }
        &.titanium { background: linear-gradient(135deg, #2c2c2e 0%, #000000 100%); }
        &.adamantium {
            background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
            border: 1px solid rgba(100, 255, 218, 0.3);
            box-shadow: 0 0 20px rgba(100, 255, 218, 0.1);
            .card-logo { color: #64ffda; }
            .card-type { color: #64ffda; }
            .card-chip { background: linear-gradient(135deg, #64ffda 0%, #1a1a1a 100%); }
        }
        &.free { background: linear-gradient(135deg, #444 0%, #222 100%); }
    }

    .add-card {
        width: 340px;
        height: 215px;
        border: 2px dashed rgba(255,255,255,0.2);
        border-radius: 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        transition: all 0.2s;
        color: rgba(255,255,255,0.5);
        &:hover {
            border-color: rgba(255,255,255,0.4);
            color: white;
            background: rgba(255,255,255,0.05);
        }
        .plus { font-size: 3rem; margin-bottom: 10px; }
    }

    .modal-overlay, .loading-overlay {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.8);
        backdrop-filter: blur(5px);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
        flex-direction: column;
    }

    .modal-content {
        background: #1c1c1e;
        border: 1px solid #333;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        width: 90%;
        max-width: 400px;
        color: white;

        h3 { margin-top: 0; margin-bottom: 20px; }
        
        .options {
            display: flex;
            gap: 15px;
            &.vertical { flex-direction: column; }
            
            .option {
                flex: 1;
                background: #2c2c2e;
                padding: 20px;
                border-radius: 12px;
                cursor: pointer;
                transition: all 0.2s;
                border: 1px solid transparent;
                display: flex;
                align-items: center;
                gap: 15px; /* for side by side icon */
                
                &:hover {
                    background: #3a3a3c;
                    border-color: #d4a017;
                    transform: translateY(-2px);
                }
                &.danger:hover {
                    border-color: #dc3545;
                    background: rgba(220, 53, 69, 0.1);
                }

                .emoji { font-size: 1.5rem; }
                .lbl-main { font-weight: bold; color: white; }
                .lbl-sub { display: block; font-size: 0.8rem; color: #888; }
            }
        }

        .sensitive-info {
            background: #2c2c2e;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: left;
            
            .row {
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
                label { color: #888; }
                .val { font-weight: bold; color: white; }
                .val.monospace { font-family: monospace; letter-spacing: 1px; }
            }
        }
        
        .btn-secondary {
            background: transparent;
            border: 1px solid #555;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            &:hover { border-color: white; }
        }

        .card-preview-mini {
            margin-bottom: 20px;
            color: #888;
            font-size: 0.9rem;
        }
    }

    .loading-text { margin-top: 20px; font-size: 1.2rem; color: #d4a017; animation: pulse 1.5s infinite; }
    .spinner { width: 50px; height: 50px; border: 3px solid rgba(212, 160, 23, 0.3); border-radius: 50%; border-top-color: #d4a017; animation: spin 1s ease-in-out infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    .phys-tag { position: absolute; bottom: 10px; right: 20px; font-size: 0.6rem; background: rgba(255,255,255,0.2); padding: 4px 8px; border-radius: 4px; color: white; }
    `]
})
export class CardsComponent {
    cardService = inject(CardService);
    cards = signal<Card[]>([]);

    loading = signal(false);
    showTypeSelector = signal(false);
    errorMessage = signal<string>('');

    // Action Logic
    selectedCardForAction = signal<Card | null>(null);
    showSensitiveData = signal(false);

    constructor() {
        this.loadCards();
    }

    loadCards() {
        this.cardService.getCards().subscribe(res => {
            this.cards.set(res);
        });
    }

    // Modal Triggers
    openCreateFlow() {
        this.errorMessage.set('');
        this.showTypeSelector.set(true);
    }

    closeCreateFlow() {
        this.showTypeSelector.set(false);
    }

    // Action Modal Logic
    openActionModal(card: Card) {
        this.selectedCardForAction.set(card);
        this.showSensitiveData.set(false);
        this.errorMessage.set('');
    }

    closeActionModal() {
        this.selectedCardForAction.set(null);
        this.showSensitiveData.set(false);
    }

    revealDetails() {
        const card = this.selectedCardForAction();
        if (!card) return;

        this.loading.set(true);
        this.cardService.getCardDetails(card.id).subscribe({
            next: (fullCard) => {
                this.selectedCardForAction.set(fullCard); // Contains full number/cvv
                this.showSensitiveData.set(true);
                this.loading.set(false);
            },
            error: (err) => {
                this.loading.set(false);
                this.closeActionModal();
                this.errorMessage.set('Failed to load card details.');
            }
        });
    }

    deleteExposedCard() {
        const card = this.selectedCardForAction();
        if (!card) return;

        if (!confirm('Are you sure you want to delete this card? This action cannot be undone.')) return;

        this.loading.set(true);
        this.cardService.deleteCard(card.id).subscribe({
            next: () => {
                this.cards.update(list => list.filter(c => c.id !== card.id));
                this.loading.set(false);
                this.closeActionModal();
            },
            error: (err) => {
                this.loading.set(false);
                this.closeActionModal();
                this.errorMessage.set(err.error?.error || 'Failed to delete card.');
            }
        });
    }

    confirmCreate(type: 'virtual' | 'physical') {
        this.showTypeSelector.set(false);
        this.loading.set(true);
        this.errorMessage.set('');

        const minTime = new Promise(resolve => setTimeout(resolve, 1500));
        const apiCall = new Promise<Card>((resolve, reject) => {
            this.cardService.createCard(type).subscribe({
                next: (res) => resolve(res),
                error: (err) => reject(err)
            });
        });

        Promise.all([minTime, apiCall]).then(([_, newCard]) => {
            this.cards.update(c => [...c, newCard as Card]);
            this.loading.set(false);
            this.showTypeSelector.set(false);
        }).catch(err => {
            console.error('Error creating card:', err);
            this.loading.set(false);
            this.showTypeSelector.set(false);
            if (err.error && err.error.error) {
                this.errorMessage.set(err.error.error);
            } else {
                this.errorMessage.set('Failed to create card. Please try again.');
            }
        });
    }
}
