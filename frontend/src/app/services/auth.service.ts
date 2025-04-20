import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor(
    private httpClient: HttpClient
  ) { }

  getLoginUrl() {
    return environment.baseUrl + '/login';
  }

  handleLoginCallback(code: string, state: string) {
    const request = this.httpClient.get(environment.baseUrl + '/auth', {
      params: { code, state },
      withCredentials: true,
    });
    request.subscribe((res) => {
      console.log('Login callback response:', res);
    })
  }
}
