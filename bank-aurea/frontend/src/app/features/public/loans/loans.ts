import { Component } from '@angular/core';
import { NavbarComponent } from '../../../core/components/navbar/navbar';
import { FooterComponent } from '../../../core/components/footer/footer';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-loans',
  standalone: true,
  imports: [NavbarComponent, FooterComponent, RouterModule],
  templateUrl: './loans.html',
  styleUrl: './loans.scss',
})
export class LoansComponent {

}
