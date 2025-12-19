import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreditCards } from './credit-cards';

describe('CreditCards', () => {
  let component: CreditCards;
  let fixture: ComponentFixture<CreditCards>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreditCards]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreditCards);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
