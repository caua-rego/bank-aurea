import { Component } from '@angular/core';
import { NavbarComponent } from '../../../core/components/navbar/navbar';
import { FooterComponent } from '../../../core/components/footer/footer';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [NavbarComponent, FooterComponent, RouterModule],
  templateUrl: './contact.html',
  styleUrl: './contact.scss',
})
export class ContactComponent {

}
