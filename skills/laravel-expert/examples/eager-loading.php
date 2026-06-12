<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Casts\Attribute;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

/**
 * Eloquent done right: explicit mass-assignment, native casts, and query
 * scopes — plus eager loading to kill N+1 (see usage at the bottom).
 */
final class Post extends Model
{
    // Prefer an explicit $fillable allow-list over $guarded = []. An empty
    // guard is a mass-assignment hole: any column becomes settable from input.
    /** @var list<string> */
    protected $fillable = ['title', 'slug', 'status', 'published_at'];

    /**
     * Casts as a method (Laravel 11+). Enum + datetime casting happens at the
     * model boundary so the rest of the app works with real types.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'status' => \App\Enums\PostStatus::class,
            'published_at' => 'immutable_datetime',
            'meta' => 'array',
        ];
    }

    public function author(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
    }

    /**
     * Query scope: ->published() reads better than repeating the where clause,
     * and keeps the "what does published mean" rule in one place.
     */
    public function scopePublished(Builder $query): Builder
    {
        return $query->where('status', 'published')
            ->where('published_at', '<=', now());
    }

    /**
     * Accessor via the Attribute API (Laravel 9+).
     */
    protected function excerpt(): Attribute
    {
        return Attribute::make(
            get: fn (mixed $value, array $attributes): string => str($attributes['body'] ?? '')
                ->limit(120)
                ->value(),
        );
    }
}

/**
 * N+1 vs eager loading. The loop below issues 1 + N queries: one for the posts,
 * then one per post to fetch its author lazily.
 *
 *   foreach (Post::published()->get() as $post) {
 *       echo $post->author->name;            // lazy: a query per iteration
 *   }
 *
 * Eager load the relations you'll touch — one extra query total, not N:
 *
 *   $posts = Post::published()
 *       ->with(['author', 'comments' => fn ($q) => $q->latest()->limit(3)])
 *       ->withCount('comments')
 *       ->get();
 *
 * In dev, call Model::preventLazyLoading() in a service provider's boot() so an
 * un-eager-loaded access throws instead of silently degrading to N+1.
 */
