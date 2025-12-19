import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Card {
    id: number;
    number: string;
    holder_name: string;
    expiry: string;
    card_type: 'virtual' | 'physical';
    tier: 'free' | 'gold' | 'titanium' | 'adamantium';
    cvv?: string;
}

@Injectable({
    providedIn: 'root'
})
export class CardService {
    private http = inject(HttpClient);
    private apiUrl = 'http://localhost:5001/cards';

    getCards(): Observable<Card[]> {
        return this.http.get<Card[]>(`${this.apiUrl}/`, { withCredentials: true });
    }

    createCard(type: 'virtual' | 'physical' = 'virtual'): Observable<Card> {
        return this.http.post<Card>(`${this.apiUrl}/generate`, { type }, { withCredentials: true });
    }

    deleteCard(id: number): Observable<any> {
        return this.http.delete(`${this.apiUrl}/${id}`, { withCredentials: true });
    }

    getCardDetails(id: number): Observable<Card> {
        return this.http.get<Card>(`${this.apiUrl}/${id}/reveal`, { withCredentials: true });
    }
}
