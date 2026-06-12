// src/content.config.ts — glob() loader, image() asset, reference() link.
// Astro 5 Content Layer: config lives at src/content.config.ts (NOT
// src/content/config.ts) and entries have an `id` (the old `slug` is gone).
import { defineCollection, reference, z } from 'astro:content';
// glob()/file() live in astro/loaders — NOT astro:content.
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/blog' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      pubDate: z.coerce.date(), // coerce so YAML strings like 2026-01-01 parse
      draft: z.boolean().default(false),
      cover: image().optional(), // optimizable asset
      tags: z.array(z.string()).default([]),
      author: reference('authors').optional(), // link to another collection
    }),
});

const authors = defineCollection({
  loader: glob({ pattern: '**/*.json', base: './src/content/authors' }),
  schema: z.object({ name: z.string(), url: z.string().url().optional() }),
});

export const collections = { blog, authors };
