// Presentation only: never rewrites catalog entries or Firebase documents.
export function isGameLesson(lesson) {
  return /\bgame\b/iu.test(lesson.title) || /(?:^|[\/_-])game(?:[\/_.-]|$)/iu.test(lesson.href);
}

function schoolIdentity(lesson) {
  const parts = lesson.title.split(' · ');
  let name = parts.length > 1 ? parts.at(-1) : lesson.title;
  const recognized = parts.length > 1 || /^(?:THCS|THPT|Tiểu học)\s/iu.test(name);
  name = name.replace(/\s*\(\d+\s*câu\)\s*$/iu, '').replace(/\s*\(\d+\)\s*$/u, '').trim();
  const key = name.normalize('NFC').replace(/^THCS\s+/iu, '').replace(/\s+/gu, ' ').toLocaleLowerCase('vi');
  return {name, key: recognized ? `school:${key}` : `item:${lesson.href}`};
}

function directory(href) {
  if (/^https:\/\//iu.test(href)) return null;
  try {
    const decoded = decodeURIComponent(href);
    return decoded.slice(0, decoded.lastIndexOf('/') + 1);
  } catch { return null; }
}

export function groupSchoolLessons(lessons) {
  const directories = new Map();
  // Resolve games using their exam's directory, even if the game appears first.
  for (const lesson of lessons) {
    if (!isGameLesson(lesson) && directory(lesson.href)) directories.set(directory(lesson.href), schoolIdentity(lesson));
  }
  const groups = new Map();
  for (const lesson of lessons) {
    const path = directory(lesson.href);
    const examDirectory = path && [...directories.keys()].filter(dir => path.startsWith(dir)).sort((a,b) => b.length-a.length)[0];
    const school = (isGameLesson(lesson) && examDirectory ? directories.get(examDirectory) : null) || schoolIdentity(lesson);
    if (!groups.has(school.key)) groups.set(school.key, {name: school.name, lessons: []});
    groups.get(school.key).lessons.push({...lesson, kind: isGameLesson(lesson) ? 'game' : 'exam'});
  }
  return [...groups.values()];
}

export function renderSchoolFolders(lessons, query = '', context = '') {
  const fragment = document.createDocumentFragment();
  const needle = query.toLocaleLowerCase('vi').trim();
  let visibleSchools = 0;
  for (const school of groupSchoolLessons(lessons)) {
    const matching = school.lessons.filter(lesson => !needle || `${context} ${school.name} ${lesson.title} ${lesson.kind==='game'?'Game luyện đề':'Đề kiểm tra'}`.toLocaleLowerCase('vi').includes(needle));
    if (!matching.length) continue;
    visibleSchools++;
    const folder = document.createElement('details');
    folder.className = 'school-folder'; folder.open = !!needle;
    const summary = document.createElement('summary'); summary.className = 'school-summary';
    const title = document.createElement('span'); title.className = 'school-name'; title.textContent = school.name;
    const count = document.createElement('span'); count.className = 'school-count';
    const exams = matching.filter(lesson => lesson.kind==='exam').length;
    const games = matching.length-exams;
    count.textContent = [exams && `${exams} đề`, games && `${games} game`].filter(Boolean).join(' · ');
    summary.append(title, count); folder.append(summary);
    const resources = document.createElement('div'); resources.className = 'school-resources';
    for (const lesson of matching) {
      const link = document.createElement('a'); link.className = `lesson school-resource ${lesson.kind}-resource`; link.href = lesson.href;
      if (/^https:\/\//iu.test(lesson.href)) link.rel = 'noopener noreferrer';
      const kind = document.createElement('span'); kind.className = 'resource-kind'; kind.textContent = lesson.kind==='game'?'Game luyện đề':'Đề kiểm tra';
      const name = document.createElement('strong'); name.textContent = lesson.title;
      link.append(kind, name); resources.append(link);
    }
    folder.append(resources); fragment.append(folder);
  }
  return {fragment, count: visibleSchools};
}
