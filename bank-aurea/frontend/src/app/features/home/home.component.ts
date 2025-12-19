import { Component, ElementRef, HostListener, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavbarComponent } from '../../core/components/navbar/navbar';
import { FooterComponent } from '../../core/components/footer/footer';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, NavbarComponent, FooterComponent],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent {
  @ViewChild('card', { static: true })
  private cardElement?: ElementRef<HTMLElement>;

  private readonly baseTiltX = 10;
  private readonly baseTiltY = -10;
  private readonly maxTilt = 14;
  private readonly resetDebounceMs = 120;
  private resetTimeout?: number;

  glowX = '50%';
  glowY = '50%';
  glowStrength = '0.7';
  isCardHover = false;

  cardGlowX = '50%';
  cardGlowY = '50%';
  cardGlowStrength = '0.9';

  tiltX = `${this.baseTiltX}deg`;
  tiltY = `${this.baseTiltY}deg`;

  scrollTo(section: string) {
    document.getElementById(section)?.scrollIntoView({ behavior: 'smooth' });
  }

  @HostListener('window:pointermove', ['$event'])
  handleCardPointerMove(event: PointerEvent) {
    const card = this.cardElement?.nativeElement;
    if (!card) return;

    if (this.resetTimeout) {
      window.clearTimeout(this.resetTimeout);
      this.resetTimeout = undefined;
    }

    this.glowX = `${(event.clientX / window.innerWidth) * 100}%`;
    this.glowY = `${(event.clientY / window.innerHeight) * 100}%`;

    if (this.isCardHover) {
      const rect = card.getBoundingClientRect();
      const relX = ((event.clientX - rect.left) / rect.width) * 100;
      const relY = ((event.clientY - rect.top) / rect.height) * 100;
      this.cardGlowX = `${Math.max(0, Math.min(100, relX))}%`;
      this.cardGlowY = `${Math.max(0, Math.min(100, relY))}%`;
    }

    const rect = card.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    const relativeX = (event.clientX - centerX) / (window.innerWidth / 2);
    const relativeY = (event.clientY - centerY) / (window.innerHeight / 2);

    const clampedX = Math.max(-1, Math.min(1, relativeX));
    const clampedY = Math.max(-1, Math.min(1, relativeY));

    const rotateX = this.baseTiltX - clampedY * this.maxTilt;
    const rotateY = this.baseTiltY + clampedX * this.maxTilt;

    this.tiltX = `${rotateX.toFixed(2)}deg`;
    this.tiltY = `${rotateY.toFixed(2)}deg`;
  }

  @HostListener('window:pointerleave')
  resetCardTilt() {
    this.resetTimeout = window.setTimeout(() => {
      this.tiltX = `${this.baseTiltX}deg`;
      this.tiltY = `${this.baseTiltY}deg`;
      this.glowStrength = '0.7';
    }, this.resetDebounceMs);
  }

  onCardEnter() {
    this.isCardHover = true;
    this.glowStrength = '0.7';
    this.cardGlowStrength = '1';
  }

  onCardLeave() {
    this.isCardHover = false;
    this.glowStrength = '0.7';
    this.cardGlowStrength = '0';
  }
}
