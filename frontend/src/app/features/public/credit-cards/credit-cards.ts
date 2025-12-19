import { Component } from '@angular/core';
import { NavbarComponent } from '../../../core/components/navbar/navbar';
import { FooterComponent } from '../../../core/components/footer/footer';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-credit-cards',
  standalone: true,
  imports: [NavbarComponent, FooterComponent, RouterModule],
  templateUrl: './credit-cards.html',
  styleUrl: './credit-cards.scss',
})
export class CreditCardsComponent {

}
