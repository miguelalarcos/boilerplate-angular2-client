import { Component } from '@angular/core';
import { UserService } from './user.service';
import { Http, Response, Headers } from '@angular/http';
import { Store } from '@ngrx/store';
import { Observable } from 'rxjs/Observable';
import { AppState, User } from './store';
import * as actions from './actions';
import 'rxjs/Rx';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  providers: [UserService]
})
export class AppComponent {
  title = 'app';
  user: Observable<User>;

  constructor(private gl: UserService, private http: Http, private store: Store<AppState>) { 
    this.user = store.select('user');
    store.select('user').subscribe((x)=>console.log(x));
  }

  signIn(){
    this.gl.googleLogin();
  }

  signOut(){
    this.gl.signOut();
  }

  protected(){
    let token: string;
    this.store.take(1).subscribe((st) => token = st.user.jwt);
    
    const headers = new Headers({ 'Authorization': 'Bearer ' + token});
    //this.http.get('http://localhost:8889/protected', {headers}).map((response: Response) => response.json()).subscribe((x)=>console.log(x));
    this.http.get('/protected', {headers}).map((response: Response) => response.json()).subscribe((x)=>console.log(x));
  }
}
