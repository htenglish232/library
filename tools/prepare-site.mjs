// Creates a reviewed upload artifact; never publishes or contacts Firebase.
import { execFileSync } from 'node:child_process';
import { mkdirSync, copyFileSync, existsSync } from 'node:fs';
import { dirname } from 'node:path';
execFileSync(process.execPath, ['tools/check-catalog.mjs'], { stdio: 'inherit' });
if (existsSync('.site')) throw new Error('.site already exists; review/remove the previous artifact before rebuilding.');
const files = execFileSync('git', ['ls-files', '-z', '--cached', '--others', '--exclude-standard'], { encoding: 'utf8' }).split('\0').filter(Boolean);
for (const file of files) {
  if (!(/^(grade-[4-8]\/|assets\/)/.test(file) || ['index.html','admin.html','home-button.js'].includes(file))) continue;
  const target = `.site/${file}`; mkdirSync(dirname(target), { recursive: true }); copyFileSync(file, target);
}
console.log('Static artifact prepared in .site. Catalog export, tools and Firebase Rules are excluded. Nothing deployed.');
