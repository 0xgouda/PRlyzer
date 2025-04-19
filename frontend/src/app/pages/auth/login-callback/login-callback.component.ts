import { Component, OnInit } from '@angular/core';
import { MatCard } from '@angular/material/card';
import { MatProgressSpinner } from '@angular/material/progress-spinner';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-login-callback',
  standalone: true,
  imports: [MatCard, MatProgressSpinner],
  templateUrl: './login-callback.component.html',
  styleUrl: './login-callback.component.scss'
})
export class LoginCallbackComponent implements OnInit {
  constructor (
    private authService: AuthService,
  ) {}

  ngOnInit() {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');

    if (code && state) {
      this.authService.handleLoginCallback(code, state);
    } else {
      console.error('Missing code or state in URL parameters');
    }
  }
}
