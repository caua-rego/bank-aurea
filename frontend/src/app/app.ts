import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('frontend');
  showCookieConsent = signal(false);

  constructor() {
    const consent = localStorage.getItem('cookieConsent');
    if (!consent) {
      this.showCookieConsent.set(true);
    }
  }

  acceptCookies() {
    localStorage.setItem('cookieConsent', 'true');
    this.showCookieConsent.set(false);
  }
}
