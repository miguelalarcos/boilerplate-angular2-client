import { Http, Response } from '@angular/http';
import { Store } from '@ngrx/store';
import { Injectable } from '@angular/core';
import { AppState, User } from './store';
import * as actions from './actions';

declare const gapi: any;

@Injectable()
export class UserService {

  constructor(private http: Http, private store: Store<AppState>) { 
    gapi.load('auth2', function () {
      gapi.auth2.init();
    });
  }

  googleLogin() {
    const googleAuth = gapi.auth2.getAuthInstance();
    googleAuth.then(() => {
      googleAuth.signIn({scope: 'profile email'}).then(googleUser => {
        //cb(googleUser.getAuthResponse().access_token);
        let token = googleUser.getAuthResponse().access_token;
        //this.http.get('http://localhost:8889/login?token=' + token)
        this.http.get('/login/' + token)
        .map((res: Response) => {
              let body = res.json();
              return body || {};
        }).subscribe((data) => {
              this.store.dispatch(new actions.Login(data.jwt));
              console.log(data);
        });
      });
    });
  }

  signOut() {
    gapi.auth2.getAuthInstance().disconnect();
    this.store.dispatch(new actions.Logout());
  }

}
