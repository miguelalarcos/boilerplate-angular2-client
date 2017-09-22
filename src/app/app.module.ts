import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import {HttpModule} from '@angular/http';
import { AppComponent } from './app.component';
import { StoreDevtoolsModule } from '@ngrx/store-devtools';
import { StoreModule } from '@ngrx/store';
import { user } from './reducers';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule, HttpModule,
    StoreModule.forRoot({ user }),
    StoreDevtoolsModule.instrument({
      maxAge: 25 
    })
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
