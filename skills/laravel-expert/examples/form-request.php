<?php

declare(strict_types=1);

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;
use Illuminate\Validation\Validator;

/**
 * Form requests move authorization + validation out of the controller.
 * The controller method type-hints this class; Laravel resolves it, runs
 * authorize() then rules(), and aborts (403/422) before your action runs.
 *
 * In the controller, only ever read $request->validated() — that returns the
 * sanitized subset, closing the mass-assignment hole that $request->all() opens.
 */
final class StorePostRequest extends FormRequest
{
    public function authorize(): bool
    {
        // Returning false yields a 403 before validation runs.
        return $this->user()?->can('create', \App\Models\Post::class) ?? false;
    }

    /** @return array<string, mixed> */
    public function rules(): array
    {
        return [
            'title' => ['required', 'string', 'max:255'],
            'slug' => ['required', 'string', Rule::unique('posts', 'slug')],
            'status' => ['required', Rule::enum(\App\Enums\PostStatus::class)],
            'tags' => ['array'],
            'tags.*' => ['string', 'max:50'],
        ];
    }

    /**
     * Normalize input before validation runs (e.g. derive a slug).
     */
    protected function prepareForValidation(): void
    {
        if (! $this->has('slug') && $this->filled('title')) {
            $this->merge(['slug' => str($this->string('title'))->slug()->value()]);
        }
    }

    /**
     * Cross-field rules that a flat rules() array can't express.
     */
    public function withValidator(Validator $validator): void
    {
        $validator->after(function (Validator $validator): void {
            if ($this->input('status') === 'published' && ! $this->filled('tags')) {
                $validator->errors()->add('tags', 'Published posts need at least one tag.');
            }
        });
    }
}
