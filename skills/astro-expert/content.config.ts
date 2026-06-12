// src/content.config.ts — Astro 5 Content Layer API
// WHY this file lives at src/content.config.ts (NOT src/content/config.ts):
// Astro 5 moved the collections config out of src/content/ so the folder is no
// longer special. Collections now pull data through a `loader` instead of Astro
// implicitly scanning src/content/<name>/. This is the modern, copy-verbatim pattern.

import { defineCollection, reference, z } from 'astro:content';
// glob() (and file()) live in astro/loaders — NOT astro:content. The built-in
// glob loader replaces the old "magic folder" behaviour from Astro 4.
import { glob } from 'astro/loaders';

const blog = defineCollection({
  // loader = where the data comes from. pattern is micromatch; base is the
  // directory it's resolved against. Files can now live anywhere, not just
  // src/content/. The `id` of each entry is derived from its path under base.
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/blog' }),
  // schema validates frontmatter at build time and gives you a fully typed
  // `data` object in getCollection/getEntry. image() yields an optimizable asset.
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      pubDate: z.coerce.date(), // coerce so YAML strings like 2026-01-01 parse
      updatedDate: z.coerce.date().optional(),
      draft: z.boolean().default(false),
      cover: image().optional(),
      tags: z.array(z.string()).default([]),
      // reference() links to another collection; resolve later with getEntry().
      author: reference('authors').optional(),
    }),
});

const authors = defineCollection({
  // One JSON file per author; each entry's id comes from the filename. For a
  // single file holding many entries, swap glob() for file() (also astro/loaders).
  loader: glob({ pattern: '**/*.json', base: './src/content/authors' }),
  schema: z.object({
    name: z.string(),
    url: z.string().url().optional(),
  }),
});

// Every collection used in the app must be exported here.
export const collections = { blog, authors };
