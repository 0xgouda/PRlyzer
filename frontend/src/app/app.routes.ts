import { Routes } from '@angular/router';
import { LoginComponent } from './pages/auth/login/login.component';
import { LoginCallbackComponent } from './pages/auth/login-callback/login-callback.component';

export const routes: Routes = [
    { path: '', component: LoginComponent, pathMatch: 'full' },
    { path: 'login', component: LoginComponent, pathMatch: 'full' },
    { path: 'login/callback', component: LoginCallbackComponent, pathMatch: 'full' }
];
