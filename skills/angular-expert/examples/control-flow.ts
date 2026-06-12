// New control flow: @for REQUIRES track (won't compile without it), @if nests
// inline, and @empty gives a built-in empty state — no structural directives.
import { Component, signal } from '@angular/core';

interface User {
  id: string;
  name: string;
  active: boolean;
}

@Component({
  selector: 'app-user-list',
  template: `
    @for (u of users(); track u.id) {
      @if (u.active) {
        <span>{{ u.name }}</span>
      }
    } @empty {
      <p>No users</p>
    }
  `,
})
export class UserList {
  users = signal<User[]>([]);
}
