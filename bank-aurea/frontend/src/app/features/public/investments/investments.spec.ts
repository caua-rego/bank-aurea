import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Investments } from './investments';

describe('Investments', () => {
  let component: Investments;
  let fixture: ComponentFixture<Investments>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Investments]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Investments);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
