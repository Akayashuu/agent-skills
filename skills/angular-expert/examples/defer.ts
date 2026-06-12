// @defer lazy-loads a component's chunk on a trigger (no router needed), with
// @placeholder / @loading / @error blocks. `prefetch on hover` warms it early.
import { Component, signal } from '@angular/core';

@Component({
  selector: 'app-dashboard',
  template: `
    @defer (on viewport; prefetch on hover) {
      <app-heavy-chart [data]="data()" />
    } @placeholder {
      <app-skeleton />
    } @loading (after 100ms) {
      <app-spinner />
    } @error {
      <p>Failed</p>
    }
  `,
})
export class Dashboard {
  data = signal<number[]>([]);
}
