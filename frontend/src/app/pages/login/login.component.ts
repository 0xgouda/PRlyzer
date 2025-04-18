import { Component } from '@angular/core';
import { MatCard, MatCardContent, MatCardTitle, MatCardHeader, MatCardActions, MatCardSubtitle } from '@angular/material/card';
import { MatIcon } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { environment } from '../../../environments/environment';


@Component({
  selector: 'app-login',
  standalone: true,
  imports: [MatCard, MatCardTitle, MatCardContent, MatCardHeader, MatCardActions, MatButtonModule, MatIcon, MatCardSubtitle],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  loginUrl = `${environment.baseUrl}/login`;
  
}
