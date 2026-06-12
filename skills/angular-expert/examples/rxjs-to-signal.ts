// RxJS for async, signals for state. Flatten with switchMap (no subscribe-in-
// subscribe), tie teardown to the component with takeUntilDestroyed(), and expose
// the result as a signal via toSignal().
import { Component, inject } from '@angular/core';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { switchMap } from 'rxjs';

interface User {
  id: string;
  name: string;
}

@Component({
  selector: 'app-user',
  template: `{{ user()?.name }}`,
})
export class UserComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly http = inject(HttpClient);

  user = toSignal(
    this.route.params.pipe(
      switchMap((p) => this.http.get<User>(`/u/${p['id']}`)),
      takeUntilDestroyed(),
    ),
  );
}
