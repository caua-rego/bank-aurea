import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { LoginComponent } from './features/login/login.component';
import { RegisterComponent } from './features/register/register.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { HomeComponent } from './features/home/home.component';
import { AdminComponent } from './features/admin/admin';
import { adminGuard } from './core/guards/admin-guard';

import { PrivacyComponent } from './features/legal/privacy/privacy';
import { TermsComponent } from './features/legal/terms/terms';

import { LoansComponent } from './features/public/loans/loans';
import { CreditCardsComponent } from './features/public/credit-cards/credit-cards';
import { InvestmentsComponent } from './features/public/investments/investments';
import { BusinessComponent } from './features/public/business/business';
import { ContactComponent } from './features/public/contact/contact';
import { OverviewComponent } from './features/dashboard/overview/overview.component';
import { CardsComponent } from './features/cards/cards.component';
import { SettingsComponent } from './features/settings/settings.component';

export const routes: Routes = [
    { path: '', component: HomeComponent },
    { path: 'login', component: LoginComponent },
    { path: 'register', component: RegisterComponent },
    { path: 'privacy', component: PrivacyComponent },
    { path: 'terms', component: TermsComponent },

    // New Public Routes
    { path: 'loans', component: LoansComponent },
    { path: 'credit-cards', component: CreditCardsComponent },
    { path: 'investments', component: InvestmentsComponent },
    { path: 'business', component: BusinessComponent },
    { path: 'contact', component: ContactComponent },

    {
        path: 'dashboard',
        component: DashboardComponent,
        canActivate: [authGuard],
        children: [
            { path: '', component: OverviewComponent },
            { path: 'cards', component: CardsComponent },
            { path: 'settings', component: SettingsComponent }
        ]
    },
    {
        path: 'admin',
        component: AdminComponent,
        canActivate: [adminGuard]
    },
    { path: '**', redirectTo: '' }
];
