import { Component } from '@angular/core';
import { NavbarComponent } from '../../../core/components/navbar/navbar';
import { FooterComponent } from '../../../core/components/footer/footer';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-investments',
  standalone: true,
  imports: [NavbarComponent, FooterComponent, RouterModule],
  templateUrl: './investments.html',
  styleUrl: './investments.scss',
})
export class InvestmentsComponent {

}
