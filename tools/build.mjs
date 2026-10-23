import { build } from 'esbuild';
import { readFile, writeFile } from 'node:fs/promises';
await build({ entryPoints: ['tools/sdk-entry.js'], bundle: true, format: 'esm',
  target: ['es2022'], supported: { 'template-literal': false }, minify: true,
  outfile: 'assets/firebase-sdk.js', legalComments: 'linked' });
const licensePath = 'assets/firebase-sdk.js.LEGAL.txt';
const license = await readFile(licensePath, 'utf8');
await writeFile(licensePath, license.split('\n').map(line => line.trimEnd()).join('\n'));
console.log('Firebase SDK bundle built locally; no CDN dependency.');
