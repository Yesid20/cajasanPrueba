import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: `
    <div class="container">
      <h1>Gestión de Órdenes</h1>
      <router-outlet></router-outlet>
    </div>
  `,
  styles: [`
    .container {
      max-width: 900px;
      margin: 30px auto;
      font-family: Arial, sans-serif;
      padding: 15px;
    }

    h1 {
      text-align: center;
      margin-bottom: 25px;
    }
  `]
})
export class AppComponent {}