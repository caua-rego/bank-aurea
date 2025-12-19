import { Component } from '@angular/core';
import { NavbarComponent } from '../../../core/components/navbar/navbar';
import { FooterComponent } from '../../../core/components/footer/footer';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-business',
  standalone: true,
  imports: [NavbarComponent, FooterComponent, RouterModule],
  templateUrl: './business.html',
  styleUrl: './business.scss',
})
export class BusinessComponent {

}
