import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Business } from './business';

describe('Business', () => {
  let component: Business;
  let fixture: ComponentFixture<Business>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Business]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Business);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
