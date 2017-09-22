export class User{
    jwt: string;
    constructor(jwt: string){
        this.jwt = jwt;
    }
}

export interface AppState {
    user: User;
  }