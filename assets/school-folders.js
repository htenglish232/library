// Presentation only: never rewrites catalog entries or Firebase documents.
export function isGameLesson(lesson) {
  return /\bgame\b/iu.test(lesson.title) || /(?:^|[\/_-])game(?:[\/_.-]|$)/iu.test(lesson.href);
}

function schoolIdentity(lesson, schoolNames = {}) {
  const parts = lesson.title.split(' · ');
  let name = schoolNames[lesson.href] || (parts.length > 1 ? parts.at(-1) : lesson.title);
  const recognized = !!schoolNames[lesson.href] || parts.length > 1 || /^(?:THCS|THPT|Tiểu học)\s/iu.test(name);
  name = name.replace(/^(?:Game\s+)?Đề\s+số\s+\d+\s*[–—-]\s*/iu, '').replace(/\s*\(\d+\s*câu\)\s*$/iu, '').replace(/\s*\(\d+\)\s*$/u, '').trim();
  const key = name.normalize('NFC').replace(/^THCS\s+/iu, '').replace(/\s+/gu, ' ').toLocaleLowerCase('vi');
  return {name, key: recognized || /^(?:THCS|THPT|Tiểu học)\s/iu.test(name) ? `school:${key}` : `item:${lesson.href}`};
}

function directory(href) {
  if (/^https:\/\//iu.test(href)) return null;
  try {
    const decoded = decodeURIComponent(href);
    return decoded.slice(0, decoded.lastIndexOf('/') + 1);
  } catch { return null; }
}

export function groupSchoolLessons(lessons, schoolNames = {}) {
  const directories = new Map();
  // Resolve games using their exam's directory, even if the game appears first.
  for (const lesson of lessons) {
    if (!isGameLesson(lesson) && directory(lesson.href)) directories.set(directory(lesson.href), schoolIdentity(lesson, schoolNames));
  }
  const groups = new Map();
  for (const lesson of lessons) {
    const path = directory(lesson.href);
    const examDirectory = path && [...directories.keys()].filter(dir => path.startsWith(dir)).sort((a,b) => b.length-a.length)[0];
    const school = (isGameLesson(lesson) && examDirectory ? directories.get(examDirectory) : null) || schoolIdentity(lesson, schoolNames);
    if (!groups.has(school.key)) groups.set(school.key, {name: school.name, lessons: []});
    groups.get(school.key).lessons.push({...lesson, kind: isGameLesson(lesson) ? 'game' : 'exam'});
  }
  return [...groups.values()];
}

// Display metadata only. Feed the complete unit, including hidden lessons, so a
// filter/search never changes an exam's number. Stored titles/hrefs stay intact.
export function numberSchoolLessons(lessons, {schoolNames = {}, unclassified = false} = {}) {
  const explicit = title => {
    const match = title.match(/^(?:Game\s+)?Đề\s+số\s+([1-9]\d*)\s*[–—-]\s*/iu);
    const number = match && Number(match[1]);
    return Number.isSafeInteger(number) ? number : null;
  };
  let groups = groupSchoolLessons(lessons, schoolNames);
  if (unclassified) {
    const unknown = groups.filter(school => !/^THCS\s/iu.test(school.name));
    groups = groups.filter(school => /^THCS\s/iu.test(school.name));
    if (unknown.length) groups.push({name: 'Đề thi chưa phân loại', unclassified: true,
      lessons: unknown.flatMap(school => school.lessons).sort((a,b) => lessons.findIndex(l=>l.href===a.href)-lessons.findIndex(l=>l.href===b.href))});
  }
  return groups.map(school => {
    const exams = school.lessons.filter(l => l.kind === 'exam');
    const numbers = new Map(), reserved = new Set(exams.map(l => explicit(l.title)).filter(Boolean));
    let next = 1;
    for (const exam of exams) {
      let number = explicit(exam.title);
      if (number && exams.filter(l => explicit(l.title) === number).length > 1) continue;
      if (!number) { while (reserved.has(next)) next++; number = next++; reserved.add(number); }
      numbers.set(exam.href, number);
    }
    const rows = school.lessons.map((lesson, position) => {
      let exam = lesson.kind === 'exam' ? lesson : null;
      if (!exam) {
        const path = directory(lesson.href), requested = explicit(lesson.title);
        let candidates = exams.filter(e => path && directory(e.href) && path.startsWith(directory(e.href)));
        if (candidates.length) {
          const longest = Math.max(...candidates.map(e => directory(e.href).length));
          candidates = candidates.filter(e => directory(e.href).length === longest);
        } else if (requested) candidates = exams;
        if (requested) candidates = candidates.filter(e => numbers.get(e.href) === requested);
        if (candidates.length === 1) exam = candidates[0];
      }
      const examNumber = exam && numbers.get(exam.href);
      const displayTitle = examNumber && (school.name.startsWith('THCS ') || school.unclassified)
        ? `${lesson.kind === 'game' ? 'Game đề' : 'Đề'} số ${examNumber} – ${school.unclassified ? 'Chưa phân loại' : school.name}` : lesson.title;
      return {...lesson, displayTitle, unclassified: !!school.unclassified, examNumber: examNumber || null, examHref: exam?.href || null, position};
    });
    rows.sort((a,b) => (a.examNumber ?? Infinity) - (b.examNumber ?? Infinity)
      || (a.examNumber && b.examNumber ? Number(a.kind === 'game') - Number(b.kind === 'game') : 0) || a.position-b.position);
    return {...school, lessons: rows};
  });
}

export function renderSchoolFolders(lessons, query = '', context = '', groups = groupSchoolLessons(lessons)) {
  const fragment = document.createDocumentFragment();
  const needle = query.toLocaleLowerCase('vi').trim();
  let visibleSchools = 0, unclassifiedCount = 0;
  const visible = new Set(lessons.map(lesson => lesson.href));
  for (const school of groups) {
    const matching = school.lessons.filter(lesson => visible.has(lesson.href) && (!needle || `${context} ${school.name} ${lesson.title} ${lesson.displayTitle || ''} ${lesson.kind==='game'?'Game luyện đề':'Đề kiểm tra'}`.toLocaleLowerCase('vi').includes(needle)));
    if (!matching.length) continue;
    visibleSchools++;
    if (school.unclassified) unclassifiedCount++;
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
    const pairs = new Map();
    for (const lesson of matching) {
      const link = document.createElement('a'); link.className = `lesson school-resource ${lesson.kind}-resource`; link.href = lesson.href;
      if (/^https:\/\//iu.test(lesson.href)) link.rel = 'noopener noreferrer';
      const kind = document.createElement('span'); kind.className = 'resource-kind'; kind.textContent = lesson.kind==='game'?'Game luyện đề':'Đề kiểm tra';
      const name = document.createElement('strong'); name.textContent = lesson.displayTitle || lesson.title;
      link.append(kind, name);
      if (lesson.unclassified) {
        const original = document.createElement('span'); original.className = 'unclassified-title';
        original.textContent = lesson.title; link.append(original);
      }
      let container = resources;
      if (lesson.examNumber) {
        if (!pairs.has(lesson.examNumber)) {
          const pair = document.createElement('div'); pair.className = 'exam-pair';
          pair.dataset.examNumber = lesson.examNumber; pair.setAttribute('role', 'group');
          pair.setAttribute('aria-label', `Đề số ${lesson.examNumber} – ${school.unclassified ? 'Chưa phân loại' : school.name}`);
          pairs.set(lesson.examNumber, pair); resources.append(pair);
        }
        container = pairs.get(lesson.examNumber);
      }
      container.append(link);
    }
    folder.append(resources); fragment.append(folder);
  }
  return {fragment, count: visibleSchools, unclassifiedCount};
}
