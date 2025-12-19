import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../core/services/auth.service';

@Component({
    selector: 'app-settings',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule],
    template: `
    <div class="settings-page page-fade-in">
        <h2 class="page-title">Settings</h2>

        <div class="settings-grid">
            <!-- PROFILE CARD -->
            <div class="liquid-panel profile-section">
                <h3>Profile</h3>
                <div class="avatar-large" [style.backgroundImage]="'url(' + (auth.currentUser()?.profile_image || '') + ')'">
                    @if (!auth.currentUser()?.profile_image) {
                        <span>{{ auth.currentUser()?.username?.charAt(0) | uppercase }}</span>
                    }
                </div>
                
                <form [formGroup]="profileForm" (ngSubmit)="updateProfile()">
                    <div class="form-group">
                        <label>Profile Image</label>
                        <input type="file" (change)="onFileSelected($event)" accept="image/*">
                    </div>
                    <button type="submit" class="btn-primary">Save Changes</button>
                    
                    @if (message) {
                        <div class="status-msg">{{ message }}</div>
                    }
                </form>
            </div>

            <!-- PREFERENCES -->
            <div class="liquid-panel prefs-section">
                <h3>Preferences</h3>
                <div class="pref-item">
                    <span>Dark Mode</span>
                    <div class="toggle active"></div>
                </div>
                <div class="pref-item">
                    <span>Email Notifications</span>
                    <div class="toggle active"></div>
                </div>
                <div class="pref-item">
                    <span>2FA Authentication</span>
                    <div class="toggle"></div>
                </div>
            </div>
        </div>
    </div>
  `,
    styles: [`
    .settings-page { padding: 40px; color: white; }
    .page-title { font-size: 2rem; margin-bottom: 40px; }
    
    .settings-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 30px;
    }

    .liquid-panel {
        background: rgba(20, 20, 20, 0.6);
        backdrop-filter: blur(40px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 30px;
    }

    h3 { margin-top: 0; margin-bottom: 25px; font-size: 1.2rem; }

    .avatar-large {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background-color: #d4a017;
        margin: 0 auto 30px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 2.5rem;
        font-weight: 700;
        background-size: cover;
        background-position: center;
        border: 4px solid rgba(255,255,255,0.1);
    }

    .form-group {
        margin-bottom: 20px;
        
        label { display: block; margin-bottom: 10px; color: #aaa; font-size: 0.9rem; }
        input {
            width: 100%;
            padding: 12px;
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            color: white;
            box-sizing: border-box;

            &:focus { outline: none; border-color: #d4a017; }
        }
    }

    .btn-primary {
        width: 100%;
        padding: 12px;
        background: white;
        color: black;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        
        &:hover { background: #eee; }
    }

    .status-msg { margin-top: 15px; color: #2ecc71; text-align: center; }

    .pref-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);

        &:last-child { border-bottom: none; }
    }

    .toggle {
        width: 44px;
        height: 24px;
        background: #333;
        border-radius: 12px;
        position: relative;
        cursor: pointer;
        transition: background 0.2s;

        &::after {
            content: '';
            width: 20px;
            height: 20px;
            background: white;
            border-radius: 50%;
            position: absolute;
            top: 2px;
            left: 2px;
            transition: transform 0.2s;
        }

        &.active {
            background: #2ecc71;
            &::after { transform: translateX(20px); }
        }
    }
  `]
})
export class SettingsComponent {
    auth = inject(AuthService);
    http = inject(HttpClient);
    fb = inject(FormBuilder);

    profileForm = this.fb.group({
        profile_image: ['']
    });

    message = '';

    selectedFile: File | null = null;

    // Instead of FormBuilder for the file, we just handle the change event
    // We keep the form for other future fields if needed, but for now we just use it for the submit trigger

    onFileSelected(event: any) {
        const file = event.target.files[0];
        if (file) {
            this.selectedFile = file;
        }
    }

    updateProfile() {
        const formData = new FormData();

        if (this.selectedFile) {
            formData.append('profile_image', this.selectedFile);
        }

        // We can append other fields as JSON equivalent or individual fields
        // Backend handles param 'preferences'

        this.http.put('http://localhost:5001/users/profile', formData, {
            withCredentials: true
            // Note: Don't set Content-Type header manually, Angular/Browser does it for FormData with boundary
        }).subscribe({
            next: (res: any) => {
                this.message = 'Saved!';
                // Update local auth state immediately
                if (res.user) {
                    this.auth.currentUser.set({
                        ...this.auth.currentUser()!,
                        profile_image: res.user.profile_image
                    });
                }
                this.selectedFile = null; // Reset
                setTimeout(() => this.message = '', 2000);
            },
            error: (err) => {
                this.message = err.error?.error || 'Failed to upload';
            }
        });
    }
}
